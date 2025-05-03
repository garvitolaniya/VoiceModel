"""import sounddevice as sd
import numpy as np
import wave
import os

duration = 6  # seconds
sample_rate = 16000  # Whisper default

recordings_path = "../F.voice model/data/recordings"
wordlist_path = "wordlist.txt"

os.makedirs(recordings_path, exist_ok=True)

with open(wordlist_path, "r") as f:
    words = [line.strip() for line in f.readlines() if line.strip()]

for word in words:
    input(f"\n🎙️ Press Enter to record: '{word}'")
    print("Recording...")

    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    
    filename = f"{recordings_path}/{word}.wav"
    print("Saving to:", filename)

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    print(f"✅ Saved: {filename}")"""




"""import sounddevice as sd
import numpy as np
import wave
import os

# Recording settings
duration = 2 # seconds
sample_rate = 16000  # Whisper default

# Paths
recordings_root = "../F.voice model/data/recordings"  # change if needed
wordlist_path = "wordlist.txt"

# Make sure the recordings folder exists
os.makedirs(recordings_root, exist_ok=True)

# Read all words from wordlist.txt
with open(wordlist_path, "r") as f:
    words = [line.strip() for line in f if line.strip()]

# For each word, create a folder and save recordings inside it
for word in words:
    word_folder = os.path.join(recordings_root, word)
    os.makedirs(word_folder, exist_ok=True)

    # Find how many .wav files already exist
    existing_files = [f for f in os.listdir(word_folder) if f.endswith(".wav")]
    next_index = len(existing_files) + 1

    input(f"\n🎙️ Press Enter to record: '{word}'")
    print("Recording...")

    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()

    filename = os.path.join(word_folder, f"{next_index}.wav")

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit = 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    print(f"✅ Saved: {filename}")
"""







"""import tkinter as tk
from tkinter import messagebox, ttk
import sounddevice as sd
import numpy as np
import wave
import os
import random

# Settings
duration = 2  # seconds
sample_rate = 16000
recordings_root = "../F.voice model/data/recordings"
wordlist_path = "wordlist.txt"

# Desi-style prompts and appreciations
prompts = [
    "🎙️ Press Enter to record this masterpiece!",
    "🎙️ Ready? Hit Enter and let’s capture your voice!",
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

# Folder setup
os.makedirs(recordings_root, exist_ok=True)

# Load words
with open(wordlist_path, "r", encoding="utf-8") as f:
    words = [line.strip() for line in f if line.strip()]

recording_count = 0
next_appreciation_at = random.randint(5, 8)
current_word_index = 0

# GUI App
class VoiceRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Desi Voice Recorder")
        self.create_widgets()

    def create_widgets(self):
        self.word_label = tk.Label(self.root, text="", font=("Arial", 24, "bold"), fg="darkblue")
        self.word_label.pack(pady=20)

        self.prompt_label = tk.Label(self.root, text=random.choice(prompts), font=("Arial", 14))
        self.prompt_label.pack(pady=10)

        self.record_button = tk.Button(self.root, text="🎙️ Record Now", command=self.record_audio, font=("Arial", 16), bg="green", fg="white")
        self.record_button.pack(pady=10)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.refresh_word()

    def refresh_word(self):
        global current_word_index
        if current_word_index >= len(words):
            current_word_index = 0
            random.shuffle(words)
        self.word_label.config(text=f"🔤 {words[current_word_index]}")
        self.prompt_label.config(text=random.choice(prompts))
        self.progress["value"] = (current_word_index / len(words)) * 100

    def record_audio(self):
        global current_word_index, recording_count, next_appreciation_at

        word = words[current_word_index]
        word_folder = os.path.join(recordings_root, word)
        os.makedirs(word_folder, exist_ok=True)

        existing_files = [f for f in os.listdir(word_folder) if f.endswith(".wav") and f[:-4].isdigit()]
        existing_indices = [int(f[:-4]) for f in existing_files]
        next_index = max(existing_indices, default=0) + 1

        self.status_label.config(text="⏺️ Recording...", fg="red")
        self.root.update()
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()

        filename = os.path.join(word_folder, f"{next_index}.wav")
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio.tobytes())

        self.status_label.config(text=f"✅ Saved: {filename}", fg="green")
        recording_count += 1

        if recording_count >= next_appreciation_at:
            messagebox.showinfo("👏 Appreciation", random.choice(appreciations))
            recording_count = 0
            next_appreciation_at = random.randint(5, 8)

        current_word_index += 1
        self.refresh_word()

# Start App
root = tk.Tk()
app = VoiceRecorderApp(root)
root.mainloop()
"""











