"""
PyQt5-based GitFit.dev application with full video and image support.
"""

import sys
import os
import threading
import random
import subprocess
from datetime import datetime, timedelta
from typing import Optional

# Ensure PyQt5 is installed
def ensure_pyqt5():
    """Auto-install PyQt5 if needed."""
    try:
        from PyQt5 import QtCore, QtWidgets, QtGui
        return True
    except ImportError:
        try:
            print("Installing PyQt5...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5", "Pillow"])
            return True
        except Exception as e:
            print(f"Could not install PyQt5: {e}")
            sys.exit(1)

ensure_pyqt5()

from PyQt5.QtCore import (Qt, QTimer, pyqtSignal, QThread, QUrl, QTime,
                          QSettings, QSize, QRect)
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QSystemTrayIcon, QMenu,
                            QAction, QDialog, QGridLayout, QLineEdit,
                            QCheckBox, QRadioButton, QButtonGroup,
                            QSpinBox, QTimeEdit, QMessageBox, QGroupBox)
from PyQt5.QtGui import (QFont, QPalette, QColor, QIcon, QPixmap, QPainter,
                        QBrush, QPen, QPolygon, QPoint)
# Removed video support - no web engine needed

from .config import load_settings, save_settings, Settings
from .branding import APP_NAME
from .tiny_lm import TinyPhraseLM
# Removed image manager - using emoji icons instead

# Windows mutex for single instance
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


class BreakOverlay(QWidget):
    """Fullscreen break overlay with exercise image."""

    closed = pyqtSignal()

    def __init__(self, message: str, seconds: int, dismiss_text: str, parent=None):
        super().__init__(parent)

        self.message = message
        self.seconds = max(1, seconds)
        self.remaining = self.seconds
        self.dismiss_text = dismiss_text

        # Exercise emojis that rotate
        self.exercise_emojis = [
            "🏃‍♂️", "🏃‍♀️", "🤸‍♂️", "🤸‍♀️", "💪", "🏋️‍♂️", "🏋️‍♀️",
            "🚴‍♂️", "🚴‍♀️", "🧘‍♂️", "🧘‍♀️", "🤾‍♂️", "🤾‍♀️",
            "🏌️‍♂️", "🏌️‍♀️", "⛹️‍♂️", "⛹️‍♀️", "🤺", "🥊", "🥋"
        ]

        self.setup_ui()
        self.show_fullscreen()

    def setup_ui(self):
        """Setup the overlay UI."""
        # Window settings for fullscreen overlay
        self.setWindowFlags(Qt.WindowStaysOnTopHint |
                          Qt.FramelessWindowHint |
                          Qt.Tool)

        # Green background
        self.setStyleSheet("""
            QWidget {
                background-color: #00bb55;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                font-size: 18px;
                font-weight: bold;
                padding: 12px 30px;
                border-radius: 5px;
            }
            QPushButton#dismissBtn {
                background-color: #ee5555;
                color: white;
                border: 2px solid #dd4444;
            }
            QPushButton#dismissBtn:hover {
                background-color: #dd4444;
            }
            QPushButton#videoBtn {
                background-color: #00aa44;
                color: white;
                border: 2px solid #009933;
            }
            QPushButton#videoBtn:hover {
                background-color: #009933;
            }
        """)

        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Exercise message
        msg_label = QLabel(self.message)
        msg_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setMaximumWidth(1000)
        msg_label.setStyleSheet("padding: 20px;")
        layout.addWidget(msg_label)

        # Exercise image
        self.add_image_content(layout)

        # Countdown timer
        self.timer_label = QLabel(str(self.remaining))
        self.timer_label.setFont(QFont("Segoe UI", 72, QFont.Bold))
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("padding: 20px;")
        layout.addWidget(self.timer_label)

        # Instructions
        inst_label = QLabel("Press ESC to dismiss")
        inst_label.setFont(QFont("Segoe UI", 14))
        inst_label.setAlignment(Qt.AlignCenter)
        inst_label.setStyleSheet("color: #eafff3;")
        layout.addWidget(inst_label)

        # Dismiss button
        dismiss_btn = QPushButton(f"🚪 {self.dismiss_text}")
        dismiss_btn.setObjectName("dismissBtn")
        dismiss_btn.clicked.connect(self.close_overlay)
        dismiss_btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(dismiss_btn)

        self.setLayout(layout)

        # Start countdown timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def add_image_content(self, layout):
        """Add exercise emoji icon to layout."""
        # Pick random emoji based on exercise type
        exercise_icon = self.get_exercise_emoji()

        # Create a widget to hold the emoji
        icon_widget = QWidget()
        icon_widget.setFixedSize(400, 300)
        icon_widget.setStyleSheet("""
            QWidget {
                background-color: #009944;
                border-radius: 20px;
                border: 3px solid #007733;
            }
        """)

        icon_layout = QVBoxLayout()

        # Main exercise emoji - HUGE
        emoji_label = QLabel(exercise_icon)
        emoji_label.setFont(QFont("Segoe UI Emoji", 120))
        emoji_label.setAlignment(Qt.AlignCenter)
        emoji_label.setStyleSheet("color: white; padding: 20px;")
        icon_layout.addWidget(emoji_label)

        # Exercise type label
        exercise_type = self.get_exercise_type()
        type_label = QLabel(exercise_type)
        type_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        type_label.setAlignment(Qt.AlignCenter)
        type_label.setStyleSheet("color: white; padding: 10px;")
        icon_layout.addWidget(type_label)

        icon_widget.setLayout(icon_layout)
        layout.addWidget(icon_widget)

    def get_exercise_emoji(self):
        """Get emoji based on exercise in message."""
        message_lower = self.message.lower()

        # Map exercises to specific emojis
        if "squat" in message_lower:
            return random.choice(["🏋️‍♂️", "🏋️‍♀️", "🦵"])
        elif "push" in message_lower:
            return random.choice(["💪", "🤲", "👐"])
        elif "stretch" in message_lower:
            return random.choice(["🧘‍♂️", "🧘‍♀️", "🙆‍♂️", "🙆‍♀️"])
        elif "walk" in message_lower or "march" in message_lower:
            return random.choice(["🚶‍♂️", "🚶‍♀️", "🏃‍♂️", "🏃‍♀️"])
        elif "neck" in message_lower:
            return random.choice(["🙇‍♂️", "🙇‍♀️", "😌"])
        elif "shoulder" in message_lower:
            return random.choice(["🤷‍♂️", "🤷‍♀️", "💪"])
        elif "leg" in message_lower or "calf" in message_lower:
            return random.choice(["🦵", "🦶", "🏃‍♂️"])
        elif "lunge" in message_lower:
            return random.choice(["🤸‍♂️", "🤸‍♀️", "🏋️‍♂️"])
        elif "plank" in message_lower:
            return random.choice(["🛌", "💪", "🏋️‍♂️"])
        else:
            # Random exercise emoji
            return random.choice(self.exercise_emojis)

    def get_exercise_type(self):
        """Get exercise category name."""
        message_lower = self.message.lower()

        if "squat" in message_lower:
            return "SQUATS"
        elif "push" in message_lower:
            return "PUSH-UPS"
        elif "stretch" in message_lower:
            return "STRETCHING"
        elif "walk" in message_lower or "march" in message_lower:
            return "CARDIO"
        elif "neck" in message_lower or "shoulder" in message_lower:
            return "UPPER BODY"
        elif "leg" in message_lower or "calf" in message_lower or "lunge" in message_lower:
            return "LOWER BODY"
        elif "plank" in message_lower:
            return "CORE"
        else:
            return "EXERCISE"

    # Removed video methods - only using images now

    def show_fullscreen(self):
        """Show overlay on all screens."""
        # Get all screens
        screens = QApplication.screens()
        if screens:
            # Show on primary screen
            primary = screens[0]
            geometry = primary.geometry()
            self.setGeometry(geometry)
            self.showFullScreen()

    def update_timer(self):
        """Update countdown."""
        self.remaining -= 1
        self.timer_label.setText(str(self.remaining))

        if self.remaining <= 0:
            self.close_overlay()

    def close_overlay(self):
        """Close the overlay."""
        self.timer.stop()
        self.closed.emit()
        self.close()

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key_Escape:
            self.close_overlay()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self.close_overlay()
        elif event.key() == Qt.Key_Q and event.modifiers() == Qt.ControlModifier:
            self.close_overlay()


