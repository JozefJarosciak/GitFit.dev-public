"""
Fitness translations bridge for backward compatibility
This module redirects to the new language manager system
"""

from typing import List
from .language_manager import (
    get_fitness_translation,
    translate_stretch,
    translate_exercise,
    translate_motivation,
    get_dismiss_buttons
)

# Re-export for backward compatibility
__all__ = [
    'get_fitness_translation',
    'translate_stretch',
    'translate_exercise',
    'translate_motivation',
    'get_dismiss_buttons'
]