"""

import tkinter as tk
from tkinter import messagebox, ttk
import sounddevice as sd
import numpy as np
import wave
import os
import random

# Settings
duration = 2  # seconds
sample_rate = 16000
recordings_root = "../F.voice model/data/recordings"
wordlist_path = "wordlist.txt"

# Desi-style prompts and appreciations
prompts = [
    "🎙️ Press Enter to record this masterpiece!",
    "🎙️ Ready? Hit Enter and let’s capture your voice!",
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

# Folder setup
os.makedirs(recordings_root, exist_ok=True)

# Load words
with open(wordlist_path, "r", encoding="utf-8") as f:
    words = [line.strip() for line in f if line.strip()]

recording_count = 0
next_appreciation_at = random.randint(5, 8)
current_word_index = 0

# GUI App
class VoiceRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Desi Voice Recorder")
        self.create_widgets()

    def create_widgets(self):
        self.word_label = tk.Label(self.root, text="", font=("Arial", 24, "bold"), fg="darkblue")
        self.word_label.pack(pady=20)

        self.prompt_label = tk.Label(self.root, text=random.choice(prompts), font=("Arial", 14))
        self.prompt_label.pack(pady=10)

        self.record_button = tk.Button(self.root, text="🎙️ Record Now", command=self.record_audio, font=("Arial", 16), bg="green", fg="white")
        self.record_button.pack(pady=10)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.appreciation_label = tk.Label(self.root, text="", font=("Arial", 12, "italic"), fg="purple")
        self.appreciation_label.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.refresh_word()

    def refresh_word(self):
        global current_word_index
        if current_word_index >= len(words):
            current_word_index = 0
            random.shuffle(words)
        self.word_label.config(text=f"🔤 {words[current_word_index]}")
        self.prompt_label.config(text=random.choice(prompts))
        self.appreciation_label.config(text="")  # Clear appreciation text
        self.progress["value"] = (current_word_index / len(words)) * 100

    def record_audio(self):
        global current_word_index, recording_count, next_appreciation_at

        word = words[current_word_index]
        word_folder = os.path.join(recordings_root, word)
        os.makedirs(word_folder, exist_ok=True)

        existing_files = [f for f in os.listdir(word_folder) if f.endswith(".wav") and f[:-4].isdigit()]
        existing_indices = [int(f[:-4]) for f in existing_files]
        next_index = max(existing_indices, default=0) + 1

        self.status_label.config(text="⏺️ Recording...", fg="red")
        self.root.update()
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()

        filename = os.path.join(word_folder, f"{next_index}.wav")
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio.tobytes())

        self.status_label.config(text=f"✅ Saved: {filename}", fg="green")
        recording_count += 1

        if recording_count >= next_appreciation_at:
            appreciation_message = random.choice(appreciations)
            messagebox.showinfo("👏 Appreciation", appreciation_message)
            self.appreciation_label.config(text=appreciation_message)
            recording_count = 0
            next_appreciation_at = random.randint(5, 8)

        current_word_index += 1
        self.refresh_word()

# Start App
root = tk.Tk()
app = VoiceRecorderApp(root)
root.mainloop()
"""














