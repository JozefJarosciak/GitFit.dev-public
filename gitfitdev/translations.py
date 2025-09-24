"""
Translations bridge for backward compatibility
This module redirects to the new language manager system
"""

from typing import Dict
from dataclasses import dataclass
from .language_manager import (
    get_translation as _get_translation,
    get_available_languages as _get_available_languages
)

@dataclass
class Language:
    """Language data class"""
    code: str
    name: str
    native_name: str

# For backward compatibility
LANGUAGES = {
    "en": Language("en", "English", "English"),
    "sk": Language("sk", "Slovak", "Slovenčina"),
}

# Re-export the main translation function
def get_translation(key: str, language: str = "en", fallback: str = None) -> str:
    """Get a translation for a key (backward compatibility wrapper)"""
    return _get_translation(key, language, fallback)

def get_language_display(lang_code: str) -> str:
    """Get display name for a language code"""
    languages = _get_available_languages()
    return languages.get(lang_code, lang_code)

def get_available_languages() -> Dict[str, Language]:
    """Get available languages"""
    return LANGUAGES

def get_language_display_name(lang_code: str) -> str:
    """Get display name for a language (alias for get_language_display)"""
    return get_language_display(lang_code)

# For compatibility with existing code that might import TRANSLATIONS directly
# This creates a dynamic proxy that fetches translations on demand
class TranslationProxy:
    def __init__(self, lang_code: str):
        self.lang_code = lang_code

    def __getitem__(self, key: str):
        return _get_translation(key, self.lang_code)

    def get(self, key: str, default=None):
        result = _get_translation(key, self.lang_code, None)
        return result if result != key else default

# Create proxy objects for backward compatibility
TRANSLATIONS = {
    "en": TranslationProxy("en"),
    "sk": TranslationProxy("sk"),
}