class SchedulerThread(QThread):
    """Background thread for scheduling breaks."""

    trigger_break = pyqtSignal()

    def __init__(self, get_settings):
        super().__init__()
        self.get_settings = get_settings
        self.running = True

    def run(self):
        """Run the scheduler."""
        # Wait for first interval
        settings = self.get_settings()
        next_fire = datetime.now() + timedelta(minutes=max(1, settings.interval_minutes))

        while self.running:
            settings = self.get_settings()
            if not settings.paused and self.within_active_hours(settings):
                now = datetime.now()
                if now >= next_fire:
                    self.trigger_break.emit()
                    next_fire = now + timedelta(minutes=max(1, settings.interval_minutes))

            self.msleep(1000)  # Sleep 1 second

    def within_active_hours(self, settings):
        """Check if current time is within active hours."""
        now = datetime.now().time()
        start = settings.parse_active_from()
        end = settings.parse_active_to()

        if start <= end:
            return start <= now <= end
        else:
            # Overnight schedule
            return now >= start or now <= end

    def stop(self):
        """Stop the scheduler."""
        self.running = False


class SettingsDialog(QDialog):
    """Settings dialog window."""

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setup_ui()

    def setup_ui(self):
        """Setup settings UI."""
        self.setWindowTitle(f"{APP_NAME} Settings")
        self.setFixedSize(450, 400)

        layout = QVBoxLayout()

        # Create form
        form_layout = QGridLayout()

        # Active hours
        form_layout.addWidget(QLabel("Active From (HH:MM):"), 0, 0)
        self.from_time = QTimeEdit()
        self.from_time.setDisplayFormat("HH:mm")
        self.from_time.setTime(QTime.fromString(self.settings.active_from, "HH:mm"))
        form_layout.addWidget(self.from_time, 0, 1)

        form_layout.addWidget(QLabel("Active To (HH:MM):"), 1, 0)
        self.to_time = QTimeEdit()
        self.to_time.setDisplayFormat("HH:mm")
        self.to_time.setTime(QTime.fromString(self.settings.active_to, "HH:mm"))
        form_layout.addWidget(self.to_time, 1, 1)

        # Interval
        form_layout.addWidget(QLabel("Interval (minutes):"), 2, 0)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 180)
        self.interval_spin.setValue(self.settings.interval_minutes)
        form_layout.addWidget(self.interval_spin, 2, 1)

        # Lock duration
        form_layout.addWidget(QLabel("Lock Duration (sec):"), 3, 0)
        self.lock_spin = QSpinBox()
        self.lock_spin.setRange(5, 300)
        self.lock_spin.setValue(self.settings.lock_seconds)
        form_layout.addWidget(self.lock_spin, 3, 1)

        # Paused
        self.paused_check = QCheckBox("Paused")
        self.paused_check.setChecked(self.settings.paused)
        form_layout.addWidget(self.paused_check, 4, 1)

        # Removed media type options - only using emoji icons

        layout.addLayout(form_layout)

        # Buttons
        from .translations import get_translation

        button_layout = QHBoxLayout()
        save_btn = QPushButton(get_translation("button_save", self.settings.language))
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton(get_translation("button_cancel", self.settings.language))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def save_settings(self):
        """Save settings and close."""
        self.settings.active_from = self.from_time.time().toString("HH:mm")
        self.settings.active_to = self.to_time.time().toString("HH:mm")
        self.settings.interval_minutes = self.interval_spin.value()
        self.settings.lock_seconds = self.lock_spin.value()
        self.settings.paused = self.paused_check.isChecked()
        # Removed media_type setting

        save_settings(self.settings)
        self.accept()


