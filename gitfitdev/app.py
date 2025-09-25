import os
import sys
import threading
import time as _time
import subprocess
import platform
import random
import math
import atexit
import socket
from datetime import datetime, timedelta, time
import logging

# Set up logging
log_dir = os.path.expanduser('~/.gitfitdev')
if not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(log_dir, 'debug.log'))
    ]
)

# Suppress Pillow's verbose import logging
logging.getLogger('PIL').setLevel(logging.WARNING)

# Windows-specific imports for mutex
if sys.platform.startswith("win"):
    import ctypes
    from ctypes import wintypes
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.GetLastError.restype = wintypes.DWORD
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    ERROR_ALREADY_EXISTS = 183


# --- Bootstrap optional dependencies (pystray, Pillow) ---
def _ensure_deps():
    need = []
    try:
        import pystray  # noqa: F401
    except Exception:
        need.append("pystray")
    try:
        from PIL import Image  # noqa: F401
    except Exception:
        need.append("Pillow")

    if not need:
        return

    try:
        print("Installing missing packages:", need)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", *need])
    except Exception as e:
        print("Auto-install failed:", e)
        # Continue; import will fail and we exit gracefully later


_ensure_deps()

try:
    import tkinter as tk
    from tkinter import messagebox
except Exception as e:
    print("Tkinter is required. Please install the Tk package for your OS.")
    raise

try:
    import pystray
    from PIL import Image, ImageDraw, ImageTk
except Exception:
    pystray = None
    Image = None
    ImageDraw = None
    ImageTk = None

from .config import load_settings, save_settings, Settings
from .branding import APP_NAME
from .tiny_lm import TinyPhraseLM
from .themes import get_theme, THEMES
from .toast import ToastNotification
from .trigger_utils import calculate_next_trigger_time
from .body_map import get_body_map, get_daily_report
from .body_map_window import BodyMapWindow
from .translations import get_translation, get_available_languages, get_language_display_name
from .version_checker import VersionChecker
from .disclaimer_text import get_disclaimer_text
from .version import __version__, __github_repo__, __github_api_releases__


class DisclaimerDialog:
    """Mandatory liability waiver dialog that must be accepted before app use"""

    def __init__(self, parent_root, on_accept, on_decline, language="en"):
        self.parent_root = parent_root
        self.on_accept = on_accept
        self.on_decline = on_decline
        self.accepted = False
        self.language = language

        # Create modal dialog
        self.dialog = tk.Toplevel(parent_root)
        self.dialog.title(get_translation("disclaimer_title", self.language))
        self.dialog.geometry("800x800")
        self.dialog.resizable(True, True)
        self.dialog.minsize(700, 600)
        self.dialog.transient(parent_root)
        self.dialog.grab_set()  # Modal

        # Center on screen
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (800 // 2)
        self.dialog.geometry(f"800x800+{x}+{y}")

        # Set icon
        try:
            icon_image = _dumbbell_icon(32)
            self.dialog.iconphoto(False, ImageTk.PhotoImage(icon_image))
        except Exception:
            pass

        # Handle closing with X button
        self.dialog.protocol("WM_DELETE_WINDOW", self.decline_disclaimer)

        self.create_content()

    def create_content(self):
        """Create the disclaimer content"""
        # Main container with proper grid layout
        main_frame = tk.Frame(self.dialog, bg="#2d3748")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Configure grid weights
        main_frame.grid_rowconfigure(1, weight=1)  # Text area row gets most space
        main_frame.grid_columnconfigure(0, weight=1)

        # Header
        header = tk.Label(main_frame,
                         text=get_translation("disclaimer_header", self.language),
                         font=("Segoe UI", 18, "bold"),
                         fg="#ff6b6b", bg="#2d3748")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        # Scrollable text area
        text_frame = tk.Frame(main_frame, bg="#2d3748")
        text_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.text_widget = tk.Text(text_frame,
                                  wrap=tk.WORD,
                                  yscrollcommand=scrollbar.set,
                                  font=("Segoe UI", 11),
                                  bg="#4a5568", fg="#e2e8f0",
                                  padx=15, pady=15,
                                  state=tk.DISABLED)
        self.text_widget.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=self.text_widget.yview)

        # Insert disclaimer text
        disclaimer_text = get_disclaimer_text(self.language)

        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, disclaimer_text)
        self.text_widget.config(state=tk.DISABLED)

        # Checkbox for confirmation
        self.read_var = tk.BooleanVar()
        checkbox_frame = tk.Frame(main_frame, bg="#2d3748")
        checkbox_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))

        self.checkbox = tk.Checkbutton(checkbox_frame,
                                      text=get_translation("disclaimer_checkbox", self.language),
                                      variable=self.read_var,
                                      command=self.update_button_state,
                                      font=("Segoe UI", 12, "bold"),
                                      fg="#68d391", bg="#2d3748",
                                      selectcolor="#4a5568")
        self.checkbox.pack()

        # Buttons
        button_frame = tk.Frame(main_frame, bg="#2d3748")
        button_frame.grid(row=3, column=0, sticky="ew")

        # Decline button
        self.decline_btn = tk.Button(button_frame,
                                    text=get_translation("disclaimer_decline", self.language),
                                    command=self.decline_disclaimer,
                                    font=("Segoe UI", 12, "bold"),
                                    bg="#e53e3e", fg="white",
                                    padx=20, pady=10,
                                    cursor="hand2")
        self.decline_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Accept button (initially disabled)
        self.accept_btn = tk.Button(button_frame,
                                   text=get_translation("disclaimer_accept", self.language),
                                   command=self.accept_disclaimer,
                                   font=("Segoe UI", 12, "bold"),
                                   bg="#48bb78", fg="white",
                                   padx=20, pady=10,
                                   cursor="hand2",
                                   state=tk.DISABLED)
        self.accept_btn.pack(side=tk.RIGHT)

    def update_button_state(self):
        """Enable accept button only when checkbox is checked"""
        if self.read_var.get():
            self.accept_btn.config(state=tk.NORMAL)
        else:
            self.accept_btn.config(state=tk.DISABLED)

    def accept_disclaimer(self):
        """Handle disclaimer acceptance"""
        if self.read_var.get():
            self.accepted = True
            self.dialog.destroy()
            if self.on_accept:
                self.on_accept()

    def decline_disclaimer(self):
        """Handle disclaimer decline"""
        self.accepted = False
        self.dialog.destroy()
        if self.on_decline:
            self.on_decline()

    def show(self):
        """Show the dialog and wait for user response"""
        self.dialog.deiconify()  # Make sure dialog is visible
        self.dialog.focus_force()
        self.dialog.lift()  # Bring to front
        self.dialog.wait_window()
        return self.accepted


