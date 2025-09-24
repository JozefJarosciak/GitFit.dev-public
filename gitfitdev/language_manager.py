"""
Language Manager for GitFit.dev
Handles loading and switching between language packs
"""

from typing import Dict, List, Optional
import importlib

class LanguageManager:
    """Manages language loading and translation lookups"""

    def __init__(self):
        self.current_language = "en"
        self.languages = {
            "en": "English",
            "sk": "Slovak"
        }
        self.loaded_packs = {}

    def load_language(self, lang_code: str):
        """Load a language pack dynamically"""
        if lang_code not in self.languages:
            raise ValueError(f"Unknown language code: {lang_code}")

        if lang_code not in self.loaded_packs:
            try:
                # Dynamically import the language module
                module_name = f"gitfitdev.lang_{lang_code}"
                module = importlib.import_module(module_name)

                self.loaded_packs[lang_code] = {
                    'ui': getattr(module, 'UI_TRANSLATIONS', {}),
                    'fitness': getattr(module, 'FITNESS_TRANSLATIONS', {}),
                    'exercises': getattr(module, 'EXERCISE_TRANSLATIONS', {}),
                    'stretches': getattr(module, 'STRETCH_TRANSLATIONS', {}),
                    'motivations': getattr(module, 'MOTIVATION_TRANSLATIONS', {}),
                    'dismiss_buttons': getattr(module, 'DISMISS_BUTTONS', []),
                }
            except ImportError as e:
                print(f"Failed to load language pack for {lang_code}: {e}")
                # Fall back to English
                if lang_code != "en":
                    return self.load_language("en")
                raise

        return self.loaded_packs[lang_code]

    def set_language(self, lang_code: str):
        """Set the current language"""
        if lang_code in self.languages:
            self.current_language = lang_code
            self.load_language(lang_code)

    def get_translation(self, key: str, category: str = 'ui', fallback: str = None) -> str:
        """Get a translation for a key"""
        # Ensure current language is loaded
        if self.current_language not in self.loaded_packs:
            self.load_language(self.current_language)

        pack = self.loaded_packs.get(self.current_language, {})
        translations = pack.get(category, {})

        # Try to get translation
        result = translations.get(key)

        # If not found and not English, try English fallback
        if result is None and self.current_language != "en":
            if "en" not in self.loaded_packs:
                self.load_language("en")
            en_pack = self.loaded_packs.get("en", {})
            en_translations = en_pack.get(category, {})
            result = en_translations.get(key)

        # If still not found, use fallback or key
        if result is None:
            result = fallback if fallback is not None else key

        return result

    def get_ui_translation(self, key: str, fallback: str = None) -> str:
        """Get a UI translation"""
        return self.get_translation(key, 'ui', fallback)

    def get_fitness_translation(self, key: str, fallback: str = None) -> str:
        """Get a fitness-specific translation"""
        return self.get_translation(key, 'fitness', fallback)

    def translate_exercise(self, description: str) -> str:
        """Translate an exercise description"""
        if self.current_language == "en":
            return description

        if self.current_language not in self.loaded_packs:
            self.load_language(self.current_language)

        exercises = self.loaded_packs[self.current_language].get('exercises', {})

        # Try exact match first
        if description in exercises:
            return exercises[description]

        # Try pattern matching for dynamic numbers
        import re
        base_pattern = re.sub(r'\d+', 'NUM', description)

        for original, translation in exercises.items():
            if re.sub(r'\d+', 'NUM', original) == base_pattern:
                # Replace numbers from original with numbers from description
                original_nums = re.findall(r'\d+', description)
                translated_with_nums = translation
                for num in original_nums:
                    translated_with_nums = re.sub(r'\d+', num, translated_with_nums, count=1)
                return translated_with_nums

        return description

    def translate_stretch(self, description: str) -> str:
        """Translate a stretch description"""
        if self.current_language == "en":
            return description

        if self.current_language not in self.loaded_packs:
            self.load_language(self.current_language)

        stretches = self.loaded_packs[self.current_language].get('stretches', {})

        # Try exact match first
        if description in stretches:
            return stretches[description]

        # Try pattern matching for dynamic numbers
        import re
        base_pattern = re.sub(r'\d+', 'NUM', description)

        for original, translation in stretches.items():
            if re.sub(r'\d+', 'NUM', original) == base_pattern:
                # Replace numbers from original with numbers from description
                original_nums = re.findall(r'\d+', description)
                translated_with_nums = translation
                for num in original_nums:
                    translated_with_nums = re.sub(r'\d+', num, translated_with_nums, count=1)
                return translated_with_nums

        return description

    def translate_motivation(self, message: str) -> str:
        """Translate a motivational message"""
        if self.current_language == "en":
            return message

        if self.current_language not in self.loaded_packs:
            self.load_language(self.current_language)

        motivations = self.loaded_packs[self.current_language].get('motivations', {})
        return motivations.get(message, message)

    def get_dismiss_buttons(self) -> List[str]:
        """Get dismiss button texts for current language"""
        if self.current_language not in self.loaded_packs:
            self.load_language(self.current_language)

        return self.loaded_packs[self.current_language].get('dismiss_buttons', [])

    def get_available_languages(self) -> Dict[str, str]:
        """Get dictionary of available languages"""
        return self.languages.copy()