"""


import tkinter as tk
from tkinter import messagebox, ttk
import sounddevice as sd
import numpy as np
import wave
import os
import random

# Settings
duration = 2  # seconds
sample_rate = 16000
recordings_root = "../F.voice model/data/recordings"
word_sources_folder = "word_sources"  # <-- Folder with multiple .txt files

# Desi-style prompts and appreciations
prompts = [
    "🎙️ Press Enter to record this masterpiece!",
    "🎙️ Ready? Hit Enter and let’s capture your voice!",
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

# Folder setup
os.makedirs(recordings_root, exist_ok=True)

# Load all words from multiple .txt files
words = []
for filename in os.listdir(word_sources_folder):
    if filename.endswith(".txt"):
        filepath = os.path.join(word_sources_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            words.extend([line.strip() for line in f if line.strip()])

random.shuffle(words)

# Tracking
recording_count = 0
next_appreciation_at = random.randint(5, 8)
current_word_index = 0

# GUI App
class VoiceRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Desi Voice Recorder")
        self.create_widgets()

    def create_widgets(self):
        self.word_label = tk.Label(self.root, text="", font=("Arial", 24, "bold"), fg="darkblue")
        self.word_label.pack(pady=20)

        self.prompt_label = tk.Label(self.root, text=random.choice(prompts), font=("Arial", 14))
        self.prompt_label.pack(pady=10)

        self.record_button = tk.Button(self.root, text="🎙️ Record Now", command=self.record_audio, font=("Arial", 16), bg="green", fg="white")
        self.record_button.pack(pady=10)

        self.skip_button = tk.Button(self.root, text="⏩ Skip Word", command=self.skip_word, font=("Arial", 12), bg="orange", fg="white")
        self.skip_button.pack(pady=5)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.appreciation_label = tk.Label(self.root, text="", font=("Arial", 12, "italic"), fg="purple")
        self.appreciation_label.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.refresh_word()

    def refresh_word(self):
        global current_word_index
        if current_word_index >= len(words):
            current_word_index = 0
            random.shuffle(words)
        self.word_label.config(text=f"🔤 {words[current_word_index]}")
        self.prompt_label.config(text=random.choice(prompts))
        self.appreciation_label.config(text="")  # Clear appreciation text
        self.progress["value"] = (current_word_index / len(words)) * 100

    def record_audio(self):
        global current_word_index, recording_count, next_appreciation_at

        word = words[current_word_index]
        word_folder = os.path.join(recordings_root, word)
        os.makedirs(word_folder, exist_ok=True)

        existing_files = [f for f in os.listdir(word_folder) if f.endswith(".wav") and f[:-4].isdigit()]
        existing_indices = [int(f[:-4]) for f in existing_files]
        next_index = max(existing_indices, default=0) + 1

        self.status_label.config(text="⏺️ Recording...", fg="red")
        self.root.update()
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()

        filename = os.path.join(word_folder, f"{next_index}.wav")
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio.tobytes())

        self.status_label.config(text=f"✅ Saved: {filename}", fg="green")
        recording_count += 1

        if recording_count >= next_appreciation_at:
            appreciation_message = random.choice(appreciations)
            messagebox.showinfo("👏 Appreciation", appreciation_message)
            self.appreciation_label.config(text=appreciation_message)
            recording_count = 0
            next_appreciation_at = random.randint(5, 8)

        current_word_index += 1
        self.refresh_word()

    def skip_word(self):
        global current_word_index
        self.status_label.config(text="⏩ Word Skipped!", fg="blue")
        current_word_index += 1
        self.refresh_word()

# Start App
root = tk.Tk()
app = VoiceRecorderApp(root)
root.mainloop()
"""