# --- Icon generation ---
def _dumbbell_icon(size: int = 64) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Simple dumbbell: two squares + bar
    pad = size // 8
    bar_h = size // 6
    bar_y0 = size // 2 - bar_h // 2
    bar_y1 = bar_y0 + bar_h
    d.rounded_rectangle([pad, bar_y0, size - pad, bar_y1], radius=bar_h // 2, fill=(0, 150, 90, 255))
    plate_w = size // 5
    d.rounded_rectangle([pad - plate_w//2, bar_y0 - plate_w//3, pad + plate_w//2, bar_y1 + plate_w//3], radius=6, fill=(20, 200, 120, 255))
    d.rounded_rectangle([size - pad - plate_w//2, bar_y0 - plate_w//3, size - pad + plate_w//2, bar_y1 + plate_w//3], radius=6, fill=(20, 200, 120, 255))
    return img


# --- Overlay Window ---
class Overlay:
    def __init__(self, root: tk.Tk, message, seconds: int, dismiss_text: str, on_done, theme_id: str = "green", flash_mode: bool = False, count_break: bool = True, language: str = "en"):
        self.root = root
        self.seconds = max(1, int(seconds))
        self.remaining = self.seconds
        self.on_done = on_done
        self.extra_lines = []
        self.windows = []  # Store all overlay windows for multi-monitor
        self.dismiss_text = dismiss_text
        self.theme = get_theme(theme_id)
        self.flash_mode = flash_mode  # If true, show duration instead of countdown
        self.progress_bars = []  # Store progress bars for all windows
        self.countdown_labels = []  # Store countdown labels for color updates
        self.count_break = count_break  # Whether to count this as a real break
        self.start_time = _time.time()  # Track real start time for drift correction
        self.language = language  # Language for translations
        self.current_activity = None  # Track current activity (stretch/exercise)
        self.activity_switch_time = None  # When to switch activities

        # Handle both structured dict messages and legacy string messages
        if isinstance(message, dict):
            self.message_dict = message
            self.is_structured = True
        else:
            self.message_dict = {'title': message}
            self.is_structured = False

        # Determine activity type and timing
        self._setup_activity_timing()

        # Get all monitor dimensions
        monitors = self._get_all_monitors()

        # Record this as a real break if needed (only once per overlay)
        if self.count_break:
            from .tiny_lm import get_generator
            # Use the singleton generator's tracker
            self.generator = get_generator()
            self.tracker = self.generator.tracker
            # Note: break_shown is already recorded in generate_combined_message
            self.was_escaped = False  # Track if user escaped early

        # Create a fullscreen overlay on each monitor
        for i, (x, y, width, height) in enumerate(monitors):
            win = tk.Toplevel(root)
            win.title(APP_NAME)
            win.attributes("-topmost", True)
            win.overrideredirect(True)
            win.geometry(f"{width}x{height}+{x}+{y}")
            win.configure(bg=self.theme.background)

            if i == 0:  # Primary monitor gets focus
                win.focus_force()
                # REMOVED grab_set() - it locks the entire system!
                # win.grab_set()  # DO NOT USE - causes system lockout
                self.win = win  # Keep reference for compatibility

            self.windows.append(win)

        # Create UI elements on all windows
        if self.flash_mode:
            # In flash mode, show the total duration instead of countdown
            # Use overlay_seconds_left translation for countdown display
            duration_text = f"{self.seconds} {get_translation('overlay_seconds_left', self.language)}"
            self.count_var = tk.StringVar(value=duration_text)
        else:
            self.count_var = tk.StringVar(value=str(self.remaining))
        self.sub_msg_var = tk.StringVar(value="")

        # Get exercise emoji based on message
        if self.is_structured:
            self.exercise_emoji = self._get_exercise_emoji(
                self.message_dict.get('stretch_text', '') + ' ' +
                self.message_dict.get('exercise_text', '')
            )
        else:
            self.exercise_emoji = self._get_exercise_emoji(self.message_dict['title'])

        for win in self.windows:
            container = tk.Frame(win, bg=self.theme.background)
            container.pack(expand=True)

            if self.is_structured:
                # Title
                title = tk.Label(container, text=self.message_dict['title'],
                               font=("Segoe UI", 32, "bold"),
                               fg=self.theme.text_primary, bg=self.theme.background)
                title.pack(pady=(20, 30))

                # Check if this is a single activity or dual activity format
                if 'single_activity' in self.message_dict:
                    # Single activity format (for short breaks or user preference)
                    # Create a bordered frame for the activity
                    activity_border = tk.Frame(container, bg=self.theme.accent,
                                             highlightbackground=self.theme.accent,
                                             highlightthickness=2,
                                             bd=2)
                    activity_border.pack(pady=20, padx=40)

                    activity_frame = tk.Frame(activity_border, bg=self.theme.background)
                    activity_frame.pack(padx=20, pady=15)

                    activity_text = tk.Label(activity_frame,
                                           text=self.message_dict['single_activity'],
                                           font=("Segoe UI", 24),
                                           fg=self.theme.text_primary, bg=self.theme.background,
                                           wraplength=int(win.winfo_screenwidth() * 0.6))
                    activity_text.pack()
                else:
                    # Dual activity format (for longer breaks with "both" preference)
                    # Stretch section with border
                    stretch_border = tk.Frame(container, bg=self.theme.accent,
                                            highlightbackground=self.theme.accent,
                                            highlightthickness=2,
                                            bd=2)
                    stretch_border.pack(pady=10, padx=40)

                    stretch_frame = tk.Frame(stretch_border, bg=self.theme.background)
                    stretch_frame.pack(padx=15, pady=10)

                    stretch_header = tk.Label(stretch_frame,
                                            text=self.message_dict['stretch_header'],
                                            font=("Segoe UI", 24, "bold"),
                                            fg=self.theme.accent, bg=self.theme.background)
                    stretch_header.pack()

                    stretch_text = tk.Label(stretch_frame,
                                          text=self.message_dict['stretch_text'],
                                          font=("Segoe UI", 20),
                                          fg=self.theme.text_primary, bg=self.theme.background,
                                          wraplength=int(win.winfo_screenwidth() * 0.6))
                    stretch_text.pack(pady=(5, 0))

                    # Exercise section with border
                    exercise_border = tk.Frame(container, bg=self.theme.accent_secondary,
                                             highlightbackground=self.theme.accent_secondary,
                                             highlightthickness=2,
                                             bd=2)
                    exercise_border.pack(pady=10, padx=40)

                    exercise_frame = tk.Frame(exercise_border, bg=self.theme.background)
                    exercise_frame.pack(padx=15, pady=10)

                    exercise_header = tk.Label(exercise_frame,
                                             text=self.message_dict['exercise_header'],
                                             font=("Segoe UI", 24, "bold"),
                                             fg=self.theme.accent_secondary,
                                             bg=self.theme.background)
                    exercise_header.pack()

                    exercise_text = tk.Label(exercise_frame,
                                           text=self.message_dict['exercise_text'],
                                           font=("Segoe UI", 20),
                                           fg=self.theme.text_primary, bg=self.theme.background,
                                           wraplength=int(win.winfo_screenwidth() * 0.6))
                    exercise_text.pack(pady=(5, 0))

                # Motivation text
                motivation = tk.Label(container,
                                    text=self.message_dict['motivation'],
                                    font=("Segoe UI", 18, "italic"),
                                    fg=self.theme.text_secondary, bg=self.theme.background,
                                    wraplength=int(win.winfo_screenwidth() * 0.7))
                motivation.pack(pady=(15, 20))
            else:
                # Legacy single message display
                msg = tk.Label(container, text=self.message_dict['title'],
                             font=("Segoe UI", 28, "bold"),
                             fg=self.theme.text_primary, bg=self.theme.background,
                             wraplength=int(win.winfo_screenwidth() * 0.8))
                msg.pack(pady=20)

            # Add body map visualization
            try:
                # Create a frame for body map display
                body_frame = tk.Frame(container, bg=self.theme.background)
                body_frame.pack(pady=(10, 5))

                # Get body map visualization first to show in title
                from .body_map import get_body_visualization_data
                body_data = get_body_visualization_data()
                muscle_counts = body_data['muscle_work_counts']
                stats = body_data['coverage_stats']

                # Create progress title showing what's been accomplished
                exercises = stats.get('exercises_done', 0)
                stretches = stats.get('stretches_done', 0)
                breaks = stats.get('breaks_completed', 0)

                if breaks > 0:
                    # Show accomplishments
                    parts = []
                    break_word = get_translation("break" if breaks == 1 else "breaks", self.language)
                    parts.append(f"{breaks} {break_word}")

                    if exercises > 0:
                        exercise_word = get_translation("exercise" if exercises == 1 else "exercises", self.language)
                        parts.append(f"{exercises} {exercise_word}")

                    if stretches > 0:
                        stretch_word = get_translation("stretch" if stretches == 1 else "stretches", self.language)
                        parts.append(f"{stretches} {stretch_word}")

                    # Create progress text with translations
                    accomplished_text = get_translation("accomplished_today", self.language)
                    progress_text = f"{accomplished_text}: {', '.join(parts)}"
                else:
                    progress_text = get_translation("journey_begins", self.language)

                body_title = tk.Label(body_frame,
                                    text=progress_text,
                                    font=("Segoe UI", 16, "bold"),
                                    fg=self.theme.accent,
                                    bg=self.theme.background)
                body_title.pack()

                # Create visual muscle group display
                if muscle_counts:
                    # Sort by count
                    sorted_muscles = sorted(muscle_counts.items(), key=lambda x: x[1], reverse=True)

                    # Display top 5 worked muscles as mini bars
                    muscle_display = tk.Frame(body_frame, bg=self.theme.background)
                    muscle_display.pack(pady=5)

                    for muscle, count in sorted_muscles[:5]:
                        muscle_row = tk.Frame(muscle_display, bg=self.theme.background)
                        muscle_row.pack()

                        # Translate muscle name
                        muscle_key = f"muscle_{muscle.lower()}"
                        translated_name = get_translation(muscle_key, self.language)
                        # Fallback to formatted English name if no translation
                        if translated_name == muscle_key:
                            translated_name = muscle.replace('_', ' ').title()
                        name_label = tk.Label(muscle_row,
                                            text=f"{translated_name}:",
                                            font=("Segoe UI", 11),
                                            fg=self.theme.text_secondary,
                                            bg=self.theme.background,
                                            width=15,
                                            anchor='e')
                        name_label.pack(side=tk.LEFT, padx=(0, 5))

                        # Visual bar (using characters)
                        bar_length = min(count * 2, 20)
                        bar = '■' * bar_length
                        bar_label = tk.Label(muscle_row,
                                           text=f"{bar} ({count}x)",
                                           font=("Segoe UI", 11),
                                           fg=self.theme.accent_secondary,
                                           bg=self.theme.background,
                                           anchor='w')
                        bar_label.pack(side=tk.LEFT)

                # Status line removed for cleaner display

                # Add frequency recommendation if coverage is low
                from .body_map import BodyMapVisualizer
                from .config import load_settings
                visualizer = BodyMapVisualizer()
                settings = load_settings()
                recommendation = visualizer.get_frequency_recommendation(
                    stats['coverage_percentage'],
                    stats['total_breaks'],
                    settings.interval_minutes
                )

                if recommendation:
                    rec_label = tk.Label(container,
                                       text=recommendation,
                                       font=("Segoe UI", 12, "italic"),
                                       fg=self.theme.accent,
                                       bg=self.theme.background,
                                       wraplength=int(win.winfo_screenwidth() * 0.7))
                    rec_label.pack(pady=(0, 10))
            except Exception as e:
                # Silently fail if body map not available yet
                pass

            # Add exercise emoji icon
            emoji_label = tk.Label(container, text=self.exercise_emoji, font=("Segoe UI Emoji", 72),
                                  fg=self.theme.text_primary, bg=self.theme.background)
            emoji_label.pack(pady=10)

            # Adjust font size based on mode
            if self.flash_mode:
                count_font = ("Segoe UI", 48, "bold")
            else:
                count_font = ("Segoe UI", 72, "bold")

            count = tk.Label(container, textvariable=self.count_var, font=count_font,
                            fg=self._get_current_activity_color(), bg=self.theme.background)
            count.pack(pady=10)
            self.countdown_labels.append(count)  # Store for color updates

            # Add progress bar (only in non-flash mode)
            if not self.flash_mode:
                # Progress bar container
                progress_container = tk.Frame(container, bg=self.theme.background)
                progress_container.pack(pady=(10, 20))

                # Calculate width based on screen size
                bar_width = min(600, int(win.winfo_screenwidth() * 0.5))

                # Outer frame for progress bar (border)
                progress_outer = tk.Frame(progress_container,
                                        bg=self._darken_color(self.theme.background),
                                        height=30, width=bar_width)
                progress_outer.pack()
                progress_outer.pack_propagate(False)

                # Inner progress bar that will shrink
                progress_bar = tk.Frame(progress_outer,
                                       bg=self._get_current_activity_color(),
                                       height=28,
                                       width=bar_width - 2)
                progress_bar.place(x=1, y=1)

                # Store progress bar reference
                self.progress_bars.append(progress_bar)

                # Store initial width for calculations (use first window as reference)
                if len(self.progress_bars) == 1:
                    self.progress_width = bar_width - 2

            sub_msg = tk.Label(container, textvariable=self.sub_msg_var, font=("Segoe UI", 18),
                              fg=self.theme.text_secondary, bg=self.theme.background)
            sub_msg.pack(pady=10)

            # Add funny ESC instruction at the bottom
            esc_frame = tk.Frame(container, bg=self.theme.background)
            esc_frame.pack(pady=30)

            # Get funny ESC message
            esc_message = self._get_funny_esc_message()

            esc_label = tk.Label(
                esc_frame,
                text=esc_message,
                font=("Segoe UI", 14, "italic"),
                fg=self.theme.text_secondary,
                bg=self.theme.background,
                wraplength=int(win.winfo_screenwidth() * 0.6)
            )
            esc_label.pack(pady=10)

            # Add keyboard shortcuts for emergency exit - BIND GLOBALLY AND LOCALLY
            # bind_all makes it work even if window doesn't have focus
            win.bind_all("<Escape>", lambda e: self._dismiss_early())
            win.bind("<Escape>", lambda e: self._dismiss_early())

            # Alternative shortcuts
            win.bind_all("<Control-c>", lambda e: self._dismiss_early())
            win.bind_all("<Control-q>", lambda e: self._dismiss_early())
            win.bind_all("<Alt-F4>", lambda e: self._dismiss_early())

            # Make window focusable for ESC to work
            win.focus_set()
            win.focus_force()

            # Bindings to show reminder message (but don't lock input)
            win.bind("<Button-1>", self._on_user_input, add="+")
            win.bind("<Key>", self._on_user_input, add="+")  # Any key press
            # Removed FocusOut binding to avoid refocus loops

        # Start the countdown after 1 second to show the full duration first
        if self.windows:
            self.windows[0].after(1000, self._tick)

    def _darken_color(self, color: str) -> str:
        """Darken a hex color by 20%."""
        if color.startswith("#"):
            color = color[1:]
        if len(color) == 3:
            color = ''.join([c*2 for c in color])
        try:
            r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            r = max(0, int(r * 0.8))
            g = max(0, int(g * 0.8))
            b = max(0, int(b * 0.8))
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#2d3748"

    def _get_funny_esc_message(self) -> str:
        """Generate a funny ESC message."""
        import random

        # Get translated ESC completion messages
        completions = []
        for i in range(1, 13):  # We have 12 completion messages
            comp = get_translation(f"esc_completion_{i}", self.language)
            if comp and comp != f"esc_completion_{i}":  # Check if translation exists
                completions.append(comp)

        # Fallback to minimal hardcoded messages if no translations found
        if not completions:
            completions = [
                "you'll achieve peak couch potato status",
                "your muscles will file for unemployment"
            ]

        esc_msg = get_translation("press_esc_msg", self.language)
        completion = random.choice(completions)
        return f"{esc_msg} {completion}"

    def _get_exercise_emoji(self, message: str) -> str:
        """Return an emoji based on the exercise message."""
        msg_lower = message.lower()

        # Map keywords to emojis
        if any(word in msg_lower for word in ['stretch', 'yoga', 'bend']):
            return "🧘"
        elif any(word in msg_lower for word in ['walk', 'step', 'pace']):
            return "🚶"
        elif any(word in msg_lower for word in ['run', 'jog', 'sprint']):
            return "🏃"
        elif any(word in msg_lower for word in ['squat', 'lunge', 'leg']):
            return "🦵"
        elif any(word in msg_lower for word in ['push', 'pushup', 'press']):
            return "💪"
        elif any(word in msg_lower for word in ['jump', 'hop', 'leap']):
            return "🤸"
        elif any(word in msg_lower for word in ['dance', 'move', 'groove']):
            return "💃"
        elif any(word in msg_lower for word in ['arm', 'shoulder', 'rotate']):
            return "🤷"
        elif any(word in msg_lower for word in ['plank', 'core', 'abs']):
            return "🏋️"
        elif any(word in msg_lower for word in ['breathe', 'breath', 'inhale']):
            return "🫁"
        elif any(word in msg_lower for word in ['neck', 'head', 'roll']):
            return "🙆"
        elif any(word in msg_lower for word in ['sit', 'stand', 'posture']):
            return "🪑"
        else:
            # Default exercise emoji
            return "💪"

    def _setup_activity_timing(self):
        """Setup timing for activity transitions"""
        from .config import load_settings
        settings = load_settings()
        activity_type = getattr(settings, 'activity_type', 'both')

        if self.is_structured:
            # Check if this is dual activity mode (both stretch and exercise)
            if 'stretch_text' in self.message_dict and 'exercise_text' in self.message_dict:
                # Dual activity mode - split time based on preference
                if activity_type == 'both':
                    # Split time evenly between stretch and exercise
                    self.activity_switch_time = self.seconds // 2
                    self.current_activity = 'stretch'  # Start with stretch
                elif activity_type == 'stretch':
                    # Only stretching, even if exercise text exists
                    self.current_activity = 'stretch'
                    self.activity_switch_time = None
                else:  # exercise
                    # Only exercise, even if stretch text exists
                    self.current_activity = 'exercise'
                    self.activity_switch_time = None
            elif 'single_activity' in self.message_dict:
                # Single activity - determine if it's stretch or exercise
                # Check the title for hints
                title = self.message_dict.get('title', '').lower()
                if 'stretch' in title:
                    self.current_activity = 'stretch'
                else:
                    self.current_activity = 'exercise'
                self.activity_switch_time = None  # No switch needed
            else:
                self.current_activity = 'exercise'  # Default
                self.activity_switch_time = None
        else:
            self.current_activity = 'exercise'  # Default for unstructured
            self.activity_switch_time = None

    def _get_current_activity_color(self):
        """Get the appropriate color for current activity"""
        if self.current_activity == 'stretch':
            return self.theme.accent  # Primary accent for stretches
        else:
            return self.theme.accent_secondary  # Secondary accent for exercises

    def _get_all_monitors(self):
        """Get dimensions of all monitors."""
        monitors = []

        if sys.platform.startswith("win"):
            # Windows: Use ctypes to enumerate monitors
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32

            def enum_monitors_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
                rect = lprcMonitor.contents
                monitors.append((rect.left, rect.top,
                                rect.right - rect.left,
                                rect.bottom - rect.top))
                return 1

            MonitorEnumProc = ctypes.WINFUNCTYPE(
                ctypes.c_int, wintypes.HMONITOR, wintypes.HDC,
                ctypes.POINTER(wintypes.RECT), wintypes.LPARAM
            )

            callback = MonitorEnumProc(enum_monitors_proc)
            user32.EnumDisplayMonitors(None, None, callback, 0)

        # Fallback if no monitors found or on other platforms
        if not monitors:
            # Just use the primary screen
            monitors = [(0, 0, self.root.winfo_screenwidth(),
                        self.root.winfo_screenheight())]

        return monitors

    def _tick(self):
        # Calculate actual elapsed time to prevent drift
        now = _time.time()
        elapsed = now - self.start_time
        self.remaining = max(0, self.seconds - int(elapsed))

        # Check if we need to switch activities (for dual activity mode)
        if self.activity_switch_time and self.remaining <= self.activity_switch_time:
            if self.current_activity == 'stretch':
                # Switch to exercise
                self.current_activity = 'exercise'
                new_color = self._get_current_activity_color()

                # Update countdown color
                for label in self.countdown_labels:
                    try:
                        label.configure(fg=new_color)
                    except:
                        pass

                # Update progress bar color
                for bar in self.progress_bars:
                    try:
                        bar.configure(bg=new_color)
                    except:
                        pass

                # Prevent further switches
                self.activity_switch_time = None

        if not self.flash_mode:
            # Normal countdown mode - update display with new value
            self.count_var.set(str(self.remaining))

            # Update progress bars
            if hasattr(self, 'progress_bars') and hasattr(self, 'progress_width'):
                progress = self.remaining / self.seconds
                new_width = max(1, int(self.progress_width * progress))
                for bar in self.progress_bars:
                    try:
                        bar.configure(width=new_width)
                    except:
                        pass
        # In flash mode, the duration stays static

        if self.remaining <= 0:
            # Break completed normally - record as completed and activity
            if self.count_break and hasattr(self, 'tracker') and not getattr(self, 'was_escaped', False):
                self.tracker.record_break_completed()
                # Record the exercise or stretch that was done
                if hasattr(self, 'generator'):
                    self.generator.record_last_activity_completion()
            # Clean up all windows
            for win in self.windows:
                try:
                    # No need to release grab since we don't use it anymore
                    win.destroy()
                except Exception:
                    pass
            if self.on_done:
                self.on_done()
            return

        # Schedule next tick with drift correction
        if self.windows:  # Check if windows still exist
            # Calculate when the next tick should occur
            next_tick = self.start_time + (self.seconds - self.remaining + 1)
            delay = max(50, int((next_tick - now) * 1000))
            self.windows[0].after(delay, self._tick)

    def _on_user_input(self, event=None):
        # Show a fun reminder about trying to escape
        import random

        # Get translated keyboard messages
        escape_attempts = []
        for i in range(1, 31):  # We have 30 messages
            msg = get_translation(f"keypress_msg_{i}", self.language)
            if msg and msg != f"keypress_msg_{i}":  # Check if translation exists
                escape_attempts.append(msg)

        # Fallback to hardcoded messages if no translations found
        if not escape_attempts:
            escape_attempts = [
                "Nice try, but your spine already filed a complaint.",
                "Nice try, but escape isn't in your exercise routine."
            ]

        if not self.extra_lines:
            self.sub_msg_var.set(random.choice(escape_attempts))
            self.extra_lines.append(True)  # Just track that we showed a message
        # Don't refocus - it can cause problems

    def _refocus(self, event=None):
        try:
            self.win.attributes("-topmost", True)
            self.win.focus_force()
            self.win.lift()
        except Exception:
            pass

    def _dismiss_early(self):
        """Allow user to dismiss the overlay early - SAFELY."""
        # Mark as escaped if this is a counted break
        if self.count_break and hasattr(self, 'tracker'):
            self.tracker.record_break_escaped()
            self.was_escaped = True

        # Stop the timer to prevent further ticks
        self.remaining = 0

        # Clean up all windows immediately
        for win in self.windows:
            try:
                # No grab to release since we don't use it
                win.destroy()
            except Exception:
                pass

        # Clear the windows list
        self.windows = []

        if self.on_done:
            self.on_done()


# --- Settings UI ---
class SettingsWindow:
    def __init__(self, root: tk.Tk, settings: Settings, on_save, get_autostart_state=None, set_autostart_state=None):
        self.root = root
        self.settings = settings
        self.language = settings.language  # Store language for translations
        self.on_save = on_save
        self._get_autostart_state = get_autostart_state
        self._set_autostart_state = set_autostart_state
        self.win = tk.Toplevel(root)
        self.win.title(get_translation("settings_title", settings.language))
        self.win.geometry("540x850")  # Increased height for summary and all content
        self.win.resizable(True, True)
        self.win.minsize(520, 750)  # Set minimum size to ensure content is visible

        # Set window icon
        try:
            icon_image = _dumbbell_icon(32)
            self.win.iconphoto(False, ImageTk.PhotoImage(icon_image))
        except Exception:
            pass  # Fallback to default icon if there's an issue

        # Add window close handler
        self.win.protocol("WM_DELETE_WINDOW", self._on_close)
        self._is_open = True


        # Apply theme to settings window
        from .themes import THEMES
        self.theme = THEMES.get(settings.theme, THEMES["dark"])
        self.win.configure(bg=self.theme.background)

        def create_category_frame(parent, title, icon=""):
            """Create a framed category section with compact spacing."""
            # Outer frame with border effect
            outer_frame = tk.Frame(parent, bg=self._darken_color(self.theme.background), relief="flat")
            outer_frame.pack(fill="x", pady=(0, 8), padx=2)

            # Inner frame
            inner_frame = tk.Frame(outer_frame, bg=self.theme.background)
            inner_frame.pack(fill="both", expand=True, padx=1, pady=1)

            # Header (more compact)
            header = tk.Frame(inner_frame, bg=self._darken_color(self.theme.background), height=28)
            header.pack(fill="x")
            header.pack_propagate(False)

            # Title with icon
            title_container = tk.Frame(header, bg=self._darken_color(self.theme.background))
            title_container.pack(side="left", padx=10, pady=4)

            if icon:
                tk.Label(title_container, text=icon, font=("Segoe UI Emoji", 11),
                        bg=self._darken_color(self.theme.background),
                        fg=self.theme.accent).pack(side="left", padx=(0, 6))

            tk.Label(title_container, text=title, font=("Segoe UI", 10, "bold"),
                    bg=self._darken_color(self.theme.background),
                    fg=self.theme.text_primary).pack(side="left")

            # Content area (reduced padding)
            content = tk.Frame(inner_frame, bg=self.theme.background)
            content.pack(fill="both", expand=True, padx=10, pady=8)

            return content

        def add_row(parent, r, label):
            lbl = tk.Label(parent, text=label, bg=self.theme.background, fg=self.theme.text_primary,
                          font=("Segoe UI", 9), width=16, anchor="e")
            lbl.grid(row=r, column=0, sticky="e", padx=(0, 10), pady=3)

        # Create scrollable frame for main content
        # Canvas for scrolling
        canvas = tk.Canvas(self.win, bg=self.theme.background, highlightthickness=0)
        scrollbar = tk.Scrollbar(self.win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.theme.background)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Update canvas window width when canvas size changes
        def configure_canvas(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)

        canvas.bind('<Configure>', configure_canvas)

        # Add mouse wheel scrolling support
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 2), pady=10)

        # Main content frame (now inside scrollable frame)
        frm = scrollable_frame

        # Title header (more compact)
        title_frame = tk.Frame(frm, bg=self.theme.background)
        title_frame.pack(fill="x", pady=(0, 10))

        title_inner = tk.Frame(title_frame, bg=self.theme.background)
        title_inner.pack()

        tk.Label(title_inner, text="⚙️", font=("Segoe UI Emoji", 22),
                bg=self.theme.background, fg=self.theme.accent).pack(side="left", padx=(0, 8))
        tk.Label(title_inner, text=get_translation("settings_title", self.language), font=("Segoe UI", 16, "bold"),
                bg=self.theme.background, fg=self.theme.text_primary).pack(side="left")

        # Settings summary line (will be styled after _darken_color is defined)
        summary_frame = tk.Frame(frm, bg=self.theme.background)
        summary_frame.pack(fill="x", pady=(0, 8), padx=2)

        summary_inner = tk.Frame(summary_frame, bg=self.theme.background)
        summary_inner.pack(fill="both", expand=True, padx=1, pady=1)

        self.summary_label = tk.Label(
            summary_inner,
            text="",
            font=("Segoe UI", 9),
            fg=self.theme.accent,
            bg=self.theme.background,
            wraplength=520,
            justify="center"
        )
        self.summary_label.pack(pady=5)

        # Helper functions
        def _darken_color(color: str) -> str:
            """Darken a hex color by 20%."""
            if color.startswith("#"):
                color = color[1:]
            if len(color) == 3:
                color = ''.join([c*2 for c in color])
            try:
                r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
                r = max(0, int(r * 0.8))
                g = max(0, int(g * 0.8))
                b = max(0, int(b * 0.8))
                return f"#{r:02x}{g:02x}{b:02x}"
            except:
                return "#2d3748"

        self._darken_color = _darken_color

        # Now style the summary frame with the darkened color
        summary_frame.config(bg=self._darken_color(self.theme.background))

        def create_entry(parent, textvariable, width=10):
            entry_bg = self._darken_color(self.theme.background) if self.theme.name == "Dark Mode" else "#ffffff"
            entry_fg = self.theme.text_primary
            entry = tk.Entry(parent, textvariable=textvariable, width=width,
                           bg=entry_bg, fg=entry_fg, insertbackground=entry_fg,
                           font=("Segoe UI", 10), relief="flat", bd=1)
            return entry

        # ========== TIME SETTINGS CATEGORY ==========
        time_category = create_category_frame(frm, get_translation("category_schedule", self.language), "🕐")

        # Time format toggle
        add_row(time_category, 0, get_translation("label_time_format", self.language))
        time_format_frame = tk.Frame(time_category, bg=self.theme.background)
        time_format_frame.grid(row=0, column=1, sticky="w")

        self.time_format_var = tk.BooleanVar(value=settings.time_format_24h)

        tk.Radiobutton(
            time_format_frame,
            text=get_translation("settings_24h", self.language),
            variable=self.time_format_var,
            value=True,
            bg=self.theme.background,
            fg=self.theme.text_primary,
            selectcolor=self._darken_color(self.theme.background),
            activebackground=self.theme.background
        ).pack(side="left")

        tk.Radiobutton(
            time_format_frame,
            text=get_translation("settings_12h", self.language),
            variable=self.time_format_var,
            value=False,
            bg=self.theme.background,
            fg=self.theme.text_primary,
            selectcolor=self._darken_color(self.theme.background),
            activebackground=self.theme.background
        ).pack(side="left", padx=(10, 0))

        # Parse initial times for 12-hour format
        def parse_time_for_display(time_24):
            """Parse 24-hour time string and return hour, minute, period for 12-hour format"""
            h, m = map(int, time_24.split(':'))
            period = "AM" if h < 12 else "PM"
            h_12 = h % 12 if h % 12 != 0 else 12
            return h_12, m, period

        # Active From
        add_row(time_category, 1, get_translation("label_from", self.language))
        from_frame = tk.Frame(time_category, bg=self.theme.background)
        from_frame.grid(row=1, column=1, sticky="w")

        # Store the 24-hour value internally
        self.from_var = tk.StringVar(value=settings.active_from)

        # Import ttk for dropdowns
        from tkinter import ttk

        # Parse initial values
        from_h12, from_m, from_period = parse_time_for_display(settings.active_from)
        from_h24, from_m24 = map(int, settings.active_from.split(':'))

        # Variables for both formats
        self.from_hour_var = tk.StringVar(value=str(from_h12))
        self.from_min_var = tk.StringVar(value=f"{from_m:02d}")
        self.from_period_var = tk.StringVar(value=from_period)

        # 24-hour variables
        self.from_hour_24_var = tk.StringVar(value=f"{from_h24:02d}")
        self.from_min_24_var = tk.StringVar(value=f"{from_m24:02d}")

        # 24-hour dropdowns
        # Hour dropdown (00-23)
        self.from_hour_24_combo = ttk.Combobox(from_frame, textvariable=self.from_hour_24_var,
                                               values=[f"{i:02d}" for i in range(24)],
                                               state="readonly", width=3)

        self.from_colon_24 = tk.Label(from_frame, text=":", font=("Segoe UI", 10),
                                      fg=self.theme.text_primary, bg=self.theme.background)

        # Minute dropdown (00-59) in 5-minute intervals
        minute_values = [f"{i:02d}" for i in range(0, 60, 5)]  # 5-minute intervals
        self.from_min_24_combo = ttk.Combobox(from_frame, textvariable=self.from_min_24_var,
                                              values=minute_values, width=3)

        # 12-hour dropdowns
        # Hour dropdown (1-12)
        self.from_hour_combo = ttk.Combobox(from_frame, textvariable=self.from_hour_var,
                                            values=[str(i) for i in range(1, 13)],
                                            state="readonly", width=3)

        self.from_colon = tk.Label(from_frame, text=":", font=("Segoe UI", 10),
                                   fg=self.theme.text_primary, bg=self.theme.background)

        # Minute dropdown (00-59)
        self.from_min_combo = ttk.Combobox(from_frame, textvariable=self.from_min_var,
                                           values=minute_values, width=3)

        # AM/PM dropdown
        self.from_period_combo = ttk.Combobox(from_frame, textvariable=self.from_period_var,
                                              values=["AM", "PM"], state="readonly", width=4)

        # Active To
        add_row(time_category, 2, get_translation("label_to", self.language))
        to_frame = tk.Frame(time_category, bg=self.theme.background)
        to_frame.grid(row=2, column=1, sticky="w")

        # Store the 24-hour value internally
        self.to_var = tk.StringVar(value=settings.active_to)

        # Parse initial values
        to_h12, to_m, to_period = parse_time_for_display(settings.active_to)
        to_h24, to_m24 = map(int, settings.active_to.split(':'))

        # Variables for both formats
        self.to_hour_var = tk.StringVar(value=str(to_h12))
        self.to_min_var = tk.StringVar(value=f"{to_m:02d}")
        self.to_period_var = tk.StringVar(value=to_period)

        # 24-hour variables
        self.to_hour_24_var = tk.StringVar(value=f"{to_h24:02d}")
        self.to_min_24_var = tk.StringVar(value=f"{to_m24:02d}")

        # 24-hour dropdowns
        # Hour dropdown (00-23)
        self.to_hour_24_combo = ttk.Combobox(to_frame, textvariable=self.to_hour_24_var,
                                             values=[f"{i:02d}" for i in range(24)],
                                             state="readonly", width=3)

        self.to_colon_24 = tk.Label(to_frame, text=":", font=("Segoe UI", 10),
                                    fg=self.theme.text_primary, bg=self.theme.background)

        # Minute dropdown (00-59)
        self.to_min_24_combo = ttk.Combobox(to_frame, textvariable=self.to_min_24_var,
                                            values=minute_values, width=3)

        # 12-hour dropdowns
        # Hour dropdown (1-12)
        self.to_hour_combo = ttk.Combobox(to_frame, textvariable=self.to_hour_var,
                                          values=[str(i) for i in range(1, 13)],
                                          state="readonly", width=3)

        self.to_colon = tk.Label(to_frame, text=":", font=("Segoe UI", 10),
                                 fg=self.theme.text_primary, bg=self.theme.background)

        # Minute dropdown (00-59)
        self.to_min_combo = ttk.Combobox(to_frame, textvariable=self.to_min_var,
                                         values=minute_values, width=3)

        # AM/PM dropdown
        self.to_period_combo = ttk.Combobox(to_frame, textvariable=self.to_period_var,
                                           values=["AM", "PM"], state="readonly", width=4)

        # Flags to prevent infinite update loops
        self._updating_from = False
        self._updating_to = False

        # Function to update from_var when 24-hour dropdowns change
        def update_from_24(*args):
            if self._updating_from:
                return
            try:
                self._updating_from = True
                hour = int(self.from_hour_24_var.get())
                minute = int(self.from_min_24_var.get())
                self.from_var.set(f"{hour:02d}:{minute:02d}")

                # Also update 12-hour values
                h12, m, period = parse_time_for_display(f"{hour:02d}:{minute:02d}")
                self.from_hour_var.set(str(h12))
                self.from_min_var.set(f"{m:02d}")
                self.from_period_var.set(period)
                self._updating_from = False
            except:
                self._updating_from = False

        def update_to_24(*args):
            if self._updating_to:
                return
            try:
                self._updating_to = True
                hour = int(self.to_hour_24_var.get())
                minute = int(self.to_min_24_var.get())
                self.to_var.set(f"{hour:02d}:{minute:02d}")

                # Also update 12-hour values
                h12, m, period = parse_time_for_display(f"{hour:02d}:{minute:02d}")
                self.to_hour_var.set(str(h12))
                self.to_min_var.set(f"{m:02d}")
                self.to_period_var.set(period)
                self._updating_to = False
            except:
                self._updating_to = False

        # Function to convert 12-hour to 24-hour
        def update_24_from_12(which):
            if which == "from" and self._updating_from:
                return
            if which == "to" and self._updating_to:
                return
            try:
                if which == "from":
                    self._updating_from = True
                    hour = int(self.from_hour_var.get())
                    minute = int(self.from_min_var.get())
                    period = self.from_period_var.get()

                    # Convert to 24-hour
                    if period == "AM":
                        h24 = 0 if hour == 12 else hour
                    else:  # PM
                        h24 = 12 if hour == 12 else hour + 12

                    self.from_var.set(f"{h24:02d}:{minute:02d}")
                    self.from_hour_24_var.set(f"{h24:02d}")
                    self.from_min_24_var.set(f"{minute:02d}")
                    self._updating_from = False
                else:  # "to"
                    self._updating_to = True
                    hour = int(self.to_hour_var.get())
                    minute = int(self.to_min_var.get())
                    period = self.to_period_var.get()

                    # Convert to 24-hour
                    if period == "AM":
                        h24 = 0 if hour == 12 else hour
                    else:  # PM
                        h24 = 12 if hour == 12 else hour + 12

                    self.to_var.set(f"{h24:02d}:{minute:02d}")
                    self.to_hour_24_var.set(f"{h24:02d}")
                    self.to_min_24_var.set(f"{minute:02d}")
                    self._updating_to = False
            except:
                self._updating_from = False
                self._updating_to = False

        # Function to update time display
        def update_time_labels(*args):
            is_24_hour = self.time_format_var.get()

            # Show/hide appropriate widgets for From
            if is_24_hour:
                # Hide 12-hour widgets
                self.from_hour_combo.pack_forget()
                self.from_colon.pack_forget()
                self.from_min_combo.pack_forget()
                self.from_period_combo.pack_forget()
                # Show 24-hour widgets
                self.from_hour_24_combo.pack(side="left")
                self.from_colon_24.pack(side="left", padx=1)
                self.from_min_24_combo.pack(side="left")
            else:
                # Hide 24-hour widgets
                self.from_hour_24_combo.pack_forget()
                self.from_colon_24.pack_forget()
                self.from_min_24_combo.pack_forget()
                # Show 12-hour widgets
                self.from_hour_combo.pack(side="left")
                self.from_colon.pack(side="left", padx=1)
                self.from_min_combo.pack(side="left")
                self.from_period_combo.pack(side="left", padx=(5, 0))

            # Show/hide appropriate widgets for To
            if is_24_hour:
                # Hide 12-hour widgets
                self.to_hour_combo.pack_forget()
                self.to_colon.pack_forget()
                self.to_min_combo.pack_forget()
                self.to_period_combo.pack_forget()
                # Show 24-hour widgets
                self.to_hour_24_combo.pack(side="left")
                self.to_colon_24.pack(side="left", padx=1)
                self.to_min_24_combo.pack(side="left")
            else:
                # Hide 24-hour widgets
                self.to_hour_24_combo.pack_forget()
                self.to_colon_24.pack_forget()
                self.to_min_24_combo.pack_forget()
                # Show 12-hour widgets
                self.to_hour_combo.pack(side="left")
                self.to_colon.pack(side="left", padx=1)
                self.to_min_combo.pack(side="left")
                self.to_period_combo.pack(side="left", padx=(5, 0))

        # Set up traces for 24-hour dropdowns
        self.from_hour_24_var.trace("w", update_from_24)
        self.from_min_24_var.trace("w", update_from_24)
        self.to_hour_24_var.trace("w", update_to_24)
        self.to_min_24_var.trace("w", update_to_24)

        # Set up traces for 12-hour inputs
        self.from_hour_var.trace("w", lambda *args: update_24_from_12("from"))
        self.from_min_var.trace("w", lambda *args: update_24_from_12("from"))
        self.from_period_var.trace("w", lambda *args: update_24_from_12("from"))

        self.to_hour_var.trace("w", lambda *args: update_24_from_12("to"))
        self.to_min_var.trace("w", lambda *args: update_24_from_12("to"))
        self.to_period_var.trace("w", lambda *args: update_24_from_12("to"))

        # ========== BREAK SETTINGS CATEGORY ==========
        break_category = create_category_frame(frm, get_translation("category_break_settings", self.language), "💪")

        add_row(break_category, 0, get_translation("label_interval", self.language))
        interval_frame = tk.Frame(break_category, bg=self.theme.background)
        interval_frame.grid(row=0, column=1, sticky="w")

        self.int_var = tk.StringVar(value=str(settings.interval_minutes))

        # Create dropdown for interval minutes with smart, organized values
        # Values that work well with hourly scheduling
        interval_values = [
            "5",    # Every 5 minutes (12 times per hour)
            "10",   # Every 10 minutes (6 times per hour)
            "15",   # Every 15 minutes (4 times per hour)
            "20",   # Every 20 minutes (3 times per hour)
            "25",   # Every 25 minutes
            "30",   # Every 30 minutes (2 times per hour)
            "45",   # Every 45 minutes
            "60",   # Every hour
            "90",   # Every 1.5 hours
            "120",  # Every 2 hours
        ]
        self.interval_combo = ttk.Combobox(interval_frame, textvariable=self.int_var,
                                           values=interval_values, state="readonly", width=8)
        self.interval_combo.pack(side="left")

        self.interval_label = tk.Label(interval_frame, text="",
                font=("Segoe UI", 9),
                fg=self.theme.text_secondary,
                bg=self.theme.background)
        self.interval_label.pack(side="left", padx=(5, 0))

        # Function to update interval label with helpful text
        def update_interval_label(*args):
            try:
                interval = int(self.int_var.get())

                # Validate interval range
                if interval < 5:
                    self.interval_label.config(text=get_translation("interval_invalid", self.language), fg="#ff6b6b")
                    self.int_var.set("5")  # Force to minimum
                    return
                elif interval > 480:  # More than 8 hours
                    self.interval_label.config(text=get_translation("interval_invalid", self.language), fg="#ff6b6b")
                    self.int_var.set("120")  # Force to 2 hours
                    return

                # Reset color for valid values
                self.interval_label.config(fg=self.theme.text_secondary)

                if interval < 60:
                    if 60 % interval == 0:
                        times_per_hour = 60 // interval
                        # For sub-hourly intervals that divide evenly into 60
                        if times_per_hour == 1:
                            label_text = get_translation("interval_every_hour", self.language)
                        else:
                            label_text = get_translation("interval_every_min", self.language).format(minutes=interval)
                    else:
                        label_text = get_translation("interval_every_min", self.language).format(minutes=interval)
                elif interval == 60:
                    label_text = get_translation("interval_every_hour", self.language)
                elif interval == 90:
                    label_text = get_translation("interval_every_h_m", self.language).format(hours=1, minutes=30)
                elif interval == 120:
                    label_text = get_translation("interval_every_hours", self.language).format(hours=2)
                elif interval % 60 == 0:
                    hours = interval // 60
                    label_text = get_translation("interval_every_hours", self.language).format(hours=hours)
                else:
                    hours = interval // 60
                    mins = interval % 60
                    if hours > 0:
                        label_text = get_translation("interval_every_h_m", self.language).format(hours=hours, minutes=mins)
                    else:
                        label_text = get_translation("interval_every_min", self.language).format(minutes=interval)

                self.interval_label.config(text=label_text)

                # Also trigger update of break minute options if it's defined
                if 'update_trigger_options' in locals():
                    update_trigger_options()

            except ValueError:
                self.interval_label.config(text=get_translation("interval_invalid", self.language), fg="#ff6b6b")

        # Bind the update function
        self.int_var.trace("w", update_interval_label)

        # Initialize label
        update_interval_label()

        add_row(break_category, 1, get_translation("label_break_offset", self.language))
        trigger_frame = tk.Frame(break_category, bg=self.theme.background)
        trigger_frame.grid(row=1, column=1, sticky="w")

        self.trigger_var = tk.StringVar(value=str(settings.trigger_at_minute))

        # Create dropdown for trigger minute
        self.trigger_combo = ttk.Combobox(trigger_frame, textvariable=self.trigger_var,
                                          state="readonly", width=6)
        self.trigger_combo.pack(side="left")

        self.trigger_label = tk.Label(
            trigger_frame,
            text="",
            font=("Segoe UI", 9),
            fg=self.theme.text_secondary,
            bg=self.theme.background
        )
        self.trigger_label.pack(side="left", padx=(5, 0))

        # Function to update trigger minute options based on interval
        def update_trigger_options(*args):
            try:
                interval = int(self.int_var.get())

                # For small intervals, show minute WITHIN the interval period
                # For large intervals (60+), show absolute minute of the hour
                if interval < 60:
                    # Show minutes 0 to (interval-1)
                    # This represents which minute within each interval period to trigger
                    options = [str(i) for i in range(min(interval, 60))]

                    if interval == 5:
                        hint_text = get_translation("trigger_hint_5min", self.language)
                    elif interval == 10:
                        hint_text = get_translation("trigger_hint_10min", self.language)
                    elif interval == 15:
                        hint_text = get_translation("trigger_hint_15min", self.language)
                    elif interval == 20:
                        hint_text = get_translation("trigger_hint_20min", self.language)
                    elif interval == 25:
                        hint_text = get_translation("trigger_hint_25min", self.language)
                    elif interval == 30:
                        hint_text = get_translation("trigger_hint_30min", self.language)
                    elif interval == 45:
                        hint_text = get_translation("trigger_hint_45min", self.language)
                    else:
                        hint_text = get_translation("trigger_hint_generic", self.language).format(max=interval-1, interval=interval)
                else:
                    # For hourly+ intervals, show absolute minute of hour (0-59)
                    options = [str(i) for i in range(60)]
                    hint_text = get_translation("trigger_hint_minute_hour", self.language)

                # Update dropdown options
                self.trigger_combo['values'] = options

                # Update hint label
                self.trigger_label.config(text=hint_text)

                # If current value is not in options, set to first option
                current_value = self.trigger_var.get()
                if current_value not in options:
                    self.trigger_var.set(options[0])

            except ValueError:
                # If interval is not a valid number, default to minute 0
                self.trigger_combo['values'] = ["0"]
                self.trigger_label.config(text="")
                self.trigger_var.set("0")

        # Bind the update function to interval changes
        self.int_var.trace("w", update_trigger_options)

        # Initialize trigger options
        update_trigger_options()

        # Preview of next breaks - put on a new row below
        preview_row = tk.Frame(break_category, bg=self.theme.background)
        preview_row.grid(row=2, column=0, columnspan=3, sticky="w", pady=(3, 5))

        tk.Label(
            preview_row,
            text=get_translation("preview_label", self.language),
            font=("Segoe UI", 9, "bold"),
            fg=self.theme.text_primary,
            bg=self.theme.background
        ).pack(side="left", padx=(70, 5))

        self.preview_label = tk.Label(
            preview_row,
            text="",
            font=("Segoe UI", 9),
            fg=self.theme.accent,
            bg=self.theme.background,
            justify="left"
        )
        self.preview_label.pack(side="left")

        # Update preview when values change
        def update_preview(*args):
            try:
                from .trigger_utils import get_trigger_times_preview
                interval = int(self.int_var.get())
                minute = int(self.trigger_var.get())
                from_hour = int(self.from_var.get().split(":")[0])

                # For intervals < 60, minute represents offset within interval
                # We need to calculate actual clock minutes
                if interval < 60:
                    # Calculate actual trigger minutes based on offset
                    actual_minutes = []
                    for period_start in range(0, 60, interval):
                        actual_minute = (period_start + minute) % 60
                        if actual_minute not in actual_minutes:
                            actual_minutes.append(actual_minute)
                    # Use the first actual minute for preview
                    minute_for_preview = actual_minutes[0] if actual_minutes else 0
                else:
                    minute_for_preview = minute

                # Get preview times
                times = get_trigger_times_preview(interval, minute_for_preview, from_hour, 5)

                # Format based on time format setting
                if self.time_format_var.get():
                    formatted_times = times[:4]
                else:
                    # Convert to 12-hour format
                    formatted_times = []
                    for t in times[:4]:
                        h, m = map(int, t.split(":"))
                        period = "AM" if h < 12 else "PM"
                        h_12 = h % 12 if h % 12 != 0 else 12
                        formatted_times.append(f"{h_12}:{m:02d}{period}")

                preview_text = ", ".join(formatted_times)
                if len(times) > 4:
                    preview_text += "..."

                self.preview_label.config(text=preview_text)
            except:
                self.preview_label.config(text="")

        self.int_var.trace("w", update_preview)
        self.trigger_var.trace("w", update_preview)
        self.from_var.trace("w", update_preview)

        # Set up traces for time format changes
        self.time_format_var.trace("w", update_preview)
        self.time_format_var.trace("w", update_time_labels)
        # Initial display setup
        update_time_labels()

        add_row(break_category, 3, get_translation("label_lock_duration", self.language))
        lock_frame = tk.Frame(break_category, bg=self.theme.background)
        lock_frame.grid(row=3, column=1, sticky="w")

        # Ensure lock duration is within valid range (30-180 seconds)
        lock_duration = max(30, min(180, settings.lock_seconds))
        self.lock_var = tk.StringVar(value=str(lock_duration))

        # Dropdown for lock duration: 30 seconds to 3 minutes
        lock_values = ["30", "45", "60", "90", "120", "150", "180"]
        self.lock_combo = ttk.Combobox(lock_frame, textvariable=self.lock_var,
                                       values=lock_values, width=8)
        self.lock_combo.pack(side="left")

        lock_label = tk.Label(lock_frame, text=get_translation("label_time_for_exercise", self.language),
                             font=("Segoe UI", 9),
                             fg=self.theme.text_secondary,
                             bg=self.theme.background)
        lock_label.pack(side="left")

        add_row(break_category, 4, get_translation("label_activity_type", self.language))
        activity_frame = tk.Frame(break_category, bg=self.theme.background)
        activity_frame.grid(row=4, column=1, sticky="w")

        self.activity_var = tk.StringVar(value=getattr(settings, 'activity_type', 'both'))

        # Store activity values and combo for dynamic updates
        self.activity_values_full = [
            ("both", get_translation("activity_both", self.language)),
            ("stretch", get_translation("activity_stretch", self.language)),
            ("exercise", get_translation("activity_exercise", self.language))
        ]
        self.activity_values_limited = [
            ("stretch", get_translation("activity_stretch", self.language)),
            ("exercise", get_translation("activity_exercise", self.language))
        ]

        self.activity_combo = ttk.Combobox(activity_frame, textvariable=self.activity_var,
                                          width=25, state="readonly")
        self.activity_combo.pack(side="left")

        # Function to update Activity Type options based on lock duration
        def update_activity_options(*args):
            try:
                duration = int(self.lock_var.get())
                current_activity = self.activity_var.get()

                if duration < 60:
                    # Less than 1 minute: only stretch or exercise
                    values = self.activity_values_limited
                    # If current selection is "both", change to "stretch"
                    if current_activity == get_translation("activity_both", self.language):
                        self.activity_var.set(get_translation("activity_stretch", self.language))
                else:
                    # 1 minute or more: all options available
                    values = self.activity_values_full

                # Update combobox values
                self.activity_combo['values'] = [desc for val, desc in values]
            except ValueError:
                # If invalid duration, default to full options
                self.activity_combo['values'] = [desc for val, desc in self.activity_values_full]

        # Bind the update function to lock duration changes
        self.lock_var.trace("w", update_activity_options)

        # Set initial display value
        current_val = getattr(settings, 'activity_type', 'both')
        for val, desc in self.activity_values_full:
            if val == current_val:
                self.activity_var.set(desc)
                break

        # Initialize activity options based on current lock duration
        update_activity_options()

        add_row(break_category, 5, get_translation("label_exercise_position", self.language))
        position_frame = tk.Frame(break_category, bg=self.theme.background)
        position_frame.grid(row=5, column=1, sticky="w")

        self.position_var = tk.StringVar(value=getattr(settings, 'position_preference', 'sitting_standing'))
        position_values = [
            ("sitting_standing", get_translation("position_sitting_standing", self.language)),
            ("all", get_translation("position_all", self.language)),
            ("sitting", get_translation("position_sitting", self.language)),
            ("standing", get_translation("position_standing", self.language)),
            ("lying", get_translation("position_lying", self.language))
        ]

        position_combo = ttk.Combobox(position_frame, textvariable=self.position_var,
                                     values=[desc for val, desc in position_values],
                                     width=25, state="readonly")
        position_combo.pack(side="left")

        # Set the display value
        current_pos = getattr(settings, 'position_preference', 'sitting_standing')
        for val, desc in position_values:
            if val == current_pos:
                self.position_var.set(desc)
                break


        # ========== SYSTEM SETTINGS CATEGORY ==========
        system_category = create_category_frame(frm, get_translation("category_system", self.language), "⚙️")

        add_row(system_category, 0, get_translation("label_start_on_login", self.language))
        current_auto = settings.start_on_login
        if callable(self._get_autostart_state):
            try:
                current_auto = bool(self._get_autostart_state())
            except Exception:
                pass
        self.auto_var = tk.BooleanVar(value=current_auto)
        tk.Checkbutton(system_category, variable=self.auto_var, bg=self.theme.background).grid(row=0, column=1, sticky="w")

        # ========== APPEARANCE CATEGORY ==========
        appearance_category = create_category_frame(frm, get_translation("category_appearance", self.language), "🎨")

        # Theme selection
        add_row(appearance_category, 0, get_translation("label_color_theme", self.language))
        theme_frame = tk.Frame(appearance_category, bg=self.theme.background)
        theme_frame.grid(row=0, column=1, sticky="w")
        self.theme_var = tk.StringVar(value=settings.theme)

        # Create theme dropdown
        from tkinter import ttk
        theme_choices = [(get_translation(f"theme_{theme_id}", self.language), theme_id) for theme_id, theme in THEMES.items()]
        theme_dropdown = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=[name for name, _ in theme_choices],
            state="readonly",
            width=18
        )

        # Set current theme display name
        current_theme_name = get_translation(f"theme_{settings.theme}", self.language)
        theme_dropdown.set(current_theme_name)

        # Store mapping from display names to IDs
        self.theme_name_to_id = {name: tid for name, tid in theme_choices}

        theme_dropdown.pack(side="left")

        # Preview button
        btn_bg = self.theme.accent
        btn_fg = self.theme.background if self.theme.name != "Dark Mode" else "#1f2937"
        tk.Button(
            theme_frame,
            text=get_translation("settings_preview", self.language),
            command=self._preview_theme,
            bg=btn_bg,
            fg=btn_fg,
            font=("Segoe UI", 10),
            relief="flat",
            padx=10,
            cursor="hand2"
        ).pack(side="left", padx=(5, 0))

        # Language Setting
        add_row(appearance_category, 1, get_translation("label_language", self.language))
        language_frame = tk.Frame(appearance_category, bg=self.theme.background)
        language_frame.grid(row=1, column=1, sticky="w")

        # Create language dropdown
        available_langs = get_available_languages()
        language_choices = [(get_language_display_name(lang_code), lang_code) for lang_code in available_langs.keys()]

        # Set current language display name
        current_lang_display = get_language_display_name(settings.language)
        self.language_var = tk.StringVar(value=current_lang_display)

        language_dropdown = ttk.Combobox(
            language_frame,
            textvariable=self.language_var,
            values=[display_name for display_name, _ in language_choices],
            state="readonly",
            width=20
        )

        # Store mapping from display names to language codes
        self.language_name_to_code = {name: code for name, code in language_choices}

        language_dropdown.pack(side="left")

        # ========== NOTIFICATION SETTINGS CATEGORY ==========
        notification_category = create_category_frame(frm, get_translation("category_notifications", self.language), "🔔")

        # Pre-warning settings
        add_row(notification_category, 0, get_translation("label_pre_warning", self.language))
        self.pre_warning_var = tk.BooleanVar(value=settings.pre_warning)
        pre_warning_frame = tk.Frame(notification_category, bg=self.theme.background)
        pre_warning_frame.grid(row=0, column=1, sticky="w")

        tk.Checkbutton(
            pre_warning_frame,
            text=get_translation("checkbox_show_notification", self.language),
            variable=self.pre_warning_var,
            command=self._toggle_pre_warning,
            bg=self.theme.background,
            fg=self.theme.text_primary,
            font=("Segoe UI", 10),
            selectcolor=self._darken_color(self.theme.background),
            activebackground=self.theme.background
        ).pack(side="left")

        add_row(notification_category, 1, get_translation("label_warning_time", self.language))
        warning_frame = tk.Frame(notification_category, bg=self.theme.background)
        warning_frame.grid(row=1, column=1, sticky="w")

        self.pre_warning_seconds_var = tk.StringVar(value=str(settings.pre_warning_seconds))

        # Dropdown for warning time (10-60 seconds in 10 second increments)
        warning_values = ["10", "20", "30", "40", "50", "60"]
        self.pre_warning_combo = ttk.Combobox(warning_frame, textvariable=self.pre_warning_seconds_var,
                                              values=warning_values, state="readonly", width=8)
        self.pre_warning_combo.pack(side="left")

        tk.Label(warning_frame, text=get_translation("label_seconds_before", self.language),
                font=("Segoe UI", 9),
                fg=self.theme.text_secondary,
                bg=self.theme.background).pack(side="left")

        add_row(notification_category, 2, get_translation("label_flash_mode", self.language))
        flash_frame = tk.Frame(notification_category, bg=self.theme.background)
        flash_frame.grid(row=2, column=1, sticky="w")

        self.pre_warning_flash_var = tk.BooleanVar(value=settings.pre_warning_flash)
        self.flash_check = tk.Checkbutton(
            flash_frame,
            text=get_translation("checkbox_quick_flash", self.language),
            variable=self.pre_warning_flash_var,
            command=self._toggle_flash_duration,
            bg=self.theme.background,
            fg=self.theme.text_primary,
            font=("Segoe UI", 10),
            selectcolor=self._darken_color(self.theme.background),
            activebackground=self.theme.background
        )
        self.flash_check.pack(side="left")

        # Flash duration dropdown (1-10 seconds)
        tk.Label(flash_frame, text=get_translation("label_duration", self.language),
                font=("Segoe UI", 9),
                fg=self.theme.text_secondary,
                bg=self.theme.background).pack(side="left")

        self.flash_duration_var = tk.StringVar(value=str(getattr(settings, 'pre_warning_flash_duration', 3)))
        flash_duration_values = [str(i) for i in range(1, 11)]  # 1-10 seconds
        self.flash_duration_combo = ttk.Combobox(flash_frame, textvariable=self.flash_duration_var,
                                                 values=flash_duration_values,
                                                 state="readonly", width=3)
        self.flash_duration_combo.pack(side="left")

        tk.Label(flash_frame, text=get_translation("label_sec", self.language),
                font=("Segoe UI", 9),
                fg=self.theme.text_secondary,
                bg=self.theme.background).pack(side="left")

        # Enable/disable based on checkbox
        self._toggle_pre_warning()
        self._toggle_flash_duration()

        # Call update_preview initially to show current settings
        update_preview()
        update_time_labels()

        # Function to update settings summary
        def update_summary(*args):
            """Update the summary text based on current settings"""
            try:
                # Get current values
                interval = int(self.int_var.get())
                active_from = self.from_var.get()
                active_to = self.to_var.get()
                lock_duration = int(self.lock_var.get())
                activity_type = self.activity_var.get()
                position = self.position_var.get()

                # Calculate work hours
                from_hour = int(active_from.split(':')[0]) if ':' in active_from else int(active_from) if active_from.isdigit() else 9
                to_hour = int(active_to.split(':')[0]) if ':' in active_to else int(active_to) if active_to.isdigit() else 18

                # Handle day wrapping (e.g., 22:00 to 6:00)
                if to_hour <= from_hour:
                    work_hours = (24 - from_hour) + to_hour
                else:
                    work_hours = to_hour - from_hour

                # Calculate breaks per day
                if interval > 0:
                    breaks_per_day = (work_hours * 60) // interval
                else:
                    breaks_per_day = 0

                # Calculate total exercise time
                total_exercise_minutes = (breaks_per_day * lock_duration) / 60

                # Get activity type text
                activity_text = {
                    "both": get_translation("activity_both", self.language).lower(),
                    "stretching": get_translation("activity_stretch", self.language).lower(),
                    "exercise": get_translation("activity_exercise", self.language).lower()
                }.get(activity_type, activity_type)

                # Get position text
                position_text = {
                    "all": get_translation("position_all", self.language).lower(),
                    "sitting_standing": get_translation("position_sitting_standing", self.language).lower(),
                    "sitting": get_translation("position_sitting", self.language).lower(),
                    "standing": get_translation("position_standing", self.language).lower()
                }.get(position, position)

                # Build summary text - use compact version
                summary = get_translation("settings_summary_compact", self.language).format(
                    breaks=breaks_per_day,
                    interval=interval,
                    duration=lock_duration,
                    total_minutes=int(total_exercise_minutes),
                    activity=activity_text,
                    from_time=active_from,
                    to_time=active_to
                )

                self.summary_label.config(text=summary)
            except Exception as e:
                # Fallback to simple summary if something goes wrong
                try:
                    interval = int(self.int_var.get())
                    self.summary_label.config(text=f"Break every {interval} minutes")
                except:
                    self.summary_label.config(text="")

        # Connect update_summary to all setting changes
        self.int_var.trace('w', update_summary)
        self.from_var.trace('w', update_summary)
        self.from_min_var.trace('w', update_summary)
        self.to_var.trace('w', update_summary)
        self.to_min_var.trace('w', update_summary)
        self.lock_var.trace('w', update_summary)
        self.activity_var.trace('w', update_summary)
        self.position_var.trace('w', update_summary)
        self.time_format_var.trace('w', lambda *args: (update_time_labels(), update_summary()))

        # Initial summary update
        update_summary()

        # ========== ACTION BUTTONS ==========
        btns = tk.Frame(frm, bg=self.theme.background)
        btns.pack(pady=12)

        # Save button (primary)
        save_btn = tk.Button(
            btns,
            text=get_translation("settings_save", self.language),
            command=self._save,
            bg=self.theme.accent,
            fg=self.theme.background if self.theme.name != "Dark Mode" else "#1f2937",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=18,
            pady=4,
            cursor="hand2"
        )
        save_btn.pack(side="left", padx=6)

        # Cancel button (secondary)
        cancel_btn = tk.Button(
            btns,
            text=get_translation("settings_cancel", self.language),
            command=self.win.destroy,
            bg=self._darken_color(self.theme.background),
            fg=self.theme.text_primary,
            font=("Segoe UI", 10),
            relief="flat",
            padx=18,
            pady=4,
            cursor="hand2"
        )
        cancel_btn.pack(side="left", padx=6)

        # Reset to Defaults button (warning color)
        reset_btn = tk.Button(
            btns,
            text=get_translation("settings_reset", self.language),
            command=self._reset_to_defaults,
            bg="#dc2626" if self.theme.name == "Dark Mode" else "#ef4444",
            fg="#ffffff",
            font=("Segoe UI", 10),
            relief="flat",
            padx=18,
            pady=4,
            cursor="hand2"
        )
        reset_btn.pack(side="left", padx=6)

    def _reset_to_defaults(self):
        """Reset all settings to default values."""
        # Import at function level to avoid circular dependency
        from .config import get_default_settings

        # Confirm with user
        from tkinter import messagebox
        result = messagebox.askyesno(
            get_translation("reset_dialog_title", self.language),
            get_translation("reset_dialog_message", self.language),
            parent=self.win
        )

        if result:
            # Get default settings
            defaults = get_default_settings()

            # Update all UI variables
            self.time_format_var.set(defaults.time_format_24h)

            # Parse time for display
            from_h, from_m = map(int, defaults.active_from.split(':'))
            to_h, to_m = map(int, defaults.active_to.split(':'))

            # Update main time variables (these are what get saved)
            self.from_var.set(defaults.active_from)
            self.to_var.set(defaults.active_to)

            # Update 24-hour variables
            self.from_hour_24_var.set(f"{from_h:02d}")
            self.from_min_24_var.set(f"{from_m:02d}")
            self.to_hour_24_var.set(f"{to_h:02d}")
            self.to_min_24_var.set(f"{to_m:02d}")

            # Update 12-hour variables
            from_period = "AM" if from_h < 12 else "PM"
            from_h12 = from_h % 12 if from_h % 12 != 0 else 12
            self.from_hour_var.set(str(from_h12))
            self.from_min_var.set(f"{from_m:02d}")
            self.from_period_var.set(from_period)

            to_period = "AM" if to_h < 12 else "PM"
            to_h12 = to_h % 12 if to_h % 12 != 0 else 12
            self.to_hour_var.set(str(to_h12))
            self.to_min_var.set(f"{to_m:02d}")
            self.to_period_var.set(to_period)

            # Update other settings
            self.int_var.set(str(defaults.interval_minutes))
            self.trigger_var.set(str(defaults.trigger_at_minute))
            self.lock_var.set(str(defaults.lock_seconds))
            self.auto_var.set(defaults.start_on_login)

            # Update theme
            current_theme = get_theme(defaults.theme)
            self.theme_var.set(current_theme.name)

            # Update language
            current_lang_display = get_language_display_name(defaults.language)
            self.language_var.set(current_lang_display)

            # Update activity and position settings
            current_activity_val = getattr(defaults, 'activity_type', 'both')
            activity_values = [
                ("both", "Both (stretch + exercise)"),
                ("stretch", "Stretches only"),
                ("exercise", "Exercises only")
            ]
            for val, desc in activity_values:
                if val == current_activity_val:
                    self.activity_var.set(desc)
                    break

            current_position_val = getattr(defaults, 'position_preference', 'sitting_standing')
            position_values = [
                ("sitting_standing", "Sitting & Standing (default)"),
                ("all", "All positions"),
                ("sitting", "Sitting only"),
                ("standing", "Standing only"),
                ("lying", "Lying/Ground only")
            ]
            for val, desc in position_values:
                if val == current_position_val:
                    self.position_var.set(desc)
                    break

            # Update notification settings
            self.pre_warning_var.set(defaults.pre_warning)
            self.pre_warning_seconds_var.set(str(defaults.pre_warning_seconds))
            self.pre_warning_flash_var.set(defaults.pre_warning_flash)
            self.flash_duration_var.set(str(defaults.pre_warning_flash_duration))

            # Update UI state
            self._toggle_pre_warning()
            self._toggle_flash_duration()

            messagebox.showinfo(
                get_translation("reset_complete_title", self.language),
                get_translation("reset_complete_message", self.language),
                parent=self.win
            )

    def _toggle_pre_warning(self):
        """Enable/disable pre-warning seconds dropdown and flash mode based on checkbox."""
        try:
            if self.pre_warning_var.get():
                if hasattr(self, 'pre_warning_combo') and self.pre_warning_combo:
                    self.pre_warning_combo.configure(state="readonly")
                if hasattr(self, 'flash_check') and self.flash_check:
                    self.flash_check.configure(state="normal")
                self._toggle_flash_duration()  # Update flash duration state
            else:
                if hasattr(self, 'pre_warning_combo') and self.pre_warning_combo:
                    self.pre_warning_combo.configure(state="disabled")
                if hasattr(self, 'flash_check') and self.flash_check:
                    self.flash_check.configure(state="disabled")
                if hasattr(self, 'flash_duration_combo') and self.flash_duration_combo:
                    self.flash_duration_combo.configure(state="disabled")
        except Exception as e:
            # Silently handle widget access issues
            pass

    def _toggle_flash_duration(self):
        """Enable/disable flash duration based on flash mode checkbox."""
        try:
            if hasattr(self, 'flash_duration_combo') and self.flash_duration_combo:
                if self.pre_warning_var.get() and self.pre_warning_flash_var.get():
                    self.flash_duration_combo.configure(state="readonly")
                else:
                    self.flash_duration_combo.configure(state="disabled")
        except Exception as e:
            # Silently handle widget access issues
            pass

    def _preview_theme(self):
        """Show a quick preview of the selected theme."""
        theme_name = self.theme_var.get()
        theme_id = self.theme_name_to_id.get(theme_name, "green")
        theme = get_theme(theme_id)

        # Create a preview window
        preview = tk.Toplevel(self.win)
        preview.title(f"{get_translation('preview_title', self.language)}: {theme.name}")
        preview.geometry("400x250")
        preview.configure(bg=theme.background)
        preview.resizable(False, False)

        # Preview content
        tk.Label(
            preview,
            text=get_translation("preview_message", self.language),
            font=("Segoe UI", 24, "bold"),
            fg=theme.text_primary,
            bg=theme.background
        ).pack(pady=20)

        tk.Label(
            preview,
            text="💪",
            font=("Segoe UI Emoji", 48),
            fg=theme.text_primary,
            bg=theme.background
        ).pack()

        tk.Label(
            preview,
            text="30",
            font=("Segoe UI", 36, "bold"),
            fg=theme.accent,
            bg=theme.background
        ).pack(pady=10)

        tk.Label(
            preview,
            text=get_translation("preview_submessage", self.language),
            font=("Segoe UI", 12, "italic"),
            fg=theme.text_secondary,
            bg=theme.background
        ).pack()

        # Close button
        tk.Button(
            preview,
            text=get_translation("preview_close", self.language),
            command=preview.destroy,
            padx=20,
            pady=5
        ).pack(pady=15)

        # Auto-close after 3 seconds
        preview.after(3000, lambda: preview.destroy() if preview.winfo_exists() else None)

    def _save(self):
        try:
            # Get theme ID from display name
            theme_name = self.theme_var.get()
            theme_id = self.theme_name_to_id.get(theme_name, "green")

            # Get trigger minute
            try:
                trigger_minute = int(self.trigger_var.get().strip())
                # Validate minute (0-59)
                if trigger_minute < 0 or trigger_minute > 59:
                    trigger_minute = 0
            except ValueError:
                trigger_minute = 0

            # Convert activity display value back to config value
            activity_display = self.activity_var.get()
            activity_values = [
                ("both", "Both (stretch + exercise)"),
                ("stretch", "Stretches only"),
                ("exercise", "Exercises only")
            ]
            activity_val = "both"  # default
            for val, desc in activity_values:
                if desc == activity_display:
                    activity_val = val
                    break

            # Convert position display value back to config value
            position_display = self.position_var.get()
            position_values = [
                ("sitting_standing", "Sitting & Standing (default)"),
                ("all", "All positions"),
                ("sitting", "Sitting only"),
                ("standing", "Standing only"),
                ("lying", "Lying/Ground only")
            ]
            position_val = "sitting_standing"  # default
            for val, desc in position_values:
                if desc == position_display:
                    position_val = val
                    break

            # Validate lock duration (30-180 seconds)
            lock_duration = int(self.lock_var.get().strip())
            if lock_duration < 30:
                lock_duration = 30
            elif lock_duration > 180:
                lock_duration = 180

            # Get language code from display name
            language_display = self.language_var.get()
            language_code = self.language_name_to_code.get(language_display, "en")

            s = Settings(
                active_from=self.from_var.get().strip(),
                active_to=self.to_var.get().strip(),
                interval_minutes=int(self.int_var.get().strip()),
                trigger_at_minute=trigger_minute,
                lock_seconds=lock_duration,
                activity_type=activity_val,
                position_preference=position_val,
                paused=False,
                start_on_login=self.auto_var.get(),
                theme=theme_id,
                pre_warning=self.pre_warning_var.get(),
                pre_warning_seconds=int(self.pre_warning_seconds_var.get().strip()) if self.pre_warning_var.get() else 60,
                pre_warning_flash=self.pre_warning_flash_var.get() if self.pre_warning_var.get() else True,
                pre_warning_flash_duration=int(self.flash_duration_var.get()) if self.pre_warning_flash_var.get() else 3,
                time_format_24h=self.time_format_var.get(),
                disclaimer_accepted=self.settings.disclaimer_accepted,  # Preserve disclaimer status
                disclaimer_version=self.settings.disclaimer_version,
                language=language_code,
                # Preserve version checking settings
                last_version_check=getattr(self.settings, 'last_version_check', 0),
                latest_known_version=getattr(self.settings, 'latest_known_version', ""),
                auto_check_updates=getattr(self.settings, 'auto_check_updates', True)
            )
            save_settings(s)
            if callable(self._set_autostart_state):
                try:
                    self._set_autostart_state(self.auto_var.get())
                except Exception:
                    pass
            if self.on_save:
                self.on_save(s)
            self._on_close()
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Settings save error: {error_details}")
            messagebox.showerror(get_translation("error_title", self.language), f"{get_translation('validation_invalid_settings', self.language)}\n\n{str(e)}\n\nCheck console for details.")

    def _on_close(self):
        """Clean up and close the settings window."""
        if hasattr(self, '_is_open') and self._is_open:
            self._is_open = False
            try:
                self.win.destroy()
            except:
                pass


# --- Scheduler ---
class Scheduler(threading.Thread):
    def __init__(self, trigger_fn, pre_warning_fn, get_settings):
        super().__init__(daemon=True)
        self.trigger_fn = trigger_fn
        self.pre_warning_fn = pre_warning_fn
        self.get_settings = get_settings
        self._stop = threading.Event()
        self._lock = threading.Lock()  # Add thread safety lock
        self.next_fire = None
        self.pre_warning_shown = False
        self.snooze_until = None

    def run(self):
        # Calculate first trigger time based on trigger_at_minute
        s: Settings = self.get_settings()
        now = datetime.now()

        # Calculate next trigger based on interval and trigger minute
        next_hour, next_minute = calculate_next_trigger_time(
            s.interval_minutes,
            s.trigger_at_minute,
            now.hour,
            now.minute
        )

        # Create datetime for next trigger
        next_trigger = now.replace(hour=next_hour, minute=next_minute, second=0, microsecond=0)

        # Keep adding intervals until we get a future time
        while next_trigger <= now:
            next_trigger += timedelta(minutes=s.interval_minutes)

        # Check if next trigger is within active hours
        next_trigger = self._ensure_within_active_hours(next_trigger, s)

        self.next_fire = next_trigger
        logging.info(f"[Scheduler] Initial next break scheduled for: {self.next_fire.strftime('%H:%M:%S')}")

        while not self._stop.is_set():
            s: Settings = self.get_settings()
            if not s.paused and self._within_hours(s):
                now = datetime.now()

                # Check if we're in snooze period
                if self.snooze_until and now < self.snooze_until:
                    self._stop.wait(1.0)
                    continue

                # Clear snooze if expired
                if self.snooze_until and now >= self.snooze_until:
                    self.snooze_until = None
                    # Reset next fire time after snooze
                    self.next_fire = now + timedelta(seconds=5)  # Quick trigger after snooze
                    self.pre_warning_shown = False

                # Check for pre-warning
                if s.pre_warning and self.next_fire and not self.pre_warning_shown:
                    time_until = (self.next_fire - now).total_seconds()
                    if 0 < time_until <= s.pre_warning_seconds:
                        # Round up to avoid showing N-1 seconds
                        seconds_to_show = math.ceil(time_until)
                        logging.info(f"[Scheduler] Showing pre-warning: {seconds_to_show} seconds until break")
                        self.pre_warning_fn(seconds_to_show)
                        self.pre_warning_shown = True

                # Check for main trigger
                if self.next_fire and now >= self.next_fire:
                    logging.info(f"[Scheduler] Triggering break at {now.strftime('%H:%M:%S')}")
                    self.trigger_fn()

                    # Calculate next trigger time
                    next_hour, next_minute = calculate_next_trigger_time(
                        s.interval_minutes,
                        s.trigger_at_minute,
                        now.hour,
                        now.minute + 1  # Add 1 minute to avoid re-triggering
                    )

                    # Handle day rollover
                    if next_hour < now.hour:
                        # Next day
                        next_trigger = (now + timedelta(days=1)).replace(
                            hour=next_hour, minute=next_minute, second=0, microsecond=0
                        )
                    else:
                        next_trigger = now.replace(
                            hour=next_hour, minute=next_minute, second=0, microsecond=0
                        )

                    # Ensure we don't trigger in the past
                    if next_trigger <= now:
                        next_trigger += timedelta(minutes=s.interval_minutes)

                    # Check if next trigger is within active hours
                    next_trigger = self._ensure_within_active_hours(next_trigger, s)

                    self.next_fire = next_trigger
                    self.pre_warning_shown = False
                    logging.info(f"[Scheduler] Next break scheduled for: {self.next_fire.strftime('%H:%M:%S')}")
            else:
                # Log every 30 seconds when outside active hours or paused
                if not hasattr(self, '_last_status_log'):
                    self._last_status_log = datetime.now()

                if (datetime.now() - self._last_status_log).total_seconds() > 30:
                    if s.paused:
                        logging.debug("[Scheduler] Currently paused")
                    else:
                        logging.debug(f"[Scheduler] Outside active hours ({s.active_from} - {s.active_to})")
                    self._last_status_log = datetime.now()

            # Sleep in small increments to be responsive to changes
            self._stop.wait(1.0)

    def snooze(self, minutes=5):
        """Snooze the next break for specified minutes."""
        with self._lock:
            self.snooze_until = datetime.now() + timedelta(minutes=minutes)
            self.pre_warning_shown = False

    def trigger_now(self):
        """Trigger break immediately."""
        with self._lock:
            self.next_fire = datetime.now()
            self.pre_warning_shown = True  # Skip pre-warning for manual trigger

    def recalculate_next_fire(self):
        """Recalculate the next break time based on current settings."""
        with self._lock:
            s: Settings = self.get_settings()
            now = datetime.now()

            # Calculate next trigger based on interval and trigger minute
            next_hour, next_minute = calculate_next_trigger_time(
                s.interval_minutes,
                s.trigger_at_minute,
                now.hour,
                now.minute
            )

            # Create datetime for next trigger
            next_trigger = now.replace(hour=next_hour, minute=next_minute, second=0, microsecond=0)

            # Keep adding intervals until we get a future time
            while next_trigger <= now:
                next_trigger += timedelta(minutes=s.interval_minutes)

            # Check if next trigger is within active hours
            next_trigger = self._ensure_within_active_hours(next_trigger, s)

        self.next_fire = next_trigger
        self.pre_warning_shown = False
        logging.info(f"[Scheduler] Recalculated next break for: {self.next_fire.strftime('%H:%M:%S')}")

    def stop(self):
        self._stop.set()

    def _within_hours(self, s: Settings) -> bool:
        now = datetime.now().time()
        start = s.parse_active_from()
        end = s.parse_active_to()
        if start <= end:
            return start <= now <= end
        # Overnight window
        return now >= start or now <= end

    def _ensure_within_active_hours(self, next_trigger: datetime, s: Settings) -> datetime:
        """Ensure the next trigger time falls within active hours. If not, schedule for next day's start."""
        start_time = s.parse_active_from()
        end_time = s.parse_active_to()

        trigger_time = next_trigger.time()

        # If active hours don't span midnight (e.g., 5:00-17:00)
        if start_time <= end_time:
            # Check if trigger time is outside active hours
            if trigger_time > end_time or trigger_time < start_time:
                # Schedule for next day's start time
                next_day = next_trigger.date() + timedelta(days=1)
                return datetime.combine(next_day, start_time)
        else:
            # Active hours span midnight (e.g., 22:00-06:00)
            if end_time < trigger_time < start_time:
                # Schedule for today's start time if we haven't passed it, else tomorrow
                if datetime.now().time() < start_time:
                    return datetime.combine(next_trigger.date(), start_time)
                else:
                    next_day = next_trigger.date() + timedelta(days=1)
                    return datetime.combine(next_day, start_time)

        # Trigger time is within active hours
        return next_trigger


# --- App ---
class MoveReminderApp:
    def __init__(self):
        self.settings = load_settings()
        self.root = tk.Tk()

        # Set window icon
        try:
            icon_image = _dumbbell_icon(32)
            self.root.iconphoto(False, ImageTk.PhotoImage(icon_image))
        except Exception:
            pass  # Fallback to default icon if there's an issue

        self.root.withdraw()
        self._tray = None
        self._scheduler = Scheduler(self.trigger_overlay, self.show_pre_warning, self._get_settings)
        self._toast = None
        self._lm = TinyPhraseLM(language=self.settings.language)
        self._lock = threading.Lock()
        self._pause_until = None  # For temporary pause functionality
        self._skip_next = False  # Flag to skip next break
        self._settings_window = None
        self._body_map_window = None
        self._settings_autosave_timer = None
        self._paused_icon = None
        self._disclaimer_accepted = False  # Track disclaimer acceptance for this session

        # Initialize version checker
        self._version_checker = VersionChecker(self.settings)
        self._version_checker.set_update_callback(self._handle_update_available)
        self._update_info = None  # Store update information

        # Register cleanup on exit
        atexit.register(self._cleanup_on_exit)

        # Start periodic settings save
        self._start_autosave()

    def _get_settings(self):
        return self.settings

    def _setup_linux_appindicator(self, image, menu):
        """Setup native AppIndicator3 for GNOME compatibility"""
        print("[Linux] Attempting to use native AppIndicator3...")

        try:
            # Import AppIndicator3
            import gi
            gi.require_version('AppIndicator3', '0.1')
            gi.require_version('Gtk', '3.0')
            from gi.repository import AppIndicator3, Gtk, GLib

            # Ensure we can create an indicator to test functionality
            test_indicator = AppIndicator3.Indicator.new(
                "test", "", AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            if test_indicator is None:
                raise Exception("AppIndicator3 not functional")

            print("[Linux] AppIndicator3 libraries loaded and tested successfully")

            # Save icon to temporary file for AppIndicator
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                image.save(tmp.name, 'PNG')
                self._temp_icon_path = tmp.name

            # Create AppIndicator
            self._indicator = AppIndicator3.Indicator.new(
                "gitfit-dev",
                self._temp_icon_path,
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )

            # Set status to active
            self._indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            self._indicator.set_title("GitFit.dev")
            self._indicator.set_label("GitFit.dev", "GitFit.dev")

            # Convert pystray menu to GTK menu
            gtk_menu = self._create_gtk_menu_from_pystray(menu)
            self._indicator.set_menu(gtk_menu)

            # Store reference to prevent garbage collection
            self._gtk_menu = gtk_menu
            self._tray = self._indicator  # Store as tray for consistency

            # Create GNOME-compatible notification
            try:
                import subprocess
                subprocess.run([
                    'notify-send',
                    'GitFit.dev Started',
                    'Click the system tray icon to access menu.',
                    '--icon=applications-utilities'
                ], capture_output=True, timeout=5)
            except:
                pass

            print("[Linux] Native AppIndicator3 setup completed successfully")
            print("[Linux] • Click tray icon for menu")
            print("[Linux] • Alternative: ./GitFitDev --show-settings")

        except Exception as e:
            print(f"[Linux] AppIndicator3 setup failed: {e}")
            # Clean up temp file if created
            if hasattr(self, '_temp_icon_path'):
                try:
                    import os
                    os.unlink(self._temp_icon_path)
                except:
                    pass
            raise

    def _create_gtk_menu_from_pystray(self, pystray_menu):
        """Convert a pystray menu to a GTK menu"""
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk

            gtk_menu = Gtk.Menu()
        except Exception as e:
            print(f"[Linux] Failed to import GTK: {e}")
            raise

        for item in pystray_menu:
            if hasattr(item, 'text'):
                if item.text == pystray.Menu.SEPARATOR:
                    # Add separator
                    separator = Gtk.SeparatorMenuItem()
                    gtk_menu.append(separator)
                else:
                    # Regular menu item
                    menu_item = Gtk.MenuItem.new_with_label(item.text)

                    # Handle submenu
                    if hasattr(item, 'menu') and item.menu:
                        submenu = self._create_gtk_menu_from_pystray(item.menu)
                        menu_item.set_submenu(submenu)

                    # Handle action
                    if hasattr(item, 'action') and item.action:
                        def create_callback(action):
                            def callback(widget):
                                try:
                                    # Call the action with proper parameters
                                    if callable(action):
                                        action(self._indicator, item)
                                except Exception as e:
                                    print(f"[Linux] Menu action error: {e}")
                            return callback

                        menu_item.connect("activate", create_callback(item.action))

                    # Handle checked state
                    if hasattr(item, 'checked') and callable(item.checked):
                        try:
                            is_checked = item.checked(item)
                            if is_checked is not None:
                                # Convert to CheckMenuItem
                                check_item = Gtk.CheckMenuItem.new_with_label(item.text)
                                check_item.set_active(bool(is_checked))
                                if hasattr(item, 'action') and item.action:
                                    def create_check_callback(action):
                                        def callback(widget):
                                            try:
                                                action(self._indicator, item)
                                            except Exception as e:
                                                print(f"[Linux] Check menu action error: {e}")
                                        return callback
                                    check_item.connect("toggled", create_check_callback(item.action))
                                menu_item = check_item
                        except:
                            pass  # Use regular menu item if checked state fails

                    gtk_menu.append(menu_item)

        gtk_menu.show_all()
        return gtk_menu

    def _setup_linux_alternatives(self):
        """Setup alternative access methods for Linux/GNOME"""
        print("[Linux] Setting up alternative access methods...")

        # Method 1: D-Bus service for external control
        try:
            self._setup_dbus_service()
        except Exception as e:
            print(f"[Linux] D-Bus service setup failed: {e}")

        # Method 2: Create desktop entry with keyboard shortcuts
        try:
            self._create_linux_desktop_entries()
        except Exception as e:
            print(f"[Linux] Desktop entries creation failed: {e}")

        # Method 3: Persistent notification with action buttons
        try:
            self._create_persistent_notification()
        except Exception as e:
            print(f"[Linux] Persistent notification failed: {e}")

        # Method 4: File-based control system
        try:
            self._setup_file_control_system()
        except Exception as e:
            print(f"[Linux] File control system failed: {e}")

        print("[Linux] Alternative access methods configured.")
        print("[Linux] Available access methods:")
        print("[Linux] • Super+G: Quick settings access")
        print("[Linux] • Super+Shift+G: Toggle pause/resume")
        print("[Linux] • ./GitFitDev --show-settings")
        print("[Linux] • ./GitFitDev --toggle-pause")
        print("[Linux] • touch ~/.gitfitdev/show_settings")

    def _setup_dbus_service(self):
        """Setup D-Bus service for external control"""
        try:
            import dbus
            import dbus.service
            from dbus.mainloop.glib import DBusGMainLoop

            # This is complex to implement properly, skip for now
            # Would need proper D-Bus service implementation
            pass
        except ImportError:
            pass

    def _create_linux_desktop_entries(self):
        """Create desktop entries for keyboard shortcuts"""
        import os

        # Get executable path
        exe_path = sys.executable if not self._is_frozen() else sys.argv[0]

        # Main settings shortcut
        settings_entry = f"""[Desktop Entry]
Type=Application
Name=GitFit.dev Settings
Comment=Open GitFit.dev Settings
Exec={exe_path} --show-settings
Icon=applications-utilities
NoDisplay=true
StartupNotify=false
Keywords=gitfit;settings;fitness;break;
"""

        # Pause toggle shortcut
        pause_entry = f"""[Desktop Entry]
Type=Application
Name=GitFit.dev Toggle Pause
Comment=Toggle GitFit.dev Pause/Resume
Exec={exe_path} --toggle-pause
Icon=applications-utilities
NoDisplay=true
StartupNotify=false
Keywords=gitfit;pause;resume;fitness;break;
"""

        # Write desktop entries
        desktop_dir = os.path.expanduser("~/.local/share/applications")
        os.makedirs(desktop_dir, exist_ok=True)

        with open(os.path.join(desktop_dir, "gitfit-settings.desktop"), 'w') as f:
            f.write(settings_entry)

        with open(os.path.join(desktop_dir, "gitfit-pause.desktop"), 'w') as f:
            f.write(pause_entry)

        # Try to setup custom keyboard shortcuts (GNOME)
        try:
            import subprocess

            # Set custom keyboard shortcuts using gsettings
            subprocess.run([
                'gsettings', 'set', 'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gitfit-settings/',
                'name', 'GitFit.dev Settings'
            ], capture_output=True, timeout=5)

            subprocess.run([
                'gsettings', 'set', 'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gitfit-settings/',
                'command', f'{exe_path} --show-settings'
            ], capture_output=True, timeout=5)

            subprocess.run([
                'gsettings', 'set', 'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gitfit-settings/',
                'binding', '<Super>g'
            ], capture_output=True, timeout=5)

            # Pause toggle shortcut
            subprocess.run([
                'gsettings', 'set', 'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gitfit-pause/',
                'name', 'GitFit.dev Toggle Pause'
            ], capture_output=True, timeout=5)

            subprocess.run([
                'gsettings', 'set', 'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gitfit-pause/',
                'command', f'{exe_path} --toggle-pause'
            ], capture_output=True, timeout=5)

            subprocess.run([
                'gsettings', 'set', 'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gitfit-pause/',
                'binding', '<Super><Shift>g'
            ], capture_output=True, timeout=5)

            # Add to the list of custom keybindings
            result = subprocess.run([
                'gsettings', 'get', 'org.gnome.settings-daemon.plugins.media-keys', 'custom-keybindings'
            ], capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                current_bindings = result.stdout.strip()
                if 'gitfit-settings' not in current_bindings:
                    # Parse current bindings and add ours
                    if current_bindings in ['@as []', '[]']:
                        new_bindings = "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gitfit-settings/', '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gitfit-pause/']"
                    else:
                        # Add to existing bindings
                        current_bindings = current_bindings.strip("[]'")
                        if current_bindings:
                            new_bindings = f"['{current_bindings}', '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gitfit-settings/', '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gitfit-pause/']"
                        else:
                            new_bindings = "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gitfit-settings/', '/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gitfit-pause/']"

                    subprocess.run([
                        'gsettings', 'set', 'org.gnome.settings-daemon.plugins.media-keys', 'custom-keybindings', new_bindings
                    ], capture_output=True, timeout=5)

            print("[Linux] GNOME keyboard shortcuts configured:")
            print("[Linux] • Super+G: Open settings")
            print("[Linux] • Super+Shift+G: Toggle pause")

        except Exception as e:
            print(f"[Linux] Keyboard shortcuts setup failed: {e}")

    def _create_persistent_notification(self):
        """Create a persistent notification with action buttons (if supported)"""
        try:
            import subprocess

            # Send a notification with instructions
            subprocess.run([
                'notify-send',
                '--urgency=low',
                '--expire-time=10000',  # 10 seconds
                'GitFit.dev',
                'System tray may not be clickable in GNOME.\nUse Super+G for settings or run:\n./GitFitDev --show-settings',
                '--icon=applications-utilities'
            ], capture_output=True, timeout=5)

        except Exception:
            pass

    def _setup_file_control_system(self):
        """Setup file-based control system for external tools"""
        control_dir = os.path.expanduser("~/.gitfitdev/control")
        os.makedirs(control_dir, exist_ok=True)

        # Create control files that external scripts can touch
        control_files = {
            'show_settings': 'Touch this file to open settings',
            'toggle_pause': 'Touch this file to toggle pause/resume',
            'trigger_break': 'Touch this file to trigger break now',
            'quit': 'Touch this file to quit application'
        }

        for filename, description in control_files.items():
            readme_path = os.path.join(control_dir, f"{filename}.txt")
            with open(readme_path, 'w') as f:
                f.write(f"{description}\n")
                f.write(f"Usage: touch ~/.gitfitdev/control/{filename}\n")

        # Start file monitoring
        def check_control_files():
            try:
                for action in ['show_settings', 'toggle_pause', 'trigger_break', 'quit']:
                    control_file = os.path.join(control_dir, action)
                    if os.path.exists(control_file):
                        os.remove(control_file)  # Remove trigger file

                        # Execute action
                        if action == 'show_settings':
                            self._call_in_tk(self.open_settings)
                        elif action == 'toggle_pause':
                            self._call_in_tk(lambda: self._toggle_pause(None, None))
                        elif action == 'trigger_break':
                            self._call_in_tk(self.trigger_overlay)
                        elif action == 'quit':
                            self._call_in_tk(self._quit)

                        print(f"[Linux] Control file action executed: {action}")

                # Schedule next check
                if self.root:
                    self.root.after(2000, check_control_files)  # Check every 2 seconds

            except Exception as e:
                print(f"[Linux] Control file monitoring error: {e}")
                # Retry in 5 seconds
                if self.root:
                    self.root.after(5000, check_control_files)

        # Start monitoring
        if self.root:
            self.root.after(1000, check_control_files)

        print(f"[Linux] File control system active in: {control_dir}")
        print(f"[Linux] Example: touch ~/.gitfitdev/control/show_settings")

    def start(self):
        # Check disclaimer acceptance before starting any functionality
        if not self.settings.disclaimer_accepted:
            self._show_disclaimer()
            if not self._disclaimer_accepted:
                # User declined, exit the application
                return

        if pystray is None:
            messagebox.showerror(
                APP_NAME,
                get_translation("error_missing_deps", self.settings.language),
            )
            # Still run without tray — scheduler + overlay only
            self._scheduler.start()
            self.root.mainloop()
            return

        image = _dumbbell_icon(64)

        def get_status_text(item=None):
            if self._pause_until and datetime.now() < self._pause_until:
                minutes_left = int((self._pause_until - datetime.now()).total_seconds() / 60)
                paused_for_text = get_translation("paused_for_minutes", self.settings.language)
                return paused_for_text.format(minutes=minutes_left)
            elif self.settings.paused:
                return get_translation("status_paused", self.settings.language)
            elif self._skip_next:
                return get_translation("next_break_skipped", self.settings.language)
            elif self._scheduler.next_fire:
                time_str = self._scheduler.next_fire.strftime('%H:%M')
                # Format based on user preference
                if not self.settings.time_format_24h:
                    h, m = map(int, time_str.split(':'))
                    period = "AM" if h < 12 else "PM"
                    h_12 = h % 12 if h % 12 != 0 else 12
                    time_str = f"{h_12}:{m:02d} {period}"
                next_break_text = get_translation("next_break", self.settings.language)
                return f"{next_break_text}: {time_str}"
            else:
                return get_translation("status_active", self.settings.language)

        menu = pystray.Menu(
            pystray.MenuItem(get_status_text, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(get_translation("tray_trigger_now", self.settings.language), lambda: self._call_in_tk(self.trigger_overlay)),
            pystray.MenuItem(
                lambda text: get_translation("tray_resume", self.settings.language) if self.settings.paused else get_translation("tray_pause", self.settings.language),
                self._toggle_pause
            ),
            pystray.Menu.SEPARATOR,
            # Quick Actions submenu
            pystray.MenuItem(get_translation("menu_quick_actions", self.settings.language), pystray.Menu(
                pystray.MenuItem(get_translation("menu_skip_next", self.settings.language), lambda: self._call_in_tk(self._skip_next_break)),
                pystray.MenuItem(get_translation("menu_break_in_5", self.settings.language), lambda: self._call_in_tk(lambda: self._snooze_break(5))),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(get_translation("menu_pause_30", self.settings.language), lambda: self._call_in_tk(lambda: self._pause_for_duration(30))),
                pystray.MenuItem(get_translation("menu_pause_60", self.settings.language), lambda: self._call_in_tk(lambda: self._pause_for_duration(60))),
                pystray.MenuItem(get_translation("menu_pause_120", self.settings.language), lambda: self._call_in_tk(lambda: self._pause_for_duration(120))),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(get_translation("menu_reset_schedule", self.settings.language), lambda: self._call_in_tk(self._reset_schedule)),
            )),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(get_translation("tray_daily_progress", self.settings.language), lambda: self._call_in_tk(self.open_body_map)),
            pystray.MenuItem(get_translation("tray_open_settings", self.settings.language), lambda: self._call_in_tk(self.open_settings)),
            pystray.Menu.SEPARATOR,
            # Help submenu
            pystray.MenuItem(get_translation("tray_help", self.settings.language), pystray.Menu(
                pystray.MenuItem(get_translation("tray_about", self.settings.language), lambda: self._call_in_tk(self.show_about_dialog)),
            )),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(get_translation("tray_quit", self.settings.language), self._quit),
        )
        # Platform-specific click handling
        import platform

        def on_clicked(icon, item):
            """Handle clicks - platform-specific behavior"""
            if platform.system() == 'Darwin':  # macOS
                # On macOS, clicking the icon should open settings
                if str(item) == "Open Settings" or item is None:
                    self._call_in_tk(self.open_settings)
            elif platform.system() == 'Linux':  # Linux
                # On Linux, left-click opens settings, right-click shows menu
                if str(item) == APP_NAME or item is None:
                    self._call_in_tk(self.open_settings)
            else:  # Windows
                # On Windows, left-click opens settings, right-click shows menu
                if str(item) == APP_NAME or item is None:
                    self._call_in_tk(self.open_settings)

        # Create icon with platform-appropriate behavior
        if platform.system() == 'Darwin':
            # macOS: menu bar icon, menu opens on left-click
            self._tray = pystray.Icon(
                APP_NAME,
                image,
                f"{APP_NAME} - Stay active while coding!",
                menu
            )
        elif platform.system() == 'Linux':
            # Linux: GNOME has fundamental issues with clickable system tray
            # Use a combination of approaches for maximum compatibility
            print(f"[Linux] Setting up GNOME-compatible system access...")

            # Try AppIndicator first, but don't rely on it being clickable
            try:
                self._setup_linux_appindicator(image, menu)
                print(f"[Linux] AppIndicator created (may not be clickable in GNOME)")
            except Exception as e:
                print(f"[Linux] AppIndicator failed ({e}), using pystray fallback...")
                self._tray = pystray.Icon(
                    APP_NAME,
                    image,
                    f"{APP_NAME} - Stay active while coding!",
                    menu
                )

            # Always setup alternative access methods regardless of tray success
            self._setup_linux_alternatives()
        else:
            # Windows: system tray icon, menu on right-click
            self._tray = pystray.Icon(
                APP_NAME,
                image,
                f"{APP_NAME} - Stay active while coding!",
                menu
            )
            # Add double-click to open settings on Windows
            self._tray.default = lambda: self._call_in_tk(self.open_settings)

        # Start scheduler
        self._scheduler.start()

        # Start automatic version checking
        self._version_checker.check_for_updates_async()

        # Start tray in a thread; keep Tk mainloop on main thread
        t = threading.Thread(target=self._tray.run, daemon=True)
        t.start()

        self.root.mainloop()

    def _call_in_tk(self, fn):
        self.root.after(0, fn)

    def _toggle_pause(self, icon, item):
        # pystray passes (icon, item)
        def do():
            self.settings.paused = not self.settings.paused
            save_settings(self.settings)
            # Update the menu to reflect new state
            self._update_tray_menu()
        self._call_in_tk(do)

    def _update_tray_menu(self):
        """Recreate the tray menu to update dynamic text."""
        if self._tray:
            def get_status_text(item=None):
                if self._pause_until and datetime.now() < self._pause_until:
                    minutes_left = int((self._pause_until - datetime.now()).total_seconds() / 60)
                    paused_for_text = get_translation("paused_for_minutes", self.settings.language)
                    return paused_for_text.format(minutes=minutes_left)
                elif self.settings.paused:
                    return get_translation("status_paused", self.settings.language)
                elif self._skip_next:
                    return get_translation("next_break_skipped", self.settings.language)
                elif self._scheduler.next_fire:
                    time_str = self._scheduler.next_fire.strftime('%H:%M')
                    # Format based on user preference
                    if not self.settings.time_format_24h:
                        h, m = map(int, time_str.split(':'))
                        period = "AM" if h < 12 else "PM"
                        h_12 = h % 12 if h % 12 != 0 else 12
                        time_str = f"{h_12}:{m:02d} {period}"
                    next_break_text = get_translation("next_break", self.settings.language)
                    return f"{next_break_text}: {time_str}"
                else:
                    return get_translation("status_active", self.settings.language)

            # Build help submenu items, only About option
            help_items = [
                pystray.MenuItem(get_translation("tray_about", self.settings.language), lambda: self._call_in_tk(self.show_about_dialog)),
            ]

            menu = pystray.Menu(
                pystray.MenuItem(get_status_text, None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(get_translation("tray_trigger_now", self.settings.language), lambda: self._call_in_tk(self.trigger_overlay)),
                pystray.MenuItem(
                    lambda text: get_translation("tray_resume", self.settings.language) if self.settings.paused else get_translation("tray_pause", self.settings.language),
                    self._toggle_pause
                ),
                pystray.Menu.SEPARATOR,
                # Quick Actions submenu
                pystray.MenuItem(get_translation("menu_quick_actions", self.settings.language), pystray.Menu(
                    pystray.MenuItem(get_translation("menu_skip_next", self.settings.language), lambda: self._call_in_tk(self._skip_next_break)),
                    pystray.MenuItem(get_translation("menu_break_in_5", self.settings.language), lambda: self._call_in_tk(lambda: self._snooze_break(5))),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(get_translation("menu_pause_30", self.settings.language), lambda: self._call_in_tk(lambda: self._pause_for_duration(30))),
                    pystray.MenuItem(get_translation("menu_pause_60", self.settings.language), lambda: self._call_in_tk(lambda: self._pause_for_duration(60))),
                    pystray.MenuItem(get_translation("menu_pause_120", self.settings.language), lambda: self._call_in_tk(lambda: self._pause_for_duration(120))),
                    pystray.Menu.SEPARATOR,
                    pystray.MenuItem(get_translation("menu_reset_schedule", self.settings.language), lambda: self._call_in_tk(self._reset_schedule)),
                )),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(get_translation("tray_daily_progress", self.settings.language), lambda: self._call_in_tk(self.open_body_map)),
                pystray.MenuItem(get_translation("tray_open_settings", self.settings.language), lambda: self._call_in_tk(self.open_settings)),
                pystray.Menu.SEPARATOR,
                # Help submenu
                pystray.MenuItem(
                    get_translation("tray_help", self.settings.language),
                    pystray.Menu(*help_items)
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(get_translation("tray_quit", self.settings.language), self._quit),
            )
            # Handle both pystray and AppIndicator menu updates
            if hasattr(self._tray, 'menu'):
                # pystray
                self._tray.menu = menu
                self._tray.update_menu()
            elif hasattr(self._tray, 'set_menu'):
                # AppIndicator - convert pystray menu to GTK
                try:
                    gtk_menu = self._create_gtk_menu_from_pystray(menu)
                    self._tray.set_menu(gtk_menu)
                    self._gtk_menu = gtk_menu  # Keep reference
                except Exception as e:
                    print(f"[Linux] Failed to update AppIndicator menu: {e}")

    def open_body_map(self):
        """Open the body map viewer window"""
        # Check if body map window is already open
        if self._body_map_window and hasattr(self._body_map_window, 'root'):
            try:
                # Bring existing window to front
                self._body_map_window.root.lift()
                self._body_map_window.root.focus_force()
                return
            except tk.TclError:
                # Window was destroyed, clear reference
                self._body_map_window = None

        try:
            # Create and show body map window
            self._body_map_window = BodyMapWindow(self.root, self.settings.theme, self.settings.language)

            # Override the close handling to clear our reference
            if hasattr(self._body_map_window, 'root'):
                body_window_root = self._body_map_window.root
                def enhanced_close():
                    self._body_map_window = None
                    body_window_root.destroy()
                body_window_root.protocol("WM_DELETE_WINDOW", enhanced_close)

        except Exception as e:
            logging.error(f"[App] Failed to open body map: {e}")
            # Check if error_body_map translation exists, otherwise use a default message
            error_msg = "Failed to open body map: {error}".format(error=str(e))
            messagebox.showerror(get_translation("error_title", self.language), error_msg)

    def open_settings(self):
        # Check if settings window is already open
        if self._settings_window and hasattr(self._settings_window, 'win'):
            try:
                # Bring existing window to front
                self._settings_window.win.lift()
                self._settings_window.win.focus_force()
                return
            except tk.TclError:
                # Window was destroyed, clear reference
                self._settings_window = None

        def on_save(new_settings: Settings):
            self.settings = new_settings
            # Update language in message generator if it changed
            self._lm.language = new_settings.language
            # Only update generator language if it exists
            if hasattr(self._lm, 'generator') and self._lm.generator is not None:
                self._lm.generator.language = new_settings.language
                # Refresh exercise pools with new position preference
                self._lm.generator.initialize_pools()
            # Recalculate next break time when settings change
            self._scheduler.recalculate_next_fire()
            # Update tray menu to show new time
            self._update_tray_menu()
            logging.info(f"[App] Settings saved, recalculated next break time")

        def on_close():
            # Clear reference when window closes
            self._settings_window = None

        # Create settings window with close callback
        self._settings_window = SettingsWindow(self.root, self.settings, on_save, self._autostart_is_enabled, self._autostart_set)

        # Override the _on_close method to clear our reference
        original_on_close = self._settings_window._on_close
        def enhanced_on_close():
            original_on_close()
            self._settings_window = None
        self._settings_window._on_close = enhanced_on_close

    def show_about_dialog(self):
        """Show About dialog with app information"""
        import webbrowser

        about_window = tk.Toplevel(self.root)
        about_window.title(get_translation("about_title", self.settings.language))
        about_window.geometry("450x420")
        about_window.resizable(False, False)

        theme = get_theme(self.settings.theme)
        about_window.configure(bg=theme.background)

        # App icon and name
        title_frame = tk.Frame(about_window, bg=theme.background)
        title_frame.pack(pady=20)

        app_name = tk.Label(
            title_frame,
            text=APP_NAME,
            font=("Segoe UI", 20, "bold"),
            fg=theme.accent,
            bg=theme.background
        )
        app_name.pack()

        version_label = tk.Label(
            title_frame,
            text=f"{get_translation('version', self.settings.language)}: {__version__}",
            font=("Segoe UI", 11),
            fg=theme.text_secondary,
            bg=theme.background
        )
        version_label.pack(pady=(5, 0))

        # Description
        desc_text = get_translation("about_description", self.settings.language)
        desc_label = tk.Label(
            about_window,
            text=desc_text,
            font=("Segoe UI", 10),
            fg=theme.text_primary,
            bg=theme.background,
            wraplength=400,
            justify=tk.CENTER
        )
        desc_label.pack(pady=20)

        # Website link
        website_frame = tk.Frame(about_window, bg=theme.background)
        website_frame.pack(pady=5)

        website_label = tk.Label(
            website_frame,
            text="Website:",
            font=("Segoe UI", 10),
            fg=theme.text_primary,
            bg=theme.background
        )
        website_label.pack(side=tk.LEFT, padx=(0, 5))

        website_link = tk.Label(
            website_frame,
            text="gitfit.dev",
            font=("Segoe UI", 10, "underline"),
            fg=theme.accent_secondary,
            bg=theme.background,
            cursor="hand2"
        )
        website_link.pack(side=tk.LEFT)
        website_link.bind("<Button-1>", lambda e: webbrowser.open("https://gitfit.dev"))

        # GitHub link
        github_frame = tk.Frame(about_window, bg=theme.background)
        github_frame.pack(pady=5)

        github_label = tk.Label(
            github_frame,
            text=get_translation("github_repo", self.settings.language) + ":",
            font=("Segoe UI", 10),
            fg=theme.text_primary,
            bg=theme.background
        )
        github_label.pack(side=tk.LEFT, padx=(0, 5))

        github_link = tk.Label(
            github_frame,
            text="GitHub",
            font=("Segoe UI", 10, "underline"),
            fg=theme.accent_secondary,
            bg=theme.background,
            cursor="hand2"
        )
        github_link.pack(side=tk.LEFT)
        github_link.bind("<Button-1>", lambda e: webbrowser.open(__github_repo__))

        # Version check status
        self.version_status_label = tk.Label(
            about_window,
            text="",  # Empty initially, will be populated after version check
            font=("Segoe UI", 9),
            fg=theme.text_secondary,
            bg=theme.background
        )
        self.version_status_label.pack(pady=10)

        # Check for updates button
        try:
            check_btn_text = get_translation("about_check_version", self.settings.language)
        except Exception:
            check_btn_text = "Check for Latest Version"

        check_btn = tk.Button(
            about_window,
            text=check_btn_text,
            command=lambda: self.check_version_async(self.version_status_label),
            bg=theme.accent,
            fg=theme.background,
            font=("Segoe UI", 10),
            padx=20,
            pady=5
        )
        check_btn.pack(pady=10)

        # OK button
        ok_btn = tk.Button(
            about_window,
            text=get_translation("button_ok", self.settings.language),
            command=about_window.destroy,
            bg=theme.text_secondary,
            fg=theme.background,
            font=("Segoe UI", 10),
            padx=30,
            pady=5
        )
        ok_btn.pack(pady=(10, 20))

        # Center window
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (450 // 2)
        y = (about_window.winfo_screenheight() // 2) - (420 // 2)
        about_window.geometry(f"450x420+{x}+{y}")

        # Auto-check version on open
        self.check_version_async(self.version_status_label)

    def open_github(self):
        """Open GitHub repository in browser"""
        import webbrowser
        webbrowser.open(__github_repo__)

    def check_version_async(self, status_label):
        """Check for updates asynchronously"""
        import threading

        # Show checking status immediately
        try:
            checking_text = get_translation("version_checking", self.settings.language)
        except Exception:
            checking_text = "Checking for updates..."
        status_label.config(text=checking_text)

        def check():
            try:
                import urllib.request
                import json

                # Get current version safely
                try:
                    from .version import __version__ as current_version
                except ImportError:
                    # Fallback for installed versions
                    current_version = "1.0.3"

                # Get GitHub API URL safely
                try:
                    from .version import __github_api_releases__
                    api_url = __github_api_releases__
                except ImportError:
                    # Fallback for installed versions
                    api_url = "https://api.github.com/repos/JozefJarosciak/GitFit.dev-public/releases/latest"

                # Get latest release from GitHub
                with urllib.request.urlopen(api_url, timeout=5) as response:
                    data = json.loads(response.read())
                    latest_version = data.get('tag_name', '').lstrip('v')

                    if latest_version:
                        current = current_version.split('.')
                        latest = latest_version.split('.')

                        # Compare versions
                        is_newer = False
                        for i in range(min(len(current), len(latest))):
                            if int(latest[i]) > int(current[i]):
                                is_newer = True
                                break
                            elif int(latest[i]) < int(current[i]):
                                break

                        # Update label in main thread
                        def update_label():
                            try:
                                if is_newer:
                                    status_label.config(
                                        text=get_translation("update_available", self.settings.language).format(version=latest_version),
                                        fg=get_theme(self.settings.theme).accent
                                    )
                                else:
                                    status_label.config(
                                        text=get_translation("up_to_date", self.settings.language),
                                        fg=get_theme(self.settings.theme).text_secondary
                                    )
                            except Exception:
                                # Fallback text if translation fails
                                if is_newer:
                                    status_label.config(text=f"Update available: v{latest_version}")
                                else:
                                    status_label.config(text="You are running the latest version.")

                        self.root.after(0, update_label)
                    else:
                        def update_error():
                            status_label.config(text=get_translation("update_check_failed", self.settings.language))
                        self.root.after(0, update_error)

            except Exception as e:
                def update_error():
                    status_label.config(text=get_translation("update_check_failed", self.settings.language))
                self.root.after(0, update_error)

        thread = threading.Thread(target=check, daemon=True)
        thread.start()

    def check_for_updates(self):
        """Check for updates and show result in a simple dialog"""
        check_window = tk.Toplevel(self.root)
        check_window.title(get_translation("check_updates_title", self.settings.language))
        check_window.geometry("400x200")
        check_window.resizable(False, False)

        theme = get_theme(self.settings.theme)
        check_window.configure(bg=theme.background)

        # Status label
        status_label = tk.Label(
            check_window,
            text=get_translation("checking_updates", self.settings.language) + "...",
            font=("Segoe UI", 11),
            fg=theme.text_primary,
            bg=theme.background
        )
        status_label.pack(pady=30)

        # OK button
        ok_btn = tk.Button(
            check_window,
            text=get_translation("button_ok", self.settings.language),
            command=check_window.destroy,
            bg=theme.accent,
            fg=theme.background,
            font=("Segoe UI", 10),
            padx=30,
            pady=5
        )
        ok_btn.pack(pady=10)

        # Center window
        check_window.update_idletasks()
        x = (check_window.winfo_screenwidth() // 2) - (350 // 2)
        y = (check_window.winfo_screenheight() // 2) - (150 // 2)
        check_window.geometry(f"350x150+{x}+{y}")

        # Check version
        self.check_version_async(status_label)

    def show_pre_warning(self, seconds_remaining):
        """Show a pre-warning toast notification."""
        logging.info(f"[App] show_pre_warning called with {seconds_remaining} seconds")

        # Block pre-warning functionality if disclaimer not accepted
        if not self.settings.disclaimer_accepted:
            logging.info("[App] Pre-warning blocked - disclaimer not accepted")
            return

        def on_break_now():
            # User wants to take break immediately
            logging.info("[Toast] User clicked 'Take break now'")
            self._scheduler.trigger_now()

        def on_snooze():
            # User wants to snooze for 5 minutes
            logging.info("[Toast] User clicked 'Snooze 5 min'")
            self._scheduler.snooze(5)

        def on_timeout():
            # Pre-warning timed out, break will start
            logging.info("[Toast] Pre-warning timeout - break will start")
            pass

        # Dismiss any existing toast
        if self._toast:
            try:
                self._toast._dismiss()
            except:
                pass

        # Show new toast with current theme
        message = get_translation("toast_time_to_move", self.settings.language)
        try:
            # Use flash mode if enabled
            if self.settings.pre_warning_flash:
                flash_duration = getattr(self.settings, 'pre_warning_flash_duration', 3)
                self._toast = ToastNotification(
                    self.root,
                    message,
                    seconds_remaining,
                    on_break_now=None,  # No buttons in flash mode
                    on_snooze=None,
                    on_timeout=on_timeout,
                    theme_id=self.settings.theme,
                    flash_mode=True,
                    flash_duration=flash_duration
                )
                logging.info(f"[Toast] Flash notification created with theme: {self.settings.theme}, duration: {flash_duration}s")
            else:
                self._toast = ToastNotification(
                    self.root,
                    message,
                    seconds_remaining,
                    on_break_now=on_break_now,
                    on_snooze=on_snooze,
                    on_timeout=on_timeout,
                    theme_id=self.settings.theme,
                    flash_mode=False
                )
                logging.info(f"[Toast] Full notification created with theme: {self.settings.theme}")
        except Exception as e:
            logging.error(f"[Toast] Error creating notification: {e}")

    def trigger_overlay(self):
        with self._lock:
            # Block break functionality if disclaimer not accepted
            if not self.settings.disclaimer_accepted:
                logging.info("[App] Break blocked - disclaimer not accepted")
                return

            # Check if this break should be skipped
            if self._skip_next:
                self._skip_next = False  # Reset flag
                self._scheduler.recalculate_next_fire()  # Schedule next break
                self._update_tray_menu()
                logging.info("[App] Skipped scheduled break")
                return

            # Check if we're in a temporary pause
            if self._pause_until and datetime.now() < self._pause_until:
                logging.info("[App] Break skipped due to temporary pause")
                return

            # Dismiss any toast if present
            if self._toast:
                try:
                    self._toast._dismiss()
                except:
                    pass
                self._toast = None

            msg = self._lm.generate_combined_message(break_seconds=self.settings.lock_seconds, count_break=True)
            dismiss_text = self._lm.get_dismiss_button_text()
            # Never use flash mode for the main break overlay - we want countdown
            Overlay(self.root, msg, self.settings.lock_seconds, dismiss_text, on_done=lambda: None, theme_id=self.settings.theme, flash_mode=False, count_break=True, language=self.settings.language)

    def _skip_next_break(self):
        """Skip the next scheduled break."""
        self._skip_next = True
        self._update_tray_menu()
        logging.info("[App] Next break will be skipped")

    def _snooze_break(self, minutes):
        """Reschedule the next break to occur in X minutes."""
        if self._scheduler.next_fire:
            self._scheduler.next_fire = datetime.now() + timedelta(minutes=minutes)
            self._skip_next = False  # Clear skip flag if set
            self._update_tray_menu()
            logging.info(f"[App] Break snoozed for {minutes} minutes")

    def _pause_for_duration(self, minutes):
        """Pause breaks for a specific duration."""
        self._pause_until = datetime.now() + timedelta(minutes=minutes)
        self.settings.paused = True
        save_settings(self.settings)
        self._update_tray_menu()

        # Schedule a resume after the duration
        self.root.after(minutes * 60 * 1000, self._resume_from_temp_pause)
        logging.info(f"[App] Paused for {minutes} minutes")

    def _resume_from_temp_pause(self):
        """Resume from temporary pause."""
        self._pause_until = None
        self.settings.paused = False
        save_settings(self.settings)
        self._scheduler.recalculate_next_fire()
        self._update_tray_menu()
        logging.info("[App] Resumed from temporary pause")

    def _reset_schedule(self):
        """Reset the break schedule to start fresh."""
        self._skip_next = False
        self._pause_until = None
        if self.settings.paused:
            self.settings.paused = False
            save_settings(self.settings)
        self._scheduler.recalculate_next_fire()
        self._update_tray_menu()
        logging.info("[App] Schedule reset")

    def _show_disclaimer(self):
        """Show mandatory liability disclaimer dialog."""
        def on_accept():
            # User accepted the disclaimer
            self._disclaimer_accepted = True
            self.settings.disclaimer_accepted = True
            self.settings.disclaimer_version = "1.0"
            save_settings(self.settings)
            logging.info("[App] User accepted liability disclaimer")

        def on_decline():
            # User declined the disclaimer, app will exit
            self._disclaimer_accepted = False
            logging.info("[App] User declined liability disclaimer")

        # Show the disclaimer dialog
        disclaimer = DisclaimerDialog(self.root, on_accept, on_decline, self.settings.language)
        disclaimer.show()

    def _quit(self, *args):
        def do_quit():
            self._cleanup_on_exit()
            self.root.quit()
        self._call_in_tk(do_quit)

    def _cleanup_on_exit(self):
        """Clean up resources and save settings on exit."""
        try:
            self._scheduler.stop()
        except Exception:
            pass
        if self._tray:
            try:
                # Handle both pystray and AppIndicator cleanup
                if hasattr(self._tray, 'stop'):
                    self._tray.stop()  # pystray
                elif hasattr(self._tray, 'set_status'):
                    # AppIndicator - set to passive
                    import gi
                    gi.require_version('AppIndicator3', '0.1')
                    from gi.repository import AppIndicator3
                    self._tray.set_status(AppIndicator3.IndicatorStatus.PASSIVE)
            except Exception:
                pass

        # Clean up temporary icon file if using AppIndicator
        if hasattr(self, '_temp_icon_path'):
            try:
                import os
                os.unlink(self._temp_icon_path)
            except:
                pass

        # Stop autosave timer
        if self._settings_autosave_timer:
            try:
                self.root.after_cancel(self._settings_autosave_timer)
            except:
                pass

        # Save settings
        try:
            save_settings(self.settings)
            logging.info("[App] Settings saved on exit")
        except Exception as e:
            logging.error(f"[App] Failed to save settings on exit: {e}")

    def _handle_update_available(self, release_info):
        """Handle when a new version is available"""
        try:
            version = release_info.get('version', 'Unknown')
            url = release_info.get('url', '')

            # Show toast notification about update
            if self._toast:
                message = f"GitFit.dev v{version} is available! Check the tray menu to download."
                self._toast.show_toast(
                    title="Update Available",
                    msg=message,
                    duration=8,
                    threaded=True,
                    callback_on_click=lambda: self._open_update_url(url)
                )

            # Store update info for tray menu
            self._update_info = release_info

            # Update tray menu to show update notification
            self._call_in_tk(self._update_tray_menu)

        except Exception as e:
            logging.error(f"[App] Error handling update notification: {e}")

    def _open_update_url(self, url):
        """Open update URL in default browser"""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as e:
            logging.error(f"[App] Error opening update URL: {e}")

    def _download_update(self):
        """Handle download update action"""
        if self._update_info:
            url = self._update_info.get('download_url', self._update_info.get('url', ''))
            self._open_update_url(url)
        else:
            self.check_for_updates()

    def _start_autosave(self):
        """Start periodic settings autosave."""
        def autosave():
            try:
                with self._lock:
                    save_settings(self.settings)
                logging.debug("[App] Settings autosaved")
            except Exception as e:
                logging.error(f"[App] Autosave failed: {e}")
            # Schedule next autosave in 5 minutes
            self._settings_autosave_timer = self.root.after(300000, autosave)

        # Initial autosave in 5 minutes
        self._settings_autosave_timer = self.root.after(300000, autosave)

    # --- Start on Login helpers (best-effort per OS) ---
    def _autostart_label(self):
        return "GitFitDev"

    def _is_frozen(self) -> bool:
        return getattr(sys, "frozen", False)

    def _autostart_command(self):
        if sys.platform.startswith("win"):
            if self._is_frozen():
                # Check if running from installed location
                exe_path = sys.executable
                # Common install locations for Windows installer
                program_files_paths = [
                    os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'GitFit.dev', 'GitFitBreaks.exe'),
                    os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'GitFit.dev', 'GitFitBreaks.exe'),
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'GitFit.dev', 'GitFitBreaks.exe'),
                ]

                # Check if current exe is in one of the installed locations
                for install_path in program_files_paths:
                    if os.path.exists(install_path):
                        # Use the installed exe path
                        return f'"{install_path}"'

                # Otherwise use the current executable
                return f'"{exe_path}"'
            else:
                return f'"{sys.executable}" -m gitfitdev.app'
        elif sys.platform == "darwin":
            if self._is_frozen():
                return [sys.executable]
            else:
                return [sys.executable, "-m", "gitfitdev.app"]
        else:
            if self._is_frozen():
                return f'"{sys.executable}"'
            else:
                return f'"{sys.executable}" -m gitfitdev.app'

    def _autostart_is_enabled(self) -> bool:
        try:
            if sys.platform.startswith("win"):
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as k:
                    try:
                        val, _ = winreg.QueryValueEx(k, self._autostart_label())
                    except FileNotFoundError:
                        return False
                    # Check if the registered path exists and points to a valid executable
                    # Don't do exact match because paths may differ
                    return isinstance(val, str) and ("GitFit" in val or "gitfitdev" in val)
            elif sys.platform == "darwin":
                plist = os.path.expanduser("~/Library/LaunchAgents/com.gitfit.breaks.plist")
                return os.path.exists(plist)
            else:
                p = os.path.expanduser("~/.config/autostart/GitFitDev.desktop")
                return os.path.exists(p)
        except Exception:
            return False

    def _autostart_set(self, enabled: bool):
        try:
            if sys.platform.startswith("win"):
                import winreg
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as k:
                    if enabled:
                        winreg.SetValueEx(k, self._autostart_label(), 0, winreg.REG_SZ, self._autostart_command())
                    else:
                        try:
                            winreg.DeleteValue(k, self._autostart_label())
                        except FileNotFoundError:
                            pass
            elif sys.platform == "darwin":
                plist_path = os.path.expanduser("~/Library/LaunchAgents/com.gitfit.breaks.plist")
                if enabled:
                    args = self._autostart_command()
                    if isinstance(args, str):
                        args_list = [args]
                    else:
                        args_list = args
                    os.makedirs(os.path.dirname(plist_path), exist_ok=True)
                    plist = (
                        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                        "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
                        "<plist version=\"1.0\"><dict>\n"
                        "  <key>Label</key><string>com.gitfit.breaks</string>\n"
                        "  <key>ProgramArguments</key><array>\n"
                        + "\n".join(f"    <string>{x}</string>" for x in args_list) +
                        "\n  </array>\n"
                        "  <key>RunAtLoad</key><true/>\n"
                        "</dict></plist>\n"
                    )
                    with open(plist_path, "w", encoding="utf-8") as f:
                        f.write(plist)
                    try:
                        subprocess.run(["launchctl", "unload", "-w", plist_path], check=False)
                        subprocess.run(["launchctl", "load", "-w", plist_path], check=False)
                    except Exception:
                        pass
                else:
                    try:
                        subprocess.run(["launchctl", "unload", "-w", plist_path], check=False)
                    except Exception:
                        pass
                    try:
                        os.remove(plist_path)
                    except FileNotFoundError:
                        pass
            else:
                # Linux autostart .desktop
                desktop_dir = os.path.expanduser("~/.config/autostart")
                os.makedirs(desktop_dir, exist_ok=True)
                desktop_file = os.path.join(desktop_dir, "GitFitDev.desktop")
                if enabled:
                    cmd = self._autostart_command()
                    if isinstance(cmd, list):
                        exec_cmd = " ".join(cmd)
                    else:
                        exec_cmd = cmd
                    content = (
                        "[Desktop Entry]\n"
                        "Type=Application\n"
                        "Name=GitFit.dev\n"
                        f"Exec={exec_cmd}\n"
                        "X-GNOME-Autostart-enabled=true\n"
                    )
                    with open(desktop_file, "w", encoding="utf-8") as f:
                        f.write(content)
                else:
                    try:
                        os.remove(desktop_file)
                    except FileNotFoundError:
                        pass
        except Exception:
            pass


def write_pid_file():
    """Write current process ID to a file."""
    pid_file = os.path.expanduser("~/.gitfitdev/app.pid")
    try:
        os.makedirs(os.path.dirname(pid_file), exist_ok=True)
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))

        def cleanup_pid():
            try:
                os.remove(pid_file)
            except:
                pass
        atexit.register(cleanup_pid)
        logging.info(f"[App] PID file written: {os.getpid()}")
    except Exception as e:
        logging.warning(f"Failed to write PID file: {e}")


def check_pid_file():
    """Check if a previous instance is still running via PID file."""
    pid_file = os.path.expanduser("~/.gitfitdev/app.pid")
    try:
        with open(pid_file, 'r') as f:
            old_pid = int(f.read().strip())

        # Check if process is still running
        if sys.platform.startswith("win"):
            # Windows: Use tasklist to check if PID exists
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {old_pid}"],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if str(old_pid) in result.stdout:
                    return True  # Process is running
            except:
                pass
        else:
            # Unix: Send signal 0 to check if process exists
            try:
                os.kill(old_pid, 0)
                return True  # Process exists
            except OSError:
                pass  # Process doesn't exist

        # PID file is stale, remove it
        logging.info(f"[App] Removing stale PID file for PID {old_pid}")
        os.remove(pid_file)
    except (FileNotFoundError, ValueError, OSError):
        pass
    return False


def check_socket_lock(port=52847):
    """Try to bind to a local socket as a cross-platform single-instance check."""
    try:
        global _lock_socket
        _lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _lock_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        _lock_socket.bind(('127.0.0.1', port))
        _lock_socket.listen(1)

        # Keep socket alive for app lifetime
        def cleanup_socket():
            try:
                _lock_socket.close()
            except:
                pass
        atexit.register(cleanup_socket)
        logging.info(f"[App] Socket lock acquired on port {port}")
        return True
    except (OSError, socket.error) as e:
        # Port is already bound - another instance is running
        logging.info(f"[App] Socket lock failed on port {port}: {e}")
        return False


def ensure_single_instance():
    """Ensure only one instance of the application is running using multiple methods."""
    # Check if another instance is already running via PID file
    if check_pid_file():
        logging.info("[App] Another instance detected via PID file")
        return False

    # Try socket-based lock (works on all platforms)
    if not check_socket_lock():
        logging.info("[App] Another instance detected via socket lock")
        return False

    # Write PID file for this instance
    write_pid_file()

    # Also use platform-specific methods for extra safety
    if sys.platform.startswith("win"):
        # Windows: Use a named mutex
        mutex_name = "Global\\GitFitDev_E3D7F8A1-2C4B-4D5E-9F1A-B2C3D4E5F6A7"
        try:
            global _app_mutex  # Keep mutex handle alive for app lifetime
            _app_mutex = kernel32.CreateMutexW(None, False, mutex_name)
            if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
                kernel32.CloseHandle(_app_mutex)
                # Try to find and activate existing window
                try:
                    import ctypes.wintypes
                    user32 = ctypes.windll.user32
                    # Find window by class name or title
                    hwnd = user32.FindWindowW(None, "GitFit.dev Settings")
                    if not hwnd:
                        hwnd = user32.FindWindowW(None, "GitFit Break!")
                    if hwnd:
                        # Bring existing window to front
                        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                        user32.SetForegroundWindow(hwnd)
                except:
                    pass
                return False
            return True
        except Exception as e:
            logging.warning(f"Failed to create mutex: {e}")
            return True  # Allow running if mutex creation fails
    else:
        # Unix/Linux/Mac: Use a lock file with pid
        import fcntl
        import atexit
        import signal

        lock_file = os.path.expanduser("~/.gitfitdev/app.lock")
        os.makedirs(os.path.dirname(lock_file), exist_ok=True)

        try:
            global _lock_fd  # Keep file descriptor alive
            _lock_fd = open(lock_file, "w")
            fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            _lock_fd.write(str(os.getpid()))
            _lock_fd.flush()

            # Register cleanup
            def cleanup():
                try:
                    fcntl.flock(_lock_fd, fcntl.LOCK_UN)
                    _lock_fd.close()
                    os.remove(lock_file)
                except:
                    pass
            atexit.register(cleanup)

            # Also cleanup on signals
            for sig in [signal.SIGTERM, signal.SIGINT]:
                signal.signal(sig, lambda s, f: (cleanup(), sys.exit(0)))

            return True
        except (IOError, OSError) as e:
            # Check if the PID in lock file is still running
            try:
                with open(lock_file, "r") as f:
                    old_pid = int(f.read().strip())
                # Check if process exists
                os.kill(old_pid, 0)
                return False  # Process is still running
            except (ValueError, OSError, IOError):
                # Lock file is stale, remove it and try again
                try:
                    os.remove(lock_file)
                    return ensure_single_instance()  # Recursive call to try again
                except:
                    return False


def main():
    # Check for command line arguments
    show_settings = False
    toggle_pause = False

    if len(sys.argv) > 1:
        if "--show-settings" in sys.argv:
            show_settings = True
        elif "--toggle-pause" in sys.argv:
            toggle_pause = True

    # Check for single instance
    if not ensure_single_instance():
        from .config import load_settings
        from .translations import get_translation

        try:
            settings = load_settings()
            language = settings.language
        except:
            language = "en"

        # Handle commands for existing instance
        if toggle_pause:
            # Signal existing instance to toggle pause via file
            try:
                control_dir = os.path.expanduser("~/.gitfitdev/control")
                os.makedirs(control_dir, exist_ok=True)
                toggle_file = os.path.join(control_dir, "toggle_pause")
                with open(toggle_file, 'w') as f:
                    f.write("")
                print("Toggle pause signal sent to existing instance.")
                sys.exit(0)
            except Exception as e:
                print(f"Failed to signal existing instance: {e}")

        if show_settings:
            # Signal existing instance to show settings via file
            try:
                control_dir = os.path.expanduser("~/.gitfitdev/control")
                os.makedirs(control_dir, exist_ok=True)
                settings_file = os.path.join(control_dir, "show_settings")
                with open(settings_file, 'w') as f:
                    f.write("")
                print("Show settings signal sent to existing instance.")
                sys.exit(0)
            except Exception as e:
                print(f"Failed to signal existing instance: {e}")

        error_msg = get_translation("error_already_running", language)
        # Replace placeholder with app name
        error_msg = error_msg.format(app_name=APP_NAME)
        print(error_msg)

        # Show GUI error message if possible
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # Hide main window
            messagebox.showwarning(
                get_translation("warning_title", language),
                error_msg
            )
            root.destroy()
        except:
            pass

        sys.exit(0)

    app = MoveReminderApp()

    # Handle command line flags
    if show_settings:
        def open_settings_delayed():
            import time
            time.sleep(2)  # Wait for app to fully initialize
            if app.root:
                app.root.after(100, app.open_settings)

        import threading
        threading.Thread(target=open_settings_delayed, daemon=True).start()

    elif toggle_pause:
        def toggle_pause_delayed():
            import time
            time.sleep(2)  # Wait for app to fully initialize
            if app.root:
                app.root.after(100, lambda: app._toggle_pause(None, None))

        import threading
        threading.Thread(target=toggle_pause_delayed, daemon=True).start()

    app.start()


if __name__ == "__main__":
    main()
