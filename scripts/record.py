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
    'primary': '#6C3EFF',  # Rich Purple
    'secondary': '#FFD700',  # Gold
    'accent': '#23232B',     # Dark Gray
    'background': '#0A0A0F', # Deep Space Black
    'surface': '#1A1A1A',    # Dark Surface
    'glass': '#2A2A2A',      # Semi-transparent dark
    'text': '#FFFFFF',       # White
    'text_light': '#B8B8B8', # Light Gray
    'success': '#00FF9D',    # Neon Green
    'error': '#FF3366',      # Neon Pink
    'warning': '#FFD700',    # Gold
    'glass_border': '#3A3A3A',  # Glass border
    'glass_shadow': '#000000',   # Shadow color
    'gradient_start': '#6C3EFF', # Gradient start
    'gradient_end': '#FFD700',   # Gradient end
    'glow': '#6C3EFF',           # Glow effect color
    'card_bg': '#2A2A2A',        # Card background
    'card_hover': '#3A3A3A'      # Card hover color
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
    """Calculate recording duration based on word length"""
    base = 1.5  # Base duration in seconds
    per_letter = 0.07  # Additional time per letter
    per_space = 0.3  # Additional time per space
    buffer = 0.5  # Buffer time
    
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

        # Create a canvas for the animated background
        self.bg_canvas = tk.Canvas(root, highlightthickness=0, bg=COLORS['background'])
        self.bg_canvas.pack(expand=True, fill="both")
        self.bg_canvas.bind('<Configure>', self.on_resize)
        
        # Create floating particles with more variety
        self.particles = []
        self.create_particles()
        self.animate_particles()

        # Main content frame with enhanced glass effect
        self.content_frame = tk.Frame(
            self.bg_canvas,
            bg=COLORS['glass'],
            bd=0,
            highlightthickness=2,
            highlightbackground=COLORS['glass_border']
        )
        self.content_window = self.bg_canvas.create_window(
            self.root.winfo_screenwidth() // 2,
            self.root.winfo_screenheight() // 2,
            window=self.content_frame,
            anchor="center"
        )

        # Header with modern design and glow effect
        self.header_frame = tk.Frame(self.content_frame, bg=COLORS['glass'], height=120)
        self.header_frame.pack(fill="x", pady=(40, 0))
        
        # Enhanced animated logo with glow
        self.logo_canvas = tk.Canvas(
            self.header_frame,
            width=100,
            height=100,
            bg=COLORS['glass'],
            highlightthickness=0
        )
        self.logo_canvas.pack(side="left", padx=30)
        self.draw_logo()
        self.animate_logo()

        # Title with enhanced styling
        self.title_frame = tk.Frame(self.header_frame, bg=COLORS['glass'])
        self.title_frame.pack(side="left", padx=20)
        self.welcome_label = tk.Label(
            self.title_frame,
            text="Welcome to",
            font=("Segoe UI", 28),
            fg=COLORS['text_light'],
            bg=COLORS['glass']
        )
        self.welcome_label.pack(anchor="w")
        self.app_name_label = tk.Label(
            self.title_frame,
            text="Voice Recorder Pro",
            font=("Segoe UI", 42, "bold"),
            fg=COLORS['primary'],
            bg=COLORS['glass']
        )
        self.app_name_label.pack(anchor="w")

        # Description with enhanced styling
        self.desc_frame = tk.Frame(self.content_frame, bg=COLORS['glass'])
        self.desc_frame.pack(fill="x", pady=40)
        self.desc_label = tk.Label(
            self.desc_frame,
            text="Record your voice to help train our AI model.\nEach recording helps make the model smarter!",
            font=("Segoe UI", 20),
            fg=COLORS['text_light'],
            bg=COLORS['glass'],
            justify="center"
        )
        self.desc_label.pack()

        # Features in modern card layout
        self.features_frame = tk.Frame(self.content_frame, bg=COLORS['glass'])
        self.features_frame.pack(fill="x", pady=20)
        
        # Create feature cards
        features = [
            {
                "icon": "🎯",
                "title": "High-quality Recording",
                "description": "Professional-grade audio capture with real-time monitoring"
            },
            {
                "icon": "📊",
                "title": "Progress Tracking",
                "description": "Visual progress indicators and achievement milestones"
            },
            {
                "icon": "🎙️",
                "title": "Microphone Support",
                "description": "Compatible with all professional microphones"
            },
            {
                "icon": "💾",
                "title": "Smart Organization",
                "description": "Automatic file management and categorization"
            }
        ]

        # Create a frame for the cards
        self.cards_frame = tk.Frame(self.features_frame, bg=COLORS['glass'])
        self.cards_frame.pack(fill="x", pady=10)

        # Create cards in a grid
        for i, feature in enumerate(features):
            card = self.create_feature_card(feature)
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            self.cards_frame.grid_columnconfigure(i%2, weight=1)

        # Premium start button with gradient effect
        self.button_frame = tk.Frame(self.content_frame, bg=COLORS['glass'])
        self.button_frame.pack(fill="x", pady=40)
        
        # Create a loading animation frame
        self.loading_frame = tk.Frame(self.button_frame, bg=COLORS['glass'])
        self.loading_frame.pack(pady=10)
        self.loading_dots = []
        self.create_loading_animation()
        
        self.start_button = tk.Button(
            self.button_frame,
            text="Start Recording",
            command=self.start_app,
            font=("Segoe UI", 20, "bold"),
            bg=COLORS['primary'],
            fg="white",
            padx=50,
            pady=20,
            relief="flat",
            borderwidth=0,
            activebackground=COLORS['secondary'],
            activeforeground="white",
            cursor="hand2"
        )
        self.start_button.pack()
        
        # Enhanced hover animation
        self.start_button.bind("<Enter>", lambda e: (
            self.start_button.configure(
                bg=COLORS['secondary'],
                fg=COLORS['primary']
            ),
            self.create_button_glow(self.start_button),
            self.animate_loading(True)
        ))
        self.start_button.bind("<Leave>", lambda e: (
            self.start_button.configure(
                bg=COLORS['primary'],
                fg="white"
            ),
            self.remove_button_glow(self.start_button),
            self.animate_loading(False)
        ))

        # Add keyboard shortcut
        self.root.bind("<Return>", lambda e: self.start_app())

    def create_feature_card(self, feature):
        # Create a modern card with hover effect
        card = tk.Frame(
            self.cards_frame,
            bg=COLORS['card_bg'],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS['glass_border']
        )
        
        # Card content
        icon_label = tk.Label(
            card,
            text=feature["icon"],
            font=("Segoe UI", 24),
            bg=COLORS['card_bg'],
            fg=COLORS['primary']
        )
        icon_label.pack(pady=(15, 5))
        
        title_label = tk.Label(
            card,
            text=feature["title"],
            font=("Segoe UI", 16, "bold"),
            bg=COLORS['card_bg'],
            fg=COLORS['text']
        )
        title_label.pack(pady=5)
        
        desc_label = tk.Label(
            card,
            text=feature["description"],
            font=("Segoe UI", 12),
            bg=COLORS['card_bg'],
            fg=COLORS['text_light'],
            wraplength=200
        )
        desc_label.pack(pady=(0, 15), padx=10)
        
        # Add hover effect
        card.bind("<Enter>", lambda e, c=card: self.on_card_enter(c))
        card.bind("<Leave>", lambda e, c=card: self.on_card_leave(c))
        
        return card

    def on_card_enter(self, card):
        card.configure(bg=COLORS['card_hover'])
        for widget in card.winfo_children():
            widget.configure(bg=COLORS['card_hover'])
        self.create_card_glow(card)

    def on_card_leave(self, card):
        card.configure(bg=COLORS['card_bg'])
        for widget in card.winfo_children():
            widget.configure(bg=COLORS['card_bg'])
        self.remove_card_glow(card)

    def create_card_glow(self, card):
        x, y = card.winfo_x(), card.winfo_y()
        width, height = card.winfo_width(), card.winfo_height()
        self.card_glow_id = self.bg_canvas.create_rectangle(
            x-5, y-5, x+width+5, y+height+5,
            outline=COLORS['glow'],
            width=2,
            tags="card_glow"
        )

    def remove_card_glow(self, card):
        self.bg_canvas.delete("card_glow")

    def create_loading_animation(self):
        # Create loading dots
        for i in range(3):
            dot = tk.Label(
                self.loading_frame,
                text="•",
                font=("Segoe UI", 20),
                bg=COLORS['glass'],
                fg=COLORS['primary']
            )
            dot.pack(side="left", padx=2)
            self.loading_dots.append(dot)
        self.loading_frame.pack_forget()  # Hide initially

    def animate_loading(self, show):
        if show:
            self.loading_frame.pack(pady=10)
            self.animate_dots()
        else:
            self.loading_frame.pack_forget()
            for dot in self.loading_dots:
                dot.configure(fg=COLORS['primary'])

    def animate_dots(self):
        for i, dot in enumerate(self.loading_dots):
            if dot.cget("fg") == COLORS['primary']:
                dot.configure(fg=COLORS['secondary'])
            else:
                dot.configure(fg=COLORS['primary'])
        self.root.after(500, self.animate_dots)

    def create_glow_effect(self, widget):
        # Create a glowing effect around the widget
        x, y = widget.winfo_x(), widget.winfo_y()
        width, height = widget.winfo_width(), widget.winfo_height()
        self.glow_id = self.bg_canvas.create_oval(
            x-5, y-5, x+width+5, y+height+5,
            outline=COLORS['glow'],
            width=2,
            tags="glow"
        )

    def remove_glow_effect(self, widget):
        # Remove the glowing effect
        self.bg_canvas.delete("glow")

    def create_button_glow(self, button):
        # Create a glowing effect around the button
        x, y = button.winfo_x(), button.winfo_y()
        width, height = button.winfo_width(), button.winfo_height()
        self.button_glow_id = self.bg_canvas.create_oval(
            x-10, y-10, x+width+10, y+height+10,
            outline=COLORS['glow'],
            width=3,
            tags="button_glow"
        )

    def remove_button_glow(self, button):
        # Remove the button glowing effect
        self.bg_canvas.delete("button_glow")

    def draw_logo(self):
        # Draw an enhanced modern logo
        self.logo_canvas.delete("all")
        # Outer glow
        self.logo_canvas.create_oval(5, 5, 95, 95, 
            outline=COLORS['glow'],
            width=2,
            tags="logo_glow"
        )
        # Main logo
        self.logo_canvas.create_oval(15, 15, 85, 85, 
            outline=COLORS['primary'],
            width=3,
            tags="logo"
        )
        # Inner elements with gradient effect
        self.logo_canvas.create_arc(25, 25, 75, 75,
            start=45,
            extent=270,
            outline=COLORS['secondary'],
            width=3,
            tags="logo"
        )
        # Center dot with glow
        self.logo_canvas.create_oval(45, 45, 55, 55,
            fill=COLORS['primary'],
            outline=COLORS['glow'],
            tags="logo"
        )

    def animate_logo(self):
        # Rotate the logo
        self.logo_canvas.delete("logo")
        self.draw_logo()
        self.root.after(50, self.animate_logo)

    def create_particles(self):
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()
        for _ in range(100):  # Increased number of particles
            x = random.randint(0, w)
            y = random.randint(0, h)
            size = random.randint(1, 4)  # Varied sizes
            color = random.choice([
                COLORS['primary'],
                COLORS['secondary'],
                '#FFFFFF',
                COLORS['glow']
            ])
            particle = self.bg_canvas.create_oval(
                x, y, x+size, y+size,
                fill=color,
                outline="",
                tags="particle"
            )
            self.particles.append({
                'id': particle,
                'x': x,
                'y': y,
                'dx': random.uniform(-1.5, 1.5),  # Faster movement
                'dy': random.uniform(-1.5, 1.5),
                'size': size,
                'color': color
            })

    def animate_particles(self):
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            
            # Bounce off walls with slight size change
            if particle['x'] <= 0 or particle['x'] >= w:
                particle['dx'] *= -1
                particle['size'] = random.randint(1, 4)
            if particle['y'] <= 0 or particle['y'] >= h:
                particle['dy'] *= -1
                particle['size'] = random.randint(1, 4)
                
            self.bg_canvas.coords(
                particle['id'],
                particle['x'],
                particle['y'],
                particle['x'] + particle['size'],
                particle['y'] + particle['size']
            )
        self.root.after(20, self.animate_particles)  # Faster animation

    def on_resize(self, event):
        # Update canvas and content positioning
        self.bg_canvas.config(width=event.width, height=event.height)
        self.bg_canvas.coords(self.content_window, event.width // 2, event.height // 2)

    def start_app(self):
        self.bg_canvas.destroy()
        self.on_start()

class VoiceRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎤 Voice Recorder Pro")
        self.root.geometry("1200x800")
        self.root.state('zoomed')
        
        # Create a canvas for the animated background
        self.bg_canvas = tk.Canvas(root, highlightthickness=0)
        self.bg_canvas.pack(expand=True, fill="both")
        self.bg_canvas.bind('<Configure>', self.on_resize)
        
        # Create floating particles
        self.particles = []
        self.create_particles()
        self.animate_particles()
        
        # Main content frame with glass effect
        self.content_frame = tk.Frame(
            self.bg_canvas,
            bg=COLORS['surface'],
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS['glass_border']
        )
        self.content_window = self.bg_canvas.create_window(
            self.root.winfo_screenwidth() // 2,
            self.root.winfo_screenheight() // 2,
            window=self.content_frame,
            anchor="center"
        )
        
        # Variables
        self.recording_count = 0
        self.next_appreciation_at = random.randint(5, 8)
        self.current_word_index = 0
        self.last_recorded_filename = ""
        self.is_recording = False
        self.recording_start_time = 0
        self.total_recordings = 0
        
        # Create widgets
        self.create_widgets()
        self.refresh_word()
        
        # Start animation
        self.animate_ui()
        
        # Add keyboard shortcuts
        self.root.bind("<space>", lambda e: self.record_audio())
        self.root.bind("<Right>", lambda e: self.skip_word())
        self.root.bind("<r>", lambda e: self.retry_recording())

    def on_resize(self, event):
        # Update canvas and content positioning
        self.bg_canvas.config(width=event.width, height=event.height)
        self.bg_canvas.coords(self.content_window, event.width // 2, event.height // 2)

    def create_particles(self):
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()
        for _ in range(50):
            x = random.randint(0, w)
            y = random.randint(0, h)
            size = random.randint(1, 3)
            color = random.choice(['#6C3EFF', '#FFD700', '#FFFFFF'])
            particle = self.bg_canvas.create_oval(
                x, y, x+size, y+size,
                fill=color,
                outline="",
                tags="particle"
            )
            self.particles.append({
                'id': particle,
                'x': x,
                'y': y,
                'dx': random.uniform(-1, 1),
                'dy': random.uniform(-1, 1)
            })

    def animate_particles(self):
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()
        for particle in self.particles:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            
            # Bounce off walls
            if particle['x'] <= 0 or particle['x'] >= w:
                particle['dx'] *= -1
            if particle['y'] <= 0 or particle['y'] >= h:
                particle['dy'] *= -1
                
            self.bg_canvas.coords(
                particle['id'],
                particle['x'],
                particle['y'],
                particle['x'] + 2,
                particle['y'] + 2
            )
        self.root.after(30, self.animate_particles)

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

class VoiceRecorder:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.recordings_root = "../F.voice model/data/recordings"
        os.makedirs(self.recordings_root, exist_ok=True)

    def record(self, word=None, duration=None):
        """Record audio for the specified duration or word"""
        if word:
            duration = get_dynamic_duration(word)
            print(f"Recording word '{word}' for {duration} seconds...")
        elif not duration:
            duration = 5  # Default duration if neither word nor duration is provided
            print(f"Recording for default duration of {duration} seconds...")
        
        # Record audio
        audio = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype='int16'
        )
        sd.wait()

        # Create word-specific folder
        if word:
            word_folder = os.path.join(self.recordings_root, word)
            os.makedirs(word_folder, exist_ok=True)
            
            # Get next index for this word
            existing_files = [f for f in os.listdir(word_folder) if f.endswith(".wav") and f[:-4].isdigit()]
            existing_indices = [int(f[:-4]) for f in existing_files]
            next_index = max(existing_indices, default=0) + 1
            
            filename = os.path.join(word_folder, f"{next_index}.wav")
        else:
            # Generate filename with timestamp for non-word recordings
            timestamp = int(time.time())
            filename = os.path.join(self.recordings_root, f"recording_{timestamp}.wav")

        # Save the recording
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio.tobytes())

        print(f"Recording saved to {filename}")
        return filename

    def get_recording_status(self):
        """Get the current recording status"""
        return {
            'is_recording': False,  # This will be updated by the Flask app
            'sample_rate': self.sample_rate
        }