"""
import tkinter as tk
from tkinter import messagebox, ttk
import sounddevice as sd  
import numpy as np
import wave
import os
import random

# Settings
sample_rate = 16000
recordings_root = "../F.voice model/data/recordings"
word_sources_folder = "word_sources"  # <-- Folder with multiple .txt files

# Desi-style prompts and appreciations
prompts = [
    "🎙️ Press Enter to record this masterpiece!",
    "🎙️ Ready? Hit Enter and let’s capture your voice!",
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

# Duration calculator based on word length
def get_dynamic_duration(word):
    base = 1.5
    per_letter = 0.07
    per_space = 0.3
    buffer = 0.5

    letters = len(word.replace(" ", ""))
    spaces = word.count(" ")
    duration = base + (letters * per_letter) + (spaces * per_space) + buffer
    return round(duration, 2)

# Folder setup
os.makedirs(recordings_root, exist_ok=True)

# Load all words from multiple .txt files
words = []
for filename in os.listdir(word_sources_folder):
    if filename.endswith(".txt"):
        filepath = os.path.join(word_sources_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            words.extend([line.strip() for line in f if line.strip()])

random.shuffle(words)

# Tracking
recording_count = 0
next_appreciation_at = random.randint(5, 8)
current_word_index = 0

# GUI App
class VoiceRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Desi Voice Recorder")
        self.create_widgets()

    def create_widgets(self):
        self.word_label = tk.Label(self.root, text="", font=("Arial", 24, "bold"), fg="darkblue")
        self.word_label.pack(pady=20)

        self.prompt_label = tk.Label(self.root, text=random.choice(prompts), font=("Arial", 14))
        self.prompt_label.pack(pady=10)

        self.record_button = tk.Button(self.root, text="🎙️ Record Now", command=self.record_audio, font=("Arial", 16), bg="green", fg="white")
        self.record_button.pack(pady=10)

        self.skip_button = tk.Button(self.root, text="⏩ Skip Word", command=self.skip_word, font=("Arial", 12), bg="orange", fg="white")
        self.skip_button.pack(pady=5)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.appreciation_label = tk.Label(self.root, text="", font=("Arial", 12, "italic"), fg="purple")
        self.appreciation_label.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.refresh_word()

    def refresh_word(self):
        global current_word_index
        if current_word_index >= len(words):
            current_word_index = 0
            random.shuffle(words)
        self.word_label.config(text=f"🔤 {words[current_word_index]}")
        self.prompt_label.config(text=random.choice(prompts))
        self.appreciation_label.config(text="")  # Clear appreciation text
        self.progress["value"] = (current_word_index / len(words)) * 100

    def record_audio(self):
        global current_word_index, recording_count, next_appreciation_at

        word = words[current_word_index]
        word_folder = os.path.join(recordings_root, word)
        os.makedirs(word_folder, exist_ok=True)

        existing_files = [f for f in os.listdir(word_folder) if f.endswith(".wav") and f[:-4].isdigit()]
        existing_indices = [int(f[:-4]) for f in existing_files]
        next_index = max(existing_indices, default=0) + 1

        # ⏱️ Smart duration
        duration = get_dynamic_duration(word)

        self.status_label.config(text=f"⏺️ Recording for {duration} sec...", fg="red")
        self.root.update()

        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()

        filename = os.path.join(word_folder, f"{next_index}.wav")
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio.tobytes())

        self.status_label.config(text=f"✅ Saved: {filename}", fg="green")
        recording_count += 1

        if recording_count >= next_appreciation_at:
            appreciation_message = random.choice(appreciations)
            messagebox.showinfo("👏 Appreciation", appreciation_message)
            self.appreciation_label.config(text=appreciation_message)
            recording_count = 0
            next_appreciation_at = random.randint(5, 8)

        current_word_index += 1
        self.refresh_word()

    def skip_word(self):
        global current_word_index
        self.status_label.config(text="⏩ Word Skipped!", fg="blue")
        current_word_index += 1
        self.refresh_word()

# Start App
root = tk.Tk()
app = VoiceRecorderApp(root)
root.mainloop()
"""
















import tkinter as tk
from tkinter import messagebox, ttk
import sounddevice as sd  
import numpy as np
import wave
import os
import random

# Settings
sample_rate = 16000
recordings_root = "../F.voice model/data/recordings"
word_sources_folder = "word_sources"  # <-- Folder with multiple .txt files

