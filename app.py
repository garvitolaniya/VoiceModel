from flask import Flask, render_template, request, jsonify, send_file
import os
from scripts.record import VoiceRecorder, get_dynamic_duration
import threading
import queue
import time
import random
import sounddevice as sd
import wave

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables for recording state
recording_thread = None
recording_queue = queue.Queue()
is_recording = False
recorder = VoiceRecorder()

# Load words from word sources
words = []
word_sources_folder = "word_sources"
os.makedirs(word_sources_folder, exist_ok=True)

# Create a sample words file if it doesn't exist
sample_words_file = os.path.join(word_sources_folder, "sample_words.txt")
if not os.path.exists(sample_words_file):
    with open(sample_words_file, "w", encoding="utf-8") as f:
        f.write("""hello
world
python
programming
voice
recording
microphone
audio
speech
recognition""")

# Load words from files
for filename in os.listdir(word_sources_folder):
    if filename.endswith(".txt"):
        filepath = os.path.join(word_sources_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            words.extend([line.strip() for line in f if line.strip()])

random.shuffle(words)

# Desi-style prompts and appreciations
prompts = [
    "🎙️ Press Enter to record this masterpiece!",
    "🎙️ Ready? Hit Enter and let's capture your voice!",
    "📢 Awaaz uthao! Yeh shabd tumhara intezaar kar raha hai...",
    "🎤 Bas bol do, camera rolling hai!",
    "🗣️ Ab bolo is shabd ko, warna yeh naraz ho jayega!",
    "🎬 Dialog delivery ka waqt aa gaya!",
    "🔊 Shabd ki duniya mein swagat hai!",
    "🎙️ Bolo beta, sharmao mat...",
]

appreciations = [
    "🎉 Wah beta wah! Tum toh asli superstar nikle!",
    "🔥 Awaaz mein kya dum hai, laga do sabko chakkar!",
    "🕺 Ekdum filmy andaaz! Agla stop: Bollywood!",
    "😂 Abey yaar, kya zabardast bola hai!",
    "💯 Perfect pronunciation! Desh ki shaan ban gaye ho!",
    "🎯 Tumhare jaise data donors kam milte hain bhai!",
    "🌟 Practice makes perfect! Mazaa aa gaya!",
    "🚀 Ab toh AI bhi confused ho gaya, itni badiya recording!",
    "📈 Har baar better ho rahe ho, solid growth!",
]

# Global variables for word tracking
current_word_index = 0
recording_count = 0
next_appreciation_at = random.randint(5, 8)
total_recordings = 0

def create_word_folder(word):
    """Create a folder for the word if it doesn't exist"""
    word_folder = os.path.join("data/recordings", word)
    os.makedirs(word_folder, exist_ok=True)
    return word_folder

def get_next_recording_index(word):
    """Get the next recording index for a word"""
    word_folder = os.path.join("data/recordings", word)
    if not os.path.exists(word_folder):
        return 1
    
    existing_files = [f for f in os.listdir(word_folder) if f.endswith(".wav") and f[:-4].isdigit()]
    existing_indices = [int(f[:-4]) for f in existing_files]
    return max(existing_indices, default=0) + 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_current_word', methods=['GET'])
def get_current_word():
    global current_word_index
    if current_word_index >= len(words):
        current_word_index = 0
        random.shuffle(words)
    
    current_word = words[current_word_index]
    prompt = random.choice(prompts)
    duration = get_dynamic_duration(current_word)
    
    # Create folder for the word
    create_word_folder(current_word)
    
    return jsonify({
        'status': 'success',
        'word': current_word,
        'prompt': prompt,
        'duration': duration,
        'progress': (current_word_index / len(words)) * 100,
        'recordings_count': get_next_recording_index(current_word) - 1
    })

@app.route('/api/start_recording', methods=['POST'])
def start_recording():
    global recording_thread, is_recording, current_word_index
    
    if is_recording:
        return jsonify({'status': 'error', 'message': 'Already recording'})
    
    try:
        current_word = words[current_word_index]
        duration = get_dynamic_duration(current_word)
        is_recording = True
        recording_thread = threading.Thread(target=record_audio)
        recording_thread.start()
        
        return jsonify({
            'status': 'success', 
            'message': 'Recording started',
            'duration': duration
        })
    except Exception as e:
        is_recording = False
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/stop_recording', methods=['POST'])
def stop_recording():
    global is_recording
    
    if not is_recording:
        return jsonify({'status': 'error', 'message': 'Not recording'})
    
    try:
        is_recording = False
        if recording_thread:
            recording_thread.join()
            
            # Get the result from the queue
            if not recording_queue.empty():
                result = recording_queue.get()
                return jsonify(result)
        
        return jsonify({'status': 'error', 'message': 'No recording found'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/skip_word', methods=['POST'])
def skip_word():
    global current_word_index
    current_word_index += 1
    if current_word_index >= len(words):
        current_word_index = 0
        random.shuffle(words)
    
    current_word = words[current_word_index]
    duration = get_dynamic_duration(current_word)
    prompt = random.choice(prompts)
    
    return jsonify({
        'status': 'success',
        'message': 'Word skipped',
        'word': current_word,
        'duration': duration,
        'prompt': prompt,
        'progress': (current_word_index / len(words)) * 100
    })

@app.route('/api/get_recording_status', methods=['GET'])
def get_recording_status():
    return jsonify({
        'status': 'success',
        'is_recording': is_recording,
        'total_recordings': total_recordings
    })

def record_audio():
    global current_word_index, recording_count, total_recordings, next_appreciation_at, is_recording
    
    try:
        current_word = words[current_word_index]
        duration = get_dynamic_duration(current_word)
        print(f"Recording word '{current_word}' for {duration} seconds...")
        
        # Create word-specific folder
        word_folder = create_word_folder(current_word)
        next_index = get_next_recording_index(current_word)
        
        # Record audio with exact duration
        audio = sd.rec(
            int(duration * recorder.sample_rate),
            samplerate=recorder.sample_rate,
            channels=1,
            dtype='int16'
        )
        
        # Wait for exact duration
        sd.wait()
        
        # Save the recording
        filename = os.path.join(word_folder, f"{next_index}.wav")
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(recorder.sample_rate)
            wf.writeframes(audio.tobytes())

        print(f"Recording saved to {filename}")
        
        # Move to next word immediately
        current_word_index += 1
        recording_count += 1
        total_recordings += 1
        
        # Reset word index if we've gone through all words
        if current_word_index >= len(words):
            current_word_index = 0
            random.shuffle(words)
        
        # Get next word info
        next_word = words[current_word_index]
        next_duration = get_dynamic_duration(next_word)
        next_prompt = random.choice(prompts)
        
        # Check if it's time for appreciation
        appreciation = None
        if recording_count >= next_appreciation_at:
            appreciation = random.choice(appreciations)
            recording_count = 0
            next_appreciation_at = random.randint(5, 8)
        
        # Put the result in the queue
        result = {
            'status': 'success',
            'message': 'Recording completed',
            'file': filename,
            'appreciation': appreciation,
            'total_recordings': total_recordings,
            'next_word': next_word,
            'next_duration': next_duration,
            'next_prompt': next_prompt,
            'progress': (current_word_index / len(words)) * 100,
            'recordings_count': get_next_recording_index(next_word) - 1
        }
        recording_queue.put(result)
        is_recording = False
        
    except Exception as e:
        print(f"Recording error: {str(e)}")
        is_recording = False
        recording_queue.put({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000) 