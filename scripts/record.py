import os
import time
import wave
import random
import sounddevice as sd
import tkinter as tk
from tkinter import ttk, messagebox
import threading

# Constants
COLORS = {
    'primary': '#6C3EFF',
    'secondary': '#FFD700',
    'accent': '#23232B',
    'background': '#0A0A0F',
    'surface': '#1A1A1A',
    'glass': '#2A2A2A',
    'text': '#FFFFFF',
    'text_light': '#B8B8B8',
    'success': '#00FF9D',
    'error': '#FF3366',
    'warning': '#FFD700'
}

# Global variables
sample_rate = 44100
recordings_root = "data/recordings"
os.makedirs(recordings_root, exist_ok=True)

# Load words
words = []
word_sources_folder = "word_sources"
os.makedirs(word_sources_folder, exist_ok=True)

# Create sample words file if it doesn't exist
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

# Prompts and appreciations
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

def get_dynamic_duration(word):
    """Calculate recording duration based on word length"""
    base_duration = 2.0
    length_factor = len(word) * 0.2
    return min(max(base_duration + length_factor, 2.0), 5.0)

class VoiceRecorder:
    def __init__(self):
        self.sample_rate = sample_rate
        self.recordings_root = recordings_root
        self.current_word_index = 0
        self.is_recording = False
        self.recording_start_time = 0
        self.recording_duration = 0
        self.recording_count = 0
        self.total_recordings = 0
        self.next_appreciation_at = random.randint(5, 8)
        self.last_recorded_filename = None

    def get_current_word(self):
        if self.current_word_index >= len(words):
            self.current_word_index = 0
            random.shuffle(words)

        current_word = words[self.current_word_index]
        prompt = random.choice(prompts)
        duration = get_dynamic_duration(current_word)

        # Create folder for the word
        word_folder = os.path.join(self.recordings_root, current_word)
        os.makedirs(word_folder, exist_ok=True)

        return {
            'word': current_word,
            'prompt': prompt,
            'duration': duration,
            'progress': (self.current_word_index / len(words)) * 100,
            'recordings_count': self.get_next_recording_index(current_word) - 1
        }

    def get_next_recording_index(self, word):
        """Get the next recording index for a word"""
        word_folder = os.path.join(self.recordings_root, word)
        if not os.path.exists(word_folder):
            return 1
        
        existing_files = [f for f in os.listdir(word_folder) if f.endswith(".wav") and f[:-4].isdigit()]
        existing_indices = [int(f[:-4]) for f in existing_files]
        return max(existing_indices, default=0) + 1

    def start_recording(self):
        if self.is_recording:
            return {'status': 'error', 'message': 'Already recording'}
        
        try:
            current_word = words[self.current_word_index]
            duration = get_dynamic_duration(current_word)
            self.is_recording = True
            self.recording_start_time = time.time()
            self.recording_duration = duration
            
            return {
                'status': 'success',
                'message': 'Recording started',
                'duration': duration
            }
        except Exception as e:
            self.is_recording = False
            return {'status': 'error', 'message': str(e)}

    def stop_recording(self):
        if not self.is_recording:
            return {'status': 'error', 'message': 'Not recording'}
        
        try:
            self.is_recording = False
            current_word = words[self.current_word_index]
            word_folder = os.path.join(self.recordings_root, current_word)
            os.makedirs(word_folder, exist_ok=True)
            next_index = self.get_next_recording_index(current_word)
            
            # Record audio with exact duration
            audio = sd.rec(
                int(self.recording_duration * self.sample_rate),
                samplerate=self.sample_rate,
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
                wf.setframerate(self.sample_rate)
            wf.writeframes(audio.tobytes())

            self.last_recorded_filename = filename
            self.recording_count += 1
            self.total_recordings += 1
            
            # Move to next word
            self.current_word_index += 1
            if self.current_word_index >= len(words):
                self.current_word_index = 0
                random.shuffle(words)
            
            # Get next word info
            next_word = words[self.current_word_index]
            next_duration = get_dynamic_duration(next_word)
            next_prompt = random.choice(prompts)
            
            # Check if it's time for appreciation
            appreciation = None
            if self.recording_count >= self.next_appreciation_at:
                appreciation = random.choice(appreciations)
                self.recording_count = 0
                self.next_appreciation_at = random.randint(5, 8)

            return {
                'status': 'success',
                'message': 'Recording completed',
                'file': filename,
                'appreciation': appreciation,
                'total_recordings': self.total_recordings,
                'next_word': next_word,
                'next_duration': next_duration,
                'next_prompt': next_prompt,
                'progress': (self.current_word_index / len(words)) * 100,
                'recordings_count': self.get_next_recording_index(next_word) - 1
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def skip_word(self):
        self.current_word_index += 1
        if self.current_word_index >= len(words):
            self.current_word_index = 0
random.shuffle(words)

        current_word = words[self.current_word_index]
        duration = get_dynamic_duration(current_word)
        prompt = random.choice(prompts)
        
        return {
            'status': 'success',
            'message': 'Word skipped',
            'word': current_word,
            'duration': duration,
            'prompt': prompt,
            'progress': (self.current_word_index / len(words)) * 100
        }

class VoiceRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Recorder Pro")
        self.root.geometry("800x600")
        self.root.configure(bg=COLORS['background'])

        self.current_word_index = 0
        self.is_recording = False
        self.recording_start_time = 0
        self.recording_duration = 0
        self.recording_count = 0
        self.total_recordings = 0
        self.next_appreciation_at = random.randint(5, 8)
        self.last_recorded_filename = None
        
        self.setup_ui()
        self.refresh_word()
        
        # Bind space key to record
        self.root.bind('<space>', lambda e: self.record_audio())
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg=COLORS['background'])
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Word display
        self.word_canvas = tk.Canvas(main_frame, bg=COLORS['surface'], height=100)
        self.word_canvas.pack(fill='x', pady=(0, 20))
        self.word_label = self.word_canvas.create_text(
            400, 50, text="", font=('Arial', 24), fill=COLORS['text']
        )
        
        # Prompt label
        self.prompt_label = tk.Label(
            main_frame, text="", font=('Arial', 12),
            bg=COLORS['background'], fg=COLORS['text_light']
        )
        self.prompt_label.pack(pady=(0, 20))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame, length=600, mode='determinate'
        )
        self.progress.pack(pady=(0, 20))
        
        # Status label
        self.status_label = tk.Label(
            main_frame, text="", font=('Arial', 12),
            bg=COLORS['background'], fg=COLORS['text_light']
        )
        self.status_label.pack(pady=(0, 20))

        # Stats label
        self.stats_label = tk.Label(
            main_frame, text="Recordings: 0", font=('Arial', 12),
            bg=COLORS['background'], fg=COLORS['text_light']
        )
        self.stats_label.pack(pady=(0, 20))

        # Appreciation label
        self.appreciation_label = tk.Label(
            main_frame, text="", font=('Arial', 12),
            bg=COLORS['background'], fg=COLORS['success']
        )
        self.appreciation_label.pack(pady=(0, 20))
        
        # Recording canvas
        self.recording_canvas = tk.Canvas(
            main_frame, bg=COLORS['surface'], height=50
        )
        
        # Buttons frame
        button_frame = tk.Frame(main_frame, bg=COLORS['background'])
        button_frame.pack(pady=(0, 20))
        
        # Record button
        self.record_button = tk.Button(
            button_frame, text="🎙️ Record (Space)",
            command=self.record_audio,
            bg=COLORS['primary'], fg=COLORS['text'],
            font=('Arial', 12), padx=20, pady=10
        )
        self.record_button.pack(side='left', padx=10)
        
        # Skip button
        self.skip_button = tk.Button(
            button_frame, text="⏩ Skip",
            command=self.skip_word,
            bg=COLORS['warning'], fg=COLORS['accent'],
            font=('Arial', 12), padx=20, pady=10
        )
        self.skip_button.pack(side='left', padx=10)
        
        # Retry button
        self.retry_button = tk.Button(
            button_frame, text="🔄 Retry",
            command=self.retry_recording,
            bg=COLORS['accent'], fg=COLORS['text'],
            font=('Arial', 12), padx=20, pady=10
        )
        self.retry_button.pack(side='left', padx=10)

    def refresh_word(self):
        if self.current_word_index >= len(words):
            self.current_word_index = 0
            random.shuffle(words)
        
        current_word = words[self.current_word_index]
        self.word_canvas.itemconfig(self.word_label, text=f"🔤 {current_word}")
        self.prompt_label.config(text=random.choice(prompts))
        self.appreciation_label.config(text="")
        self.progress["value"] = (self.current_word_index / len(words)) * 100
        
        self.recording_duration = get_dynamic_duration(current_word)
        self.status_label.config(text="Ready to record (Press Space)", fg=COLORS['text_light'])

    def record_audio(self):
        if self.is_recording:
            return
        
        self.is_recording = True
        self.recording_start_time = time.time()
        self.record_button.config(state="disabled")
        self.retry_button.config(state="disabled")
        self.skip_button.config(state="disabled")
        
        self.recording_canvas.pack()
        self.status_label.config(text="⏺️ Recording... 0s", fg=COLORS['error'])
        
        threading.Thread(target=self._record_audio_thread).start()

    def _record_audio_thread(self):
        word = words[self.current_word_index]
        word_folder = os.path.join(recordings_root, word)
        os.makedirs(word_folder, exist_ok=True)

        existing_files = [f for f in os.listdir(word_folder) if f.endswith(".wav") and f[:-4].isdigit()]
        existing_indices = [int(f[:-4]) for f in existing_files]
        next_index = max(existing_indices, default=0) + 1

        audio = sd.rec(int(self.recording_duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()

        filename = os.path.join(word_folder, f"{next_index}.wav")
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio.tobytes())

        self.last_recorded_filename = filename
        self.recording_count += 1
        self.total_recordings += 1
        self.stats_label.config(text=f"Recordings: {self.total_recordings}")

        self.root.after(0, self._finish_recording)

    def _finish_recording(self):
        self.is_recording = False
        self.recording_canvas.pack_forget()
        self.record_button.config(state="normal")
        self.retry_button.config(state="normal")
        self.skip_button.config(state="normal")

        self.status_label.config(text=f"✅ Saved: {os.path.basename(self.last_recorded_filename)}", fg=COLORS['success'])

        if self.recording_count >= self.next_appreciation_at:
            appreciation_message = random.choice(appreciations)
            messagebox.showinfo("👏 Appreciation", appreciation_message)
            self.appreciation_label.config(text=appreciation_message)
            self.recording_count = 0
            self.next_appreciation_at = random.randint(5, 8)

        self.current_word_index += 1
        self.refresh_word()

    def skip_word(self):
        if not self.is_recording:
            self.status_label.config(text="⏩ Word Skipped!", fg=COLORS['primary'])
            self.current_word_index += 1
        self.refresh_word()

    def retry_recording(self):
        if not self.is_recording and self.last_recorded_filename:
            try:
                os.remove(self.last_recorded_filename)
                self.status_label.config(text="⏺️ Retrying recording...", fg=COLORS['error'])
                self.record_audio()
            except Exception as e:
                self.status_label.config(text=f"❌ Error: {str(e)}", fg=COLORS['error'])
        elif not self.last_recorded_filename:
            self.status_label.config(text="❌ No recording to retry.", fg=COLORS['error'])

if __name__ == "__main__":
root = tk.Tk()
app = VoiceRecorderApp(root)
root.mainloop()