# Desi-style prompts and appreciations
prompts = [
    "🎙️ Press Enter to record this masterpiece!",
    "🎙️ Ready? Hit Enter and let’s capture your voice!",
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

# Duration calculator based on word length
def get_dynamic_duration(word):
    base = 1.5
    per_letter = 0.07
    per_space = 0.3
    buffer = 0.5

    letters = len(word.replace(" ", ""))
    spaces = word.count(" ")
    duration = base + (letters * per_letter) + (spaces * per_space) + buffer
    return round(duration, 2)

# Folder setup
os.makedirs(recordings_root, exist_ok=True)

# Load all words from multiple .txt files
words = []
for filename in os.listdir(word_sources_folder):
    if filename.endswith(".txt"):
        filepath = os.path.join(word_sources_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            words.extend([line.strip() for line in f if line.strip()])

random.shuffle(words)

# Tracking
recording_count = 0
next_appreciation_at = random.randint(5, 8)
current_word_index = 0
last_recorded_filename = ""  # Track the last recorded file for retry

# GUI App
class VoiceRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Desi Voice Recorder")
        self.create_widgets()

    def create_widgets(self):
        self.word_label = tk.Label(self.root, text="", font=("Arial", 24, "bold"), fg="darkblue")
        self.word_label.pack(pady=20)

        self.prompt_label = tk.Label(self.root, text=random.choice(prompts), font=("Arial", 14))
        self.prompt_label.pack(pady=10)

        self.record_button = tk.Button(self.root, text="🎙️ Record Now", command=self.record_audio, font=("Arial", 16), bg="green", fg="white")
        self.record_button.pack(pady=10)

        self.retry_button = tk.Button(self.root, text="🔄 Retry", command=self.retry_recording, font=("Arial", 12), bg="yellow", fg="black")
        self.retry_button.pack(pady=5)

        self.skip_button = tk.Button(self.root, text="⏩ Skip Word", command=self.skip_word, font=("Arial", 12), bg="orange", fg="white")
        self.skip_button.pack(pady=5)

        self.status_label = tk.Label(self.root, text="", font=("Arial", 12))
        self.status_label.pack(pady=5)

        self.appreciation_label = tk.Label(self.root, text="", font=("Arial", 12, "italic"), fg="purple")
        self.appreciation_label.pack(pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.refresh_word()

    def refresh_word(self):
        global current_word_index
        if current_word_index >= len(words):
            current_word_index = 0
            random.shuffle(words)
        self.word_label.config(text=f"🔤 {words[current_word_index]}")
        self.prompt_label.config(text=random.choice(prompts))
        self.appreciation_label.config(text="")  # Clear appreciation text
        self.progress["value"] = (current_word_index / len(words)) * 100

    def record_audio(self):
        global current_word_index, recording_count, next_appreciation_at, last_recorded_filename

        word = words[current_word_index]
        word_folder = os.path.join(recordings_root, word)
        os.makedirs(word_folder, exist_ok=True)

        existing_files = [f for f in os.listdir(word_folder) if f.endswith(".wav") and f[:-4].isdigit()]
        existing_indices = [int(f[:-4]) for f in existing_files]
        next_index = max(existing_indices, default=0) + 1

        # ⏱️ Smart duration
        duration = get_dynamic_duration(word)

        self.status_label.config(text=f"⏺️ Recording for {duration} sec...", fg="red")
        self.root.update()

        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()

        filename = os.path.join(word_folder, f"{next_index}.wav")
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio.tobytes())

        last_recorded_filename = filename  # Save the file path for retry

        self.status_label.config(text=f"✅ Saved: {filename}", fg="green")
        recording_count += 1

        if recording_count >= next_appreciation_at:
            appreciation_message = random.choice(appreciations)
            messagebox.showinfo("👏 Appreciation", appreciation_message)
            self.appreciation_label.config(text=appreciation_message)
            recording_count = 0
            next_appreciation_at = random.randint(5, 8)

        current_word_index += 1
        self.refresh_word()

    def skip_word(self):
        global current_word_index
        self.status_label.config(text="⏩ Word Skipped!", fg="blue")
        current_word_index += 1
        self.refresh_word()

    def retry_recording(self):
        global last_recorded_filename

        if last_recorded_filename:
            try:
                os.remove(last_recorded_filename)  # Remove the previous file
                self.status_label.config(text="⏺️ Retrying recording...", fg="red")
                self.record_audio()  # Retry recording the same word
            except Exception as e:
                self.status_label.config(text=f"❌ Error: {str(e)}", fg="red")
        else:
            self.status_label.config(text="❌ No recording to retry.", fg="red")

# Start App
root = tk.Tk()
app = VoiceRecorderApp(root)
root.mainloop()
