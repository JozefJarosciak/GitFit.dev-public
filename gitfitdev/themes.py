"""Theme configurations for GitFit.dev overlay."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class Theme:
    """Color theme configuration."""
    background: str      # Main background color
    text_primary: str    # Main text color
    text_secondary: str  # Secondary text color
    accent: str         # Accent color for countdown
    accent_secondary: str  # Secondary accent for headers
    name: str           # Display name


# Available themes
THEMES: Dict[str, Theme] = {
    "green": Theme(
        background="#047857",  # Even darker green for WCAG compliance
        text_primary="#ffffff",
        text_secondary="#a7f3d0",
        accent="#fde047",  # Bright yellow for stretch
        accent_secondary="#fbbf24",  # Golden amber for exercise
        name="Fresh Green"
    ),
    "blue": Theme(
        background="#1e40af",  # Darker blue for better contrast
        text_primary="#ffffff",
        text_secondary="#bfdbfe",
        accent="#fde047",  # Bright yellow for stretch
        accent_secondary="#f472b6",  # Pink for exercise
        name="Ocean Blue"
    ),
    "purple": Theme(
        background="#6b21a8",  # Darker purple for better contrast
        text_primary="#ffffff",
        text_secondary="#e9d5ff",
        accent="#fde047",  # Bright yellow for stretch
        accent_secondary="#86efac",  # Light green for exercise
        name="Royal Purple"
    ),
    "dark": Theme(
        background="#111827",  # Darker background
        text_primary="#f9fafb",
        text_secondary="#d1d5db",
        accent="#34d399",  # Bright green for stretch
        accent_secondary="#fbbf24",  # Golden yellow for exercise
        name="Dark Mode"
    ),
    "sunset": Theme(
        background="#dc2626",  # Red-orange for better contrast
        text_primary="#ffffff",
        text_secondary="#fecaca",
        accent="#fde047",  # Bright yellow for stretch
        accent_secondary="#a3e635",  # Lime green for better contrast
        name="Sunset Orange"
    ),
    "pink": Theme(
        background="#be185d",  # Darker pink for better contrast
        text_primary="#ffffff",
        text_secondary="#fce7f3",
        accent="#fde047",  # Bright yellow for stretch
        accent_secondary="#67e8f9",  # Light cyan for exercise
        name="Energy Pink"
    ),
    "teal": Theme(
        background="#0f766e",  # Darker teal for better contrast
        text_primary="#ffffff",
        text_secondary="#99f6e4",
        accent="#fde047",  # Bright yellow for stretch
        accent_secondary="#fbbf24",  # Golden amber for better contrast
        name="Calm Teal"
    ),
    "indigo": Theme(
        background="#4338ca",  # Darker indigo for better contrast
        text_primary="#ffffff",
        text_secondary="#c7d2fe",
        accent="#fde047",  # Bright yellow for stretch
        accent_secondary="#f9a8d4",  # Light pink for exercise
        name="Deep Indigo"
    ),
    "red": Theme(
        background="#991b1b",  # Darker red for better contrast
        text_primary="#ffffff",
        text_secondary="#fecaca",
        accent="#fde047",  # Bright yellow for stretch
        accent_secondary="#67e8f9",  # Light cyan for exercise
        name="Power Red"
    ),
    "forest": Theme(
        background="#14532d",  # Much darker forest green
        text_primary="#ffffff",
        text_secondary="#bbf7d0",
        accent="#fde047",  # Bright yellow for stretch
        accent_secondary="#f0abfc",  # Light fuchsia for exercise
        name="Forest Green"
    )
}


def get_theme(theme_id: str) -> Theme:
    """Get theme by ID, with fallback to green."""
    return THEMES.get(theme_id, THEMES["green"])