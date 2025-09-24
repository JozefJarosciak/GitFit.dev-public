import json
import os
import threading
from dataclasses import dataclass, asdict
from datetime import time


def _home_dir() -> str:
    # Cross-platform user home
    return os.path.expanduser("~")


def _config_dir() -> str:
    base = os.path.join(_home_dir(), ".gitfitdev")
    return base


def _config_path() -> str:
    return os.path.join(_config_dir(), "config.json")


def _ensure_dir(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass


@dataclass
class Settings:
    active_from: str = "09:00"   # 24h HH:MM - 9 AM start
    active_to: str = "17:00"     # 24h HH:MM - 5 PM end
    interval_minutes: int = 60    # 1 hour break intervals
    trigger_at_minute: int = 0    # At the top of the hour (break offset)
    lock_seconds: int = 60        # 1 minute break duration (new default)
    activity_type: str = "both"   # "stretch", "exercise", or "both"
    position_preference: str = "sitting_standing"  # "sitting_standing", "all", "sitting", "standing", "lying"
    paused: bool = False
    start_on_login: bool = False
    theme: str = "green"          # Color theme for overlay
    pre_warning: bool = True      # Show warning before break
    pre_warning_seconds: int = 30 # 30 seconds warning
    pre_warning_flash: bool = True  # Use flash notification (auto-close)
    pre_warning_flash_duration: int = 3  # 3 second flash duration
    time_format_24h: bool = True  # Use 24-hour format (False for 12-hour AM/PM)
    disclaimer_accepted: bool = False  # User must accept liability disclaimer
    disclaimer_version: str = "1.0"  # Track disclaimer version for updates
    language: str = "en"  # UI language (en, sk, etc.)
    # Version checking settings
    last_version_check: float = 0  # Last version check timestamp
    latest_known_version: str = ""  # Latest version found during check
    auto_check_updates: bool = True  # Automatically check for updates
    # Note: These are now the production defaults (9-5, 1hr intervals, 30sec breaks)

    def parse_active_from(self) -> time:
        h, m = map(int, self.active_from.split(":", 1))
        return time(hour=h, minute=m)

    def parse_active_to(self) -> time:
        h, m = map(int, self.active_to.split(":", 1))
        return time(hour=h, minute=m)

    def format_time(self, time_str: str) -> str:
        """Format time string based on 12/24 hour preference."""
        if self.time_format_24h:
            return time_str
        else:
            h, m = map(int, time_str.split(":", 1))
            period = "AM" if h < 12 else "PM"
            h_12 = h % 12 if h % 12 != 0 else 12
            return f"{h_12}:{m:02d} {period}"


_lock = threading.Lock()


def get_default_settings() -> Settings:
    """Return default settings for 9-5 workday with 1hr breaks."""
    return Settings(
        active_from="09:00",
        active_to="17:00",
        interval_minutes=60,
        trigger_at_minute=0,
        lock_seconds=60,
        activity_type="both",
        position_preference="sitting_standing",
        paused=False,
        start_on_login=True,
        theme="dark",
        pre_warning=True,
        pre_warning_seconds=30,
        pre_warning_flash=True,
        pre_warning_flash_duration=3,
        time_format_24h=True,
        disclaimer_accepted=False,
        disclaimer_version="1.0",
        language="en"
    )


def load_settings() -> Settings:
    try:
        with _lock:
            path = _config_path()
            if not os.path.exists(path):
                return get_default_settings()
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Handle legacy break_offset_minutes field
            if 'break_offset_minutes' in data and 'trigger_at_minute' not in data:
                data['trigger_at_minute'] = data['break_offset_minutes']
            if 'break_offset_minutes' in data:
                del data['break_offset_minutes']
            # Use default settings as base, override with saved data
            defaults = asdict(get_default_settings())
            return Settings(**{**defaults, **data})
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        # Log error and return defaults for corrupted config
        import logging
        logging.error(f"Config file corrupted, using defaults: {e}")
        return get_default_settings()
    except Exception:
        return get_default_settings()


def save_settings(settings: Settings) -> None:
    with _lock:
        _ensure_dir(_config_dir())
        path = _config_path()
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(asdict(settings), f, indent=2)
        try:
            os.replace(tmp, path)
        except Exception:
            # Fallback copy
            with open(path, "w", encoding="utf-8") as f:
                json.dump(asdict(settings), f, indent=2)