# Global instance
_language_manager = LanguageManager()

# Convenience functions for backward compatibility
def set_language(lang_code: str):
    """Set the current language"""
    _language_manager.set_language(lang_code)

def get_translation(key: str, language: str = None, fallback: str = None) -> str:
    """Get a UI translation (backward compatibility)"""
    if language and language != _language_manager.current_language:
        old_lang = _language_manager.current_language
        _language_manager.set_language(language)
        result = _language_manager.get_ui_translation(key, fallback)
        _language_manager.set_language(old_lang)
        return result
    return _language_manager.get_ui_translation(key, fallback)

def get_fitness_translation(key: str, language: str = None, fallback: str = None) -> str:
    """Get a fitness translation (backward compatibility)"""
    if language and language != _language_manager.current_language:
        old_lang = _language_manager.current_language
        _language_manager.set_language(language)
        result = _language_manager.get_fitness_translation(key, fallback)
        _language_manager.set_language(old_lang)
        return result
    return _language_manager.get_fitness_translation(key, fallback)

def translate_exercise(description: str, language: str = None) -> str:
    """Translate an exercise description"""
    if language and language != _language_manager.current_language:
        old_lang = _language_manager.current_language
        _language_manager.set_language(language)
        result = _language_manager.translate_exercise(description)
        _language_manager.set_language(old_lang)
        return result
    return _language_manager.translate_exercise(description)

def translate_stretch(description: str, language: str = None) -> str:
    """Translate a stretch description"""
    if language and language != _language_manager.current_language:
        old_lang = _language_manager.current_language
        _language_manager.set_language(language)
        result = _language_manager.translate_stretch(description)
        _language_manager.set_language(old_lang)
        return result
    return _language_manager.translate_stretch(description)

def translate_motivation(message: str, language: str = None) -> str:
    """Translate a motivational message"""
    if language and language != _language_manager.current_language:
        old_lang = _language_manager.current_language
        _language_manager.set_language(language)
        result = _language_manager.translate_motivation(message)
        _language_manager.set_language(old_lang)
        return result
    return _language_manager.translate_motivation(message)

def get_dismiss_buttons(language: str = None) -> List[str]:
    """Get dismiss button texts"""
    if language and language != _language_manager.current_language:
        old_lang = _language_manager.current_language
        _language_manager.set_language(language)
        result = _language_manager.get_dismiss_buttons()
        _language_manager.set_language(old_lang)
        return result
    return _language_manager.get_dismiss_buttons()

def get_available_languages() -> Dict[str, str]:
    """Get available languages"""
    return _language_manager.get_available_languages()