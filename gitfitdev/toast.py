"""Toast notification for pre-warning."""

import tkinter as tk
from typing import Callable, Optional
import logging
from .themes import THEMES, Theme
from .translations import get_translation
from .config import load_settings


class ToastNotification:
    """A themed toast notification that appears in the corner."""

    def __init__(self, root: tk.Tk, message: str, countdown: int,
                 on_break_now: Optional[Callable] = None,
                 on_snooze: Optional[Callable] = None,
                 on_timeout: Optional[Callable] = None,
                 theme_id: str = "dark",
                 flash_mode: bool = False,
                 flash_duration: int = 3,
                 language: str = None):
        self.root = root
        self.message = message
        self.countdown = countdown
        self.on_break_now = on_break_now
        self.on_snooze = on_snooze
        self.on_timeout = on_timeout
        self.remaining = countdown
        self.dismissed = False
        self.theme = THEMES.get(theme_id, THEMES["dark"])
        self.flash_mode = flash_mode
        self.flash_duration = flash_duration

        # Get language for translations
        if language is None:
            settings = load_settings()
            self.language = settings.language
        else:
            self.language = language

        # Create toast window
        self.win = tk.Toplevel(root)
        self.win.title(get_translation("app_name", self.language))
        self.win.overrideredirect(True)  # No title bar
        self.win.attributes("-topmost", True)

        # Set transparency
        self.win.attributes("-alpha", 0.0)  # Start invisible for fade-in

        # Configure window size and position
        if flash_mode:
            width = 350  # Increased from 280 for better text fit
            height = 90  # Slightly taller
        else:
            width = 320
            height = 120

        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Position in bottom-right corner with padding
        if flash_mode:
            # Center horizontally, slightly above center vertically
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2 - 100
        else:
            padding = 20
            x = screen_width - width - padding
            y = screen_height - height - padding - 50  # Extra padding for taskbar

        self.win.geometry(f"{width}x{height}+{x}+{y}")

        # Apply theme colors
        self.win.configure(bg=self.theme.background)

        # Create rounded corner effect with frame
        main_frame = tk.Frame(self.win, bg=self.theme.background, padx=15, pady=10)
        main_frame.pack(fill="both", expand=True)

        # Header with app branding and close button
        header_frame = tk.Frame(main_frame, bg=self.theme.background)
        header_frame.pack(fill="x", pady=(0, 5))

        # App icon and title (more compact)
        title_frame = tk.Frame(header_frame, bg=self.theme.background)
        title_frame.pack(side="left")

        # Fitness emoji icon (smaller)
        icon_label = tk.Label(
            title_frame,
            text="🏃",
            font=("Segoe UI Emoji", 16),
            fg=self.theme.accent,
            bg=self.theme.background
        )
        icon_label.pack(side="left", padx=(0, 8))

        # Title and message in one line
        title_label = tk.Label(
            title_frame,
            text=get_translation("app_name", self.language),
            font=("Segoe UI", 11, "bold"),
            fg=self.theme.text_primary,
            bg=self.theme.background
        )
        title_label.pack(side="left")

        if flash_mode:
            tk.Label(
                title_frame,
                text=get_translation("toast_subtitle_reminder", self.language),
                font=("Segoe UI", 10),
                fg=self.theme.accent,
                bg=self.theme.background
            ).pack(side="left")
        else:
            tk.Label(
                title_frame,
                text=get_translation("toast_subtitle_coming", self.language),
                font=("Segoe UI", 10),
                fg=self.theme.text_secondary,
                bg=self.theme.background
            ).pack(side="left")

        # Close button - hide in flash mode
        if not flash_mode:
            close_frame = tk.Frame(header_frame, bg=self.theme.background)
            close_frame.pack(side="right", fill="y")

            close_btn = tk.Button(
                close_frame,
                text="✕",
                font=("Segoe UI", 10),
                fg=self.theme.text_secondary,
                bg=self.theme.background,
                bd=0,
                padx=5,
                pady=2,
                cursor="hand2",
                command=self._dismiss,
                activebackground=self.theme.background
            )
            close_btn.pack()

        # Countdown section (more compact)
        self.countdown_frame = tk.Frame(main_frame, bg=self.theme.background)
        self.countdown_frame.pack(fill="x", pady=(5, 5))

        # Inline countdown with message
        countdown_container = tk.Frame(self.countdown_frame, bg=self.theme.background)
        countdown_container.pack()

        if flash_mode:
            # For flash mode, show message with static time info (no countdown)
            # Use the initial countdown value, not the remaining time
            if countdown <= 60:
                time_text = f"{countdown} seconds"
            else:
                minutes = countdown // 60
                time_text = f"{minutes} minute{'s' if minutes != 1 else ''}"

            flash_msg = f"Break coming in {time_text}!"
            self.msg_label = tk.Label(
                countdown_container,
                text=flash_msg,
                font=("Segoe UI", 12, "bold"),  # Slightly larger for readability
                fg=self.theme.accent,
                bg=self.theme.background,
                wraplength=320  # Wrap text if needed
            )
            self.msg_label.pack()
        else:
            # Normal mode with countdown
            self.msg_label = tk.Label(
                countdown_container,
                text=message,
                font=("Segoe UI", 10),
                fg=self.theme.text_primary,
                bg=self.theme.background
            )
            self.msg_label.pack(side="left")

            # Countdown display for normal mode only
            self.countdown_label = tk.Label(
                countdown_container,
                text=f" {self.remaining}s",
                font=("Segoe UI", 14, "bold"),
                fg=self.theme.accent,
                bg=self.theme.background
            )
            self.countdown_label.pack(side="left")

        # Action buttons - hide in flash mode
        if not flash_mode:
            btn_frame = tk.Frame(main_frame, bg=self.theme.background)
            btn_frame.pack(fill="x", pady=(3, 0))

            # Simplified button creation
            def create_button(parent, text, command, is_primary=False):
                btn = tk.Button(
                    parent,
                    text=text,
                    font=("Segoe UI", 9, "bold" if is_primary else "normal"),
                    fg=self.theme.background if is_primary else self.theme.text_primary,
                    bg=self.theme.accent if is_primary else self._darken_color(self.theme.background),
                    bd=0,
                    padx=12,
                    pady=4,
                    cursor="hand2",
                    command=command,
                    activebackground=self._lighten_color(
                        self.theme.accent if is_primary else self._darken_color(self.theme.background)
                    )
                )
                return btn

            # Create buttons
            if on_break_now:
                break_btn = create_button(btn_frame, "Start now", self._break_now, is_primary=True)
                break_btn.pack(side="left", padx=(0, 8))

            if on_snooze:
                snooze_btn = create_button(btn_frame, "Snooze", self._snooze)
                snooze_btn.pack(side="left")

        # Start countdown
        if flash_mode:
            # Auto-dismiss after configured duration
            self.win.after(self.flash_duration * 1000, self._dismiss)
        else:
            self._tick()

        # Fade in animation
        self._fade_in()

    def _lighten_color(self, color: str) -> str:
        """Lighten a hex color by 20%."""
        if color.startswith("#"):
            color = color[1:]

        # Handle 3-char hex codes
        if len(color) == 3:
            color = ''.join([c*2 for c in color])

        try:
            r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            r = min(255, int(r + (255 - r) * 0.2))
            g = min(255, int(g + (255 - g) * 0.2))
            b = min(255, int(b + (255 - b) * 0.2))
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color

    def _darken_color(self, color: str) -> str:
        """Darken a hex color by 20%."""
        if color.startswith("#"):
            color = color[1:]

        # Handle 3-char hex codes
        if len(color) == 3:
            color = ''.join([c*2 for c in color])

        try:
            r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            r = max(0, int(r * 0.8))
            g = max(0, int(g * 0.8))
            b = max(0, int(b * 0.8))
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color

    def _fade_in(self):
        """Animate the toast appearing with slide and fade."""
        self.alpha = 0.0
        self.slide_offset = 50

        # Get current position
        geometry = self.win.geometry()
        plus_index = geometry.index('+')
        x_index = geometry.index('+', plus_index + 1)
        original_y = int(geometry[x_index + 1:])
        x_pos = int(geometry[plus_index + 1:x_index])
        size = geometry[:plus_index]

        def animate():
            if self.alpha < 0.95 and not self.dismissed:
                self.alpha += 0.05
                self.slide_offset = max(0, self.slide_offset - 3)

                try:
                    self.win.attributes("-alpha", self.alpha)
                    self.win.geometry(f"{size}+{x_pos}+{original_y + self.slide_offset}")
                    self.win.after(20, animate)
                except:
                    pass  # Window might be destroyed

        animate()

    def _fade_out(self, callback=None):
        """Animate the toast disappearing with slide and fade."""
        # Don't check dismissed here - we're already dismissing
        self.alpha = self.win.attributes("-alpha")

        def animate():
            if self.alpha > 0:
                self.alpha -= 0.1

                try:
                    self.win.attributes("-alpha", self.alpha)
                    self.win.after(20, animate)
                except:
                    pass  # Window might be destroyed
            else:
                try:
                    self.win.destroy()
                except:
                    pass
                if callback:
                    callback()

        animate()

    def _tick(self):
        """Update countdown."""
        if self.dismissed or self.flash_mode:  # Skip ticking for flash mode
            return

        if self.remaining <= 0:
            if not self.dismissed:
                self._timeout()
            return

        # Update countdown display with new format
        try:
            if hasattr(self, 'countdown_label'):  # Only if countdown label exists
                self.countdown_label.configure(text=f" {self.remaining}s")

                # Add pulsing effect for last 5 seconds (adjusted for smaller size)
                if self.remaining <= 5:
                    # Make text pulse
                    original_size = 14
                    pulse_size = 16
                    self.countdown_label.configure(font=("Segoe UI", pulse_size, "bold"))
                    self.win.after(100, lambda: self.countdown_label.configure(
                        font=("Segoe UI", original_size, "bold")
                    ) if not self.dismissed else None)
        except:
            pass  # Widget might be destroyed

        self.remaining -= 1
        self.win.after(1000, self._tick)

    def _dismiss(self):
        """Dismiss the notification."""
        if self.dismissed:
            return
        self.dismissed = True

        # In flash mode, treat dismiss as timeout
        if self.flash_mode:
            logging.info("[Toast] Flash notification auto-dismissed")
            self._fade_out(self.on_timeout)
        else:
            logging.info("[Toast] Notification dismissed by user")
            self._fade_out()

    def _break_now(self):
        """User wants to take break immediately."""
        if self.dismissed:
            return
        self.dismissed = True
        self._fade_out(self.on_break_now)

    def _snooze(self):
        """User wants to snooze."""
        if self.dismissed:
            return
        self.dismissed = True
        self._fade_out(self.on_snooze)

    def _timeout(self):
        """Countdown reached zero."""
        if self.dismissed:
            return
        self.dismissed = True
        logging.info("[Toast] Countdown complete, dismissing notification")
        self._fade_out(self.on_timeout)