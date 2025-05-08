from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
import os
from scripts.record import VoiceRecorder, get_dynamic_duration
import threading
import queue
import time
import random
import sounddevice as sd
import wave
import json
from datetime import datetime
import shutil
import uuid
import subprocess
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data/recordings', exist_ok=True)
os.makedirs('word_sources', exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create VoiceRecorder instance
recorder = VoiceRecorder()

# Load words from word sources
words = []
word_sources_folder = "word_sources"

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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/voice-model')
def voice_model():
    return render_template('index.html')

@app.route('/api/get_current_word', methods=['GET'])
def get_current_word():
    result = recorder.get_current_word()
    return jsonify({
        'status': 'success',
        **result
    })

@app.route('/api/start_recording', methods=['POST'])
def start_recording():
    result = recorder.start_recording()
    return jsonify(result)

@app.route('/api/stop_recording', methods=['POST'])
def stop_recording():
    try:
        if 'audio' not in request.files:
            return jsonify({'status': 'error', 'message': 'No audio file received'})
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'status': 'error', 'message': 'No selected file'})
        
        # Get current word and create folder
        current_word = recorder.get_current_word()['word']
        word_folder = os.path.join(recorder.recordings_root, current_word)
        os.makedirs(word_folder, exist_ok=True)
        
        # Save the audio file
        next_index = recorder.get_next_recording_index(current_word)
        filename = os.path.join(word_folder, f"{next_index}.wav")
        audio_file.save(filename)
        
        # Update recorder state
        recorder.last_recorded_filename = filename
        recorder.recording_count += 1
        recorder.total_recordings += 1
        
        # Move to next word
        recorder.current_word_index += 1
        if recorder.current_word_index >= len(words):
            recorder.current_word_index = 0
            random.shuffle(words)
        
        # Get next word info
        next_word = words[recorder.current_word_index]
        next_duration = get_dynamic_duration(next_word)
        next_prompt = random.choice(prompts)
        
        # Check if it's time for appreciation
        appreciation = None
        if recorder.recording_count >= recorder.next_appreciation_at:
            appreciation = random.choice(appreciations)
            recorder.recording_count = 0
            recorder.next_appreciation_at = random.randint(5, 8)
        
        return jsonify({
            'status': 'success',
            'message': 'Recording completed',
            'file': filename,
            'appreciation': appreciation,
            'total_recordings': recorder.total_recordings,
            'next_word': next_word,
            'next_duration': next_duration,
            'next_prompt': next_prompt,
            'progress': (recorder.current_word_index / len(words)) * 100,
            'recordings_count': recorder.get_next_recording_index(next_word) - 1
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/skip_word', methods=['POST'])
def skip_word():
    result = recorder.skip_word()
    return jsonify(result)

@app.route('/api/get_recording_status', methods=['GET'])
def get_recording_status():
    return jsonify({
        'status': 'success',
        'is_recording': recorder.is_recording,
        'total_recordings': recorder.total_recordings
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000) 