class GitFitBreaksApp(QWidget):
    """Main application class."""

    def __init__(self):
        super().__init__()

        self.settings = load_settings()
        self.phrase_lm = TinyPhraseLM()
        self.tray_icon = None
        self.scheduler = None

        self.setup_tray()
        self.start_scheduler()

    def setup_tray(self):
        """Setup system tray icon."""
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)

        # Create icon
        icon = self.create_icon()
        self.tray_icon.setIcon(icon)

        # Create menu
        menu = QMenu()

        trigger_action = QAction("Trigger Now", self)
        trigger_action.triggered.connect(self.trigger_break)
        menu.addAction(trigger_action)

        self.pause_action = QAction("Pause" if not self.settings.paused else "Resume", self)
        self.pause_action.triggered.connect(self.toggle_pause)
        menu.addAction(self.pause_action)

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def create_icon(self):
        """Create dumbbell icon."""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw dumbbell
        painter.setPen(QPen(QColor(0, 150, 90), 3))
        painter.setBrush(QBrush(QColor(0, 150, 90)))

        # Bar
        painter.drawRoundedRect(8, 28, 48, 8, 4, 4)

        # Weights
        painter.setBrush(QBrush(QColor(20, 200, 120)))
        painter.drawRoundedRect(4, 20, 10, 24, 3, 3)
        painter.drawRoundedRect(50, 20, 10, 24, 3, 3)

        painter.end()

        return QIcon(pixmap)

    def start_scheduler(self):
        """Start the break scheduler."""
        self.scheduler = SchedulerThread(lambda: self.settings)
        self.scheduler.trigger_break.connect(self.trigger_break)
        self.scheduler.start()

    def trigger_break(self):
        """Show break overlay."""
        message = self.phrase_lm.generate_combined_message()
        dismiss_text = self.phrase_lm.get_dismiss_button_text()

        self.overlay = BreakOverlay(
            message,
            self.settings.lock_seconds,
            dismiss_text
        )
        self.overlay.show()

    def toggle_pause(self):
        """Toggle pause state."""
        self.settings.paused = not self.settings.paused
        save_settings(self.settings)
        self.pause_action.setText("Resume" if self.settings.paused else "Pause")

    def open_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self.settings)
        if dialog.exec_():
            # Settings were saved
            self.settings = load_settings()

    def quit_app(self):
        """Quit the application."""
        if self.scheduler:
            self.scheduler.stop()
            self.scheduler.wait()
        QApplication.quit()


def ensure_single_instance():
    """Ensure only one instance is running."""
    if sys.platform.startswith("win"):
        mutex_name = "Global\\GitFitBreaks_E3D7F8A1-2C4B-4D5E-9F1A-B2C3D4E5F6A7"
        mutex = kernel32.CreateMutexW(None, False, mutex_name)
        if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
            kernel32.CloseHandle(mutex)
            return False
        return True
    return True


def main():
    """Main entry point."""
    if not ensure_single_instance():
        from .translations import get_translation
        from .config import load_settings
        settings = load_settings()
        error_msg = get_translation("error_already_running", settings.language)
        error_msg = error_msg.format(app_name=APP_NAME)
        print(error_msg)
        sys.exit(0)

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setQuitOnLastWindowClosed(False)

    # Create main app
    gitfit = GitFitBreaksApp()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()