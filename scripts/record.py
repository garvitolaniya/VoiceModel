import tkinter as tk
from tkinter import messagebox, ttk
import sounddevice as sd
import numpy as np
import wave
import os
import random
import threading
import time
from PIL import Image, ImageTk

# Settings
sample_rate = 16000
recordings_root = "../F.voice model/data/recordings"
word_sources_folder = "word_sources"

# Color Scheme
COLORS = {
    'primary': '#6C3EFF',  # Purplish
    'secondary': '#FFD700',  # Gold
    'accent': '#23232B',     # Blackish (not used in gradient)
    'background': '#181622', # Deep dark (not used in gradient)
    'surface': '#F7FAFC',    # Very light blue/gray for content area
    'text': '#23232B',       # Blackish
    'text_light': '#7F8C8D', # Medium gray
    'success': '#27AE60',    # Professional green
    'error': '#E74C3C',      # Professional red
    'warning': '#F39C12',    # Professional orange
}

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

def get_dynamic_duration(word):
    base = 1.5
    per_letter = 0.07
    per_space = 0.3
    buffer = 0.5
    letters = len(word.replace(" ", ""))
    spaces = word.count(" ")
    duration = base + (letters * per_letter) + (spaces * per_space) + buffer
    return round(duration, 2)

class WelcomeScreen:
    def __init__(self, root, on_start):
        self.root = root
        self.root.title("Voice Recorder Pro")
        self.root.geometry("1200x800")
        self.root.state('zoomed')
        self.on_start = on_start

        # Responsive welcome frame
        self.frame = tk.Frame(root, bg=COLORS['surface'])
        self.frame.pack(expand=True, fill="both")

        # Gradient canvas
        self.gradient_canvas = tk.Canvas(
            self.frame,
            highlightthickness=0,
            bg=COLORS['surface']
        )
        self.gradient_canvas.pack(expand=True, fill="both")
        self.gradient_canvas.bind('<Configure>', self.on_resize)

        # Content frame (centered, responsive)
        self.content_frame = tk.Frame(
            self.gradient_canvas,
            bg=COLORS['surface'],
            bd=0,
            highlightthickness=0
        )
        self.content_window = self.gradient_canvas.create_window(
            self.root.winfo_screenwidth() // 2,
            self.root.winfo_screenheight() // 2,
            window=self.content_frame,
            anchor="center"
        )

        # Header
        self.header_frame = tk.Frame(self.content_frame, bg=COLORS['surface'], height=100)
        self.header_frame.pack(fill="x", pady=(20, 0))
        self.logo_canvas = tk.Canvas(self.header_frame, width=60, height=60, bg=COLORS['surface'], highlightthickness=0)
        self.logo_canvas.pack(side="left", padx=20)
        self.logo_canvas.create_oval(10, 10, 50, 50, fill=COLORS['primary'], outline="")
        self.logo_canvas.create_rectangle(25, 50, 35, 60, fill=COLORS['primary'], outline="")
        self.logo_canvas.create_rectangle(15, 60, 45, 65, fill=COLORS['primary'], outline="")
        self.title_frame = tk.Frame(self.header_frame, bg=COLORS['surface'])
        self.title_frame.pack(side="left", padx=10)
        self.welcome_label = tk.Label(self.title_frame, text="Welcome to", font=("Segoe UI", 20), fg=COLORS['text_light'], bg=COLORS['surface'])
        self.welcome_label.pack(anchor="w")
        self.app_name_label = tk.Label(self.title_frame, text="Voice Recorder Pro", font=("Segoe UI", 32, "bold"), fg=COLORS['primary'], bg=COLORS['surface'])
        self.app_name_label.pack(anchor="w")

        # Description
        self.desc_frame = tk.Frame(self.content_frame, bg=COLORS['surface'])
        self.desc_frame.pack(fill="x", pady=30)
        self.desc_label = tk.Label(
            self.desc_frame,
            text="Record your voice to help train our AI model.\nEach recording helps make the model smarter!",
            font=("Segoe UI", 16),
            fg=COLORS['text_light'],
            bg=COLORS['surface'],
            justify="center"
        )
        self.desc_label.pack()

        # Features
        self.features_frame = tk.Frame(self.content_frame, bg=COLORS['surface'])
        self.features_frame.pack(fill="x", pady=20)
        features = [
            "🎯 High-quality audio recording",
            "📊 Real-time progress tracking",
            "🎙️ Professional-grade microphone support",
            "💾 Automatic file organization"
        ]
        for feature in features:
            feature_label = tk.Label(
                self.features_frame,
                text=feature,
                font=("Segoe UI", 14),
                fg=COLORS['text'],
                bg=COLORS['surface'],
                justify="left"
            )
            feature_label.pack(pady=5)

        # Start button
        self.button_frame = tk.Frame(self.content_frame, bg=COLORS['surface'])
        self.button_frame.pack(fill="x", pady=30)
        self.start_button = tk.Button(
            self.button_frame,
            text="Start Recording",
            command=self.start_app,
            font=("Segoe UI", 16, "bold"),
            bg=COLORS['primary'],
            fg="white",
            padx=30,
            pady=15,
            relief="flat",
            borderwidth=0,
            activebackground=COLORS['secondary'],
            activeforeground="white",
            cursor="hand2"
        )
        self.start_button.pack()
        self.start_button.bind("<Enter>", lambda e: self.start_button.configure(bg=COLORS['secondary']))
        self.start_button.bind("<Leave>", lambda e: self.start_button.configure(bg=COLORS['primary']))
        self.root.bind("<Return>", lambda e: self.start_app())
        self.animate_logo()

        # Set gradient colors for purple to gold
        self.gradient_top = COLORS['primary']
        self.gradient_bottom = COLORS['secondary']
        self.animate_gradient()

    def on_resize(self, event):
        # Resize gradient and center content
        self.gradient_canvas.config(width=event.width, height=event.height)
        self.gradient_canvas.delete("gradient")
        self.draw_gradient(event.width, event.height)
        self.gradient_canvas.coords(self.content_window, event.width // 2, event.height // 2)

    def draw_gradient(self, width, height):
        # Draw a simple vertical gradient from purple to gold
        for i in range(height):
            ratio = i / max(height - 1, 1)
            r = int(int(self.gradient_top[1:3], 16) * (1 - ratio) + int(self.gradient_bottom[1:3], 16) * ratio)
            g = int(int(self.gradient_top[3:5], 16) * (1 - ratio) + int(self.gradient_bottom[3:5], 16) * ratio)
            b = int(int(self.gradient_top[5:7], 16) * (1 - ratio) + int(self.gradient_bottom[5:7], 16) * ratio)
            interpolated_color = f"#{r:02x}{g:02x}{b:02x}"
            self.gradient_canvas.create_line(0, i, width, i, fill=interpolated_color, tags="gradient")

    def animate_gradient(self):
        # Just redraw the gradient for responsiveness
        w = self.gradient_canvas.winfo_width()
        h = self.gradient_canvas.winfo_height()
        if w > 1 and h > 1:
            self.gradient_canvas.delete("gradient")
            self.draw_gradient(w, h)
        self.root.after(200, self.animate_gradient)

    def animate_logo(self):
        # Subtle logo animation
        current_color = self.logo_canvas.itemcget(1, "fill")
        if current_color == COLORS['primary']:
            self.logo_canvas.itemconfig(1, fill=COLORS['secondary'])
            self.logo_canvas.itemconfig(2, fill=COLORS['secondary'])
            self.logo_canvas.itemconfig(3, fill=COLORS['secondary'])
        else:
            self.logo_canvas.itemconfig(1, fill=COLORS['primary'])
            self.logo_canvas.itemconfig(2, fill=COLORS['primary'])
            self.logo_canvas.itemconfig(3, fill=COLORS['primary'])
        self.root.after(1000, self.animate_logo)

    def start_app(self):
        self.frame.destroy()
        self.on_start()

class VoiceRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Voice Recorder Pro")
        self.root.geometry("1200x800")
        self.root.state('zoomed')  # Start maximized
        self.root.configure(bg=COLORS['background'])
        
        # Variables
        self.recording_count = 0
        self.next_appreciation_at = random.randint(5, 8)
        self.current_word_index = 0
        self.last_recorded_filename = ""
        self.is_recording = False
        self.recording_start_time = 0
        self.total_recordings = 0
        
        # Create main frame
        self.main_frame = tk.Frame(root, bg=COLORS['background'])
        self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Create content frame with shadow effect
        self.content_frame = tk.Frame(
            self.main_frame,
            bg=COLORS['surface'],
            bd=0,
            highlightthickness=2,
            highlightbackground=COLORS['primary']
        )
        self.content_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Create widgets
        self.create_widgets()
        self.refresh_word()
        
        # Start animation
        self.animate_ui()
        
        # Add keyboard shortcuts
        self.root.bind("<space>", lambda e: self.record_audio())
        self.root.bind("<Right>", lambda e: self.skip_word())
        self.root.bind("<r>", lambda e: self.retry_recording())

    def animate_ui(self):
        # Animate the recording circle
        if self.is_recording:
            current_color = self.recording_canvas.itemcget(self.recording_circle, "fill")
            new_color = COLORS['error'] if current_color == COLORS['secondary'] else COLORS['secondary']
            self.recording_canvas.itemconfig(self.recording_circle, fill=new_color)
            
            # Update recording time
            elapsed_time = time.time() - self.recording_start_time
            self.status_label.config(text=f"⏺️ Recording... {int(elapsed_time)}s", fg=COLORS['error'])
        
        # Animate the progress bar
        current_value = self.progress["value"]
        target_value = (self.current_word_index / len(words)) * 100
        if current_value < target_value:
            self.progress["value"] = min(current_value + 1, target_value)
        
        # Animate the word display
        if not self.is_recording:
            current_color = self.word_canvas.itemcget(self.word_label, "fill")
            if current_color == COLORS['primary']:
                self.word_canvas.itemconfig(self.word_label, fill=COLORS['secondary'])
            else:
                self.word_canvas.itemconfig(self.word_label, fill=COLORS['primary'])
        
        self.root.after(1000, self.animate_ui)

    def create_widgets(self):
        # Header
        self.header_frame = tk.Frame(self.content_frame, bg=COLORS['surface'])
        self.header_frame.pack(fill="x", padx=20, pady=20)
        
        # Title with gradient effect
        self.title_label = tk.Label(
            self.header_frame,
            text="Voice Recorder Pro",
            font=("Segoe UI", 28, "bold"),
            fg=COLORS['primary'],
            bg=COLORS['surface']
        )
        self.title_label.pack(side="left")
        
        # Stats frame
        self.stats_frame = tk.Frame(self.header_frame, bg=COLORS['surface'])
        self.stats_frame.pack(side="right", padx=10)
        
        self.stats_label = tk.Label(
            self.stats_frame,
            text="Recordings: 0",
            font=("Segoe UI", 12),
            fg=COLORS['text_light'],
            bg=COLORS['surface']
        )
        self.stats_label.pack()
        
        # Main content
        self.word_frame = tk.Frame(self.content_frame, bg=COLORS['surface'])
        self.word_frame.pack(pady=(40, 20))
        
        # Word display with animation
        self.word_canvas = tk.Canvas(
            self.word_frame,
            width=800,
            height=150,
            bg=COLORS['surface'],
            highlightthickness=0
        )
        self.word_canvas.pack()
        self.word_label = self.word_canvas.create_text(
            400, 75,
            text="",
            font=("Segoe UI", 48, "bold"),
            fill=COLORS['primary']
        )
        
        # Prompt label
        self.prompt_label = tk.Label(
            self.word_frame,
            text="",
            font=("Segoe UI", 16),
            fg=COLORS['text_light'],
            bg=COLORS['surface']
        )
        self.prompt_label.pack(pady=10)
        
        # Buttons frame
        self.button_frame = tk.Frame(self.content_frame, bg=COLORS['surface'])
        self.button_frame.pack(pady=20)
        
        # Record button with hover effect
        self.record_button = tk.Button(
            self.button_frame,
            text="🎙️ Record Now (Space)",
            command=self.record_audio,
            font=("Segoe UI", 16, "bold"),
            bg=COLORS['primary'],
            fg="white",
            padx=30,
            pady=15,
            relief="flat",
            borderwidth=0,
            activebackground=COLORS['secondary'],
            activeforeground="white"
        )
        self.record_button.pack(pady=10)
        
        # Control buttons frame
        self.control_frame = tk.Frame(self.button_frame, bg=COLORS['surface'])
        self.control_frame.pack(pady=5)
        
        # Retry button
        self.retry_button = tk.Button(
            self.control_frame,
            text="🔄 Retry (R)",
            command=self.retry_recording,
            font=("Segoe UI", 12),
            bg=COLORS['warning'],
            fg="black",
            padx=20,
            pady=10,
            relief="flat",
            borderwidth=0,
            activebackground=COLORS['accent'],
            activeforeground="black"
        )
        self.retry_button.pack(side="left", padx=5)
        
        # Skip button
        self.skip_button = tk.Button(
            self.control_frame,
            text="⏩ Skip Word (→)",
            command=self.skip_word,
            font=("Segoe UI", 12),
            bg=COLORS['error'],
            fg="white",
            padx=20,
            pady=10,
            relief="flat",
            borderwidth=0,
            activebackground=COLORS['secondary'],
            activeforeground="white"
        )
        self.skip_button.pack(side="left", padx=5)
        
        # Status label
        self.status_label = tk.Label(
            self.content_frame,
            text="",
            font=("Segoe UI", 14),
            fg=COLORS['text'],
            bg=COLORS['surface']
        )
        self.status_label.pack(pady=10)
        
        # Appreciation label
        self.appreciation_label = tk.Label(
            self.content_frame,
            text="",
            font=("Segoe UI", 14, "italic"),
            fg=COLORS['primary'],
            bg=COLORS['surface']
        )
        self.appreciation_label.pack(pady=5)
        
        # Progress bar
        self.progress_frame = tk.Frame(self.content_frame, bg=COLORS['surface'])
        self.progress_frame.pack(pady=20)
        
        self.progress = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=800,
            mode="determinate",
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=10)
        
        # Configure progress bar style
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar",
                       background=COLORS['primary'],
                       troughcolor=COLORS['background'],
                       bordercolor=COLORS['primary'],
                       lightcolor=COLORS['secondary'],
                       darkcolor=COLORS['primary'])
        
        # Recording animation
        self.recording_canvas = tk.Canvas(
            self.content_frame,
            width=100,
            height=100,
            bg=COLORS['surface'],
            highlightthickness=0
        )
        self.recording_canvas.pack(pady=10)
        self.recording_circle = self.recording_canvas.create_oval(
            20, 20, 80, 80,
            fill=COLORS['error'],
            outline=""
        )
        self.recording_canvas.pack_forget()
        
        # Add hover effects
        self.add_hover_effects()

    def add_hover_effects(self):
        def on_enter(button, color):
            button.configure(bg=color)
            
        def on_leave(button, color):
            button.configure(bg=color)
            
        # Record button
        self.record_button.bind("<Enter>", lambda e: on_enter(self.record_button, COLORS['secondary']))
        self.record_button.bind("<Leave>", lambda e: on_leave(self.record_button, COLORS['primary']))
        
        # Retry button
        self.retry_button.bind("<Enter>", lambda e: on_enter(self.retry_button, COLORS['accent']))
        self.retry_button.bind("<Leave>", lambda e: on_leave(self.retry_button, COLORS['warning']))
        
        # Skip button
        self.skip_button.bind("<Enter>", lambda e: on_enter(self.skip_button, COLORS['secondary']))
        self.skip_button.bind("<Leave>", lambda e: on_leave(self.skip_button, COLORS['error']))

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

# Load words
words = []
for filename in os.listdir(word_sources_folder):
    if filename.endswith(".txt"):
        filepath = os.path.join(word_sources_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            words.extend([line.strip() for line in f if line.strip()])

random.shuffle(words)

# Start App
if __name__ == "__main__":
    root = tk.Tk()
    
    def start_app():
        app = VoiceRecorderApp(root)
    
    welcome = WelcomeScreen(root, start_app)
    root.mainloop()
