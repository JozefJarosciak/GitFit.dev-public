"""
Enhanced message generation with intelligent exercise distribution and body tracking
"""
import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime, date
import json
import os
from pathlib import Path

from .fitness_data import (
    STRETCHES, EXERCISES,
    MuscleGroup, Exercise, Stretch,
    get_benefits_for_muscle_groups,
    filter_exercises_by_position,
    filter_stretches_by_position
)

class DailyTracker:
    """Track daily exercise coverage for balanced workouts"""

    def __init__(self):
        self.data_dir = Path.home() / '.gitfitdev'
        self.data_dir.mkdir(exist_ok=True)
        self.tracker_file = self.data_dir / 'daily_tracker.json'
        self.load_daily_data()

    def load_daily_data(self):
        """Load or initialize daily tracking data"""
        today = date.today().isoformat()

        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r') as f:
                    self.data = json.load(f)
                    # Check if it's a new day and reset if needed
                    if self.data.get('date') != today:
                        self.data = {
                            'date': today,
                            'muscle_groups_worked': {},
                            'exercises_done': [],
                            'stretches_done': [],
                            'total_breaks': 0,
                            'breaks_completed': 0,
                            'breaks_escaped': 0,
                            'breaks_shown': 0
                        }
                        self.save()
            except:
                self.data = {}
        else:
            self.data = {}

        # Initialize if empty
        if not self.data or 'date' not in self.data:
            self.data = {
                'date': today,
                'muscle_groups_worked': {},
                'exercises_done': [],
                'stretches_done': [],
                'total_breaks': 0,
                'breaks_completed': 0,
                'breaks_escaped': 0,
                'breaks_shown': 0
            }
            self.save()

    def save(self):
        """Save tracking data"""
        with open(self.tracker_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def record_exercise(self, exercise: Exercise):
        """Record an exercise and update muscle group counts"""
        self.data['exercises_done'].append({
            'description': exercise.description,
            'time': datetime.now().isoformat()
        })

        for muscle_group in exercise.muscle_groups:
            mg_name = muscle_group.value
            self.data['muscle_groups_worked'][mg_name] = \
                self.data['muscle_groups_worked'].get(mg_name, 0) + 1

        # Don't increment total_breaks here - it's done in record_break()
        self.save()

    def record_stretch(self, stretch: Stretch):
        """Record a stretch and update muscle group counts"""
        self.data['stretches_done'].append({
            'description': stretch.description,
            'time': datetime.now().isoformat()
        })

        for muscle_group in stretch.muscle_groups:
            mg_name = muscle_group.value
            self.data['muscle_groups_worked'][mg_name] = \
                self.data['muscle_groups_worked'].get(mg_name, 0) + 1

        # Don't increment total_breaks here - it's done in record_break()
        self.save()

    def record_break_shown(self):
        """Record that a break was shown to the user"""
        self.load_daily_data()  # Check if it's a new day
        self.data.setdefault('breaks_shown', 0)
        self.data['breaks_shown'] += 1
        self.data['total_breaks'] += 1  # Keep for backward compatibility
        self.save()

    def record_break_completed(self):
        """Record that a break was completed (user stayed for full duration)"""
        self.load_daily_data()
        self.data.setdefault('breaks_completed', 0)
        self.data['breaks_completed'] += 1
        self.save()

    def record_break_escaped(self):
        """Record that a break was escaped early"""
        self.load_daily_data()
        self.data.setdefault('breaks_escaped', 0)
        self.data['breaks_escaped'] += 1
        self.save()

    def record_break(self):
        """Legacy method - now just records shown"""
        self.record_break_shown()

    def reset_daily_data(self):
        """Manually reset daily tracking data"""
        today = date.today().isoformat()
        self.data = {
            'date': today,
            'muscle_groups_worked': {},
            'exercises_done': [],
            'stretches_done': [],
            'total_breaks': 0,
            'breaks_completed': 0,
            'breaks_escaped': 0,
            'breaks_shown': 0
        }
        self.save()

    def get_least_worked_muscles(self) -> List[MuscleGroup]:
        """Get muscle groups that need more attention"""
        all_muscles = list(MuscleGroup)
        worked = self.data['muscle_groups_worked']

        # Sort by work count (ascending)
        sorted_muscles = sorted(
            all_muscles,
            key=lambda mg: worked.get(mg.value, 0)
        )

        # Return least worked (bottom 50%)
        return sorted_muscles[:len(sorted_muscles)//2]

    def get_coverage_stats(self) -> Dict:
        """Get statistics about today's coverage"""
        total_muscle_groups = len(MuscleGroup)

        # Only count muscle groups based on COMPLETED breaks
        completed = self.data.get('breaks_completed', 0)

        # Clear logic: no completed breaks = no muscle work
        if completed == 0:
            worked_groups = 0
        else:
            # Each completed break works ~2-3 muscle groups
            # Cap at total muscle groups
            estimated_groups = min(completed * 2, total_muscle_groups)
            worked_groups = estimated_groups

        return {
            'total_breaks': completed,  # Show completed count as total
            'breaks_shown': self.data.get('breaks_shown', self.data.get('total_breaks', 0)),
            'breaks_completed': completed,
            'breaks_escaped': self.data.get('breaks_escaped', 0),
            'muscle_groups_covered': worked_groups,
            'total_muscle_groups': total_muscle_groups,
            'coverage_percentage': (worked_groups / total_muscle_groups) * 100 if total_muscle_groups > 0 else 0,
            'exercises_done': len(self.data.get('exercises_done', [])),  # Actual exercise count
            'stretches_done': len(self.data.get('stretches_done', []))   # Actual stretch count
        }

    def get_body_map_data(self) -> Dict[str, int]:
        """Get muscle group work counts for visualization"""
        # Return the actual muscle groups worked data
        return self.data.get('muscle_groups_worked', {})


class SmartMessageGenerator:
    """Generate exercise messages with intelligent distribution"""

    def __init__(self, language: str = "en"):
        self.tracker = DailyTracker()
        self.language = language
        self.last_exercise = None  # Store last generated exercise
        self.last_stretch = None   # Store last generated stretch
        self.initialize_pools()

    def initialize_pools(self):
        """Initialize exercise and stretch pools with position filtering"""
        from .config import load_settings

        settings = load_settings()
        position_preference = getattr(settings, 'position_preference', 'sitting_standing')

        # Apply position filtering
        self.exercise_pool = filter_exercises_by_position(EXERCISES.copy(), position_preference)
        self.stretch_pool = filter_stretches_by_position(STRETCHES.copy(), position_preference)
        # Simple default motivations
        self.motivation_pool = [
            "Nice break! Posture reset complete.",
            "Tiny moves, big wins.",
            "Eyes happy. Neck happy. You got this.",
            "Back thanks you."
        ]

        random.shuffle(self.exercise_pool)
        random.shuffle(self.stretch_pool)
        random.shuffle(self.motivation_pool)

    def record_last_activity_completion(self):
        """Record the last generated exercise or stretch when break is completed"""
        # Record both if both were shown (for "both" activity type)
        if self.last_exercise:
            self.tracker.record_exercise(self.last_exercise)
            self.last_exercise = None  # Clear after recording
        if self.last_stretch:
            self.tracker.record_stretch(self.last_stretch)
            self.last_stretch = None  # Clear after recording

    def get_smart_exercise(self, record_now: bool = False) -> Exercise:
        """Get exercise targeting least-worked muscle groups"""
        least_worked = self.tracker.get_least_worked_muscles()

        # Try to find exercise targeting least-worked muscles
        candidates = [e for e in self.exercise_pool
                     if any(mg in least_worked for mg in e.muscle_groups)]

        if candidates:
            exercise = random.choice(candidates)
        else:
            # Fallback to random if no match
            exercise = random.choice(self.exercise_pool)

        # Only record if explicitly requested (when break is completed)
        if record_now:
            self.tracker.record_exercise(exercise)
        return exercise

    def get_smart_stretch(self, record_now: bool = False) -> Stretch:
        """Get stretch targeting least-worked muscle groups"""
        least_worked = self.tracker.get_least_worked_muscles()

        # Try to find stretch targeting least-worked muscles
        candidates = [s for s in self.stretch_pool
                     if any(mg in least_worked for mg in s.muscle_groups)]

        if candidates:
            stretch = random.choice(candidates)
        else:
            # Fallback to random if no match
            stretch = random.choice(self.stretch_pool)

        # Only record if explicitly requested (when break is completed)
        if record_now:
            self.tracker.record_stretch(stretch)
        return stretch

    def generate_message(self, count_break: bool = True) -> Tuple[str, str, str]:
        """Generate exercise/stretch with related benefit and motivation"""
        # Only record break shown if this is a real break (not a test)
        if count_break:
            self.tracker.record_break_shown()

        # Clear previous activity
        self.last_exercise = None
        self.last_stretch = None

        # Decide between exercise and stretch (60% exercise, 40% stretch)
        if random.random() < 0.6:
            exercise = self.get_smart_exercise()
            self.last_exercise = exercise  # Store for completion recording
            activity = exercise.description
            muscle_groups = exercise.muscle_groups
        else:
            stretch = self.get_smart_stretch()
            self.last_stretch = stretch  # Store for completion recording
            activity = stretch.description
            muscle_groups = stretch.muscle_groups

        # Get related benefit based on muscle groups
        benefits = get_benefits_for_muscle_groups(muscle_groups)
        if benefits:
            benefit = random.choice(benefits)
        else:
            # Fallback to general benefit
            benefit = "Improving overall health and wellness!"

        # Get motivation
        if not self.motivation_pool:
            # Reset motivation pool
            self.motivation_pool = [
                "Nice break! Posture reset complete.",
                "Tiny moves, big wins.",
                "Eyes happy. Neck happy. You got this.",
                "Back thanks you."
            ]
            random.shuffle(self.motivation_pool)
        motivation = self.motivation_pool.pop()
        # Translate if needed
        from .fitness_translations import translate_motivation
        motivation = translate_motivation(motivation, self.language)

        return activity, benefit, motivation

    def get_daily_summary(self) -> str:
        """Get summary of today's activity"""
        stats = self.tracker.get_coverage_stats()

        # Use shared break status description for consistency
        from .body_map import get_break_status_description

        try:
            break_status = get_break_status_description()
            expected_str = f": {break_status}"
        except:
            expected_str = f": {stats['total_breaks']} breaks today"

        summary = f"""Today's Progress:
• Breaks{expected_str}
• Exercises done: {stats['exercises_done']}
• Stretches done: {stats['stretches_done']}
• Muscle coverage: {stats['muscle_groups_covered']}/{stats['total_muscle_groups']} ({stats['coverage_percentage']:.0f}%)"""

        if stats['coverage_percentage'] >= 80:
            summary += "\nExcellent full-body coverage!"
        elif stats['coverage_percentage'] >= 60:
            summary += "\nGood coverage! Keep it up!"
        else:
            summary += "\nBuilding momentum!"

        return summary


# Legacy TinyPhraseLM class for backwards compatibility
class TinyPhraseLM:
    """
    A motivational exercise and stretching message generator for office workers.
    Creates clear, actionable prompts for both stretches and exercises that can be done at a desk.
    Enhanced with smart distribution and body tracking.
    """

    def __init__(self, seed: int | None = None, language: str = "en") -> None:
        self._rng = random.Random(seed)
        # We'll get the generator lazily to avoid circular dependency
        self.generator = None  # Will be set in _get_generator()
        self.language = language
        self.messages_generated = 0
        self.stretch_history = []
        self.exercise_history = []
        self.max_history = 10

        # Legacy data for compatibility
        self.STRETCHES = [s.description for s in STRETCHES[:25]]  # First 25 for compatibility
        self.EXERCISES = [e.description for e in EXERCISES[:25]]  # First 25 for compatibility
        # Simple motivation messages
        self.MOTIVATIONS = [
            "Nice break! Posture reset complete.",
            "Tiny moves, big wins.",
            "Eyes happy. Neck happy. You got this.",
            "Back thanks you."
        ]
        self.BENEFITS = []

    def _get_generator(self):
        """Get the generator, creating or fetching singleton as needed"""
        if self.generator is None:
            # This will be resolved at runtime to avoid circular dependency
            self.generator = get_generator()
            if self.generator.language != self.language:
                self.generator.language = self.language
        return self.generator

    def choice(self, items):
        return self._rng.choice(items)

    def get_unique_item(self, items, history):
        """Get an item that hasn't been used recently."""
        available = [item for item in items if item not in history]

        if not available:
            while len(history) > self.max_history // 2:
                history.pop(0)
            available = [item for item in items if item not in history]

        selected = self.choice(available)
        history.append(selected)
        if len(history) > self.max_history:
            history.pop(0)

        return selected

    def _adjust_duration_in_text(self, text: str, max_duration: int) -> str:
        """Adjust duration in exercise/stretch text based on break duration."""
        import re

        # Handle "X sec each" patterns - divide by 2 for each side
        def replace_each_sec(match):
            seconds = int(match.group(1))
            adjusted = min(seconds, max_duration // 2)
            adjusted = max(3, adjusted)  # Minimum 3 seconds
            return f"{adjusted} sec each"

        text = re.sub(r'(\d+) sec each', replace_each_sec, text)

        # Handle "X seconds each" patterns - divide by 2
        def replace_each_seconds(match):
            seconds = int(match.group(1))
            adjusted = min(seconds, max_duration // 2)
            adjusted = max(3, adjusted)  # Minimum 3 seconds
            return f"{adjusted} seconds each"

        text = re.sub(r'(\d+) seconds each', replace_each_seconds, text)

        # Handle regular "X seconds" patterns
        def replace_seconds(match):
            seconds = int(match.group(1))
            adjusted = min(seconds, max_duration)
            adjusted = max(3, adjusted)  # Minimum 3 seconds
            return f"{adjusted} seconds"

        text = re.sub(r'(\d+) seconds(?! each)', replace_seconds, text)

        # Handle "X-Y seconds" patterns
        def replace_range_seconds(match):
            low = int(match.group(1))
            high = int(match.group(2))
            adj_high = min(high, max_duration)
            adj_low = min(low, adj_high - 5, max_duration - 10)
            adj_low = max(3, adj_low)
            adj_high = max(adj_low + 5, adj_high)
            return f"{adj_low}-{adj_high} seconds"

        text = re.sub(r'(\d+)-(\d+) seconds', replace_range_seconds, text)

        # Handle "X times each" patterns - divide by 2
        def replace_each_times(match):
            times = int(match.group(1))
            # Calculate time per rep (assume 2 seconds per rep)
            total_time = times * 2
            if total_time > max_duration // 2:
                adjusted_times = max(3, max_duration // 4)  # 2 seconds per rep, divided by 2 for each side
                return f"{adjusted_times} times each"
            return match.group(0)

        text = re.sub(r'(\d+) times each', replace_each_times, text)

        # Handle regular "X times" patterns
        def replace_times(match):
            times = int(match.group(1))
            # Calculate time per rep (assume 2 seconds per rep)
            total_time = times * 2
            if total_time > max_duration:
                adjusted_times = max(3, max_duration // 2)
                return f"{adjusted_times} times"
            return match.group(0)

        text = re.sub(r'(\d+) times(?! each)', replace_times, text)

        # Handle "hold X sec" patterns (both with and without 'onds')
        text = re.sub(r'hold (\d+) sec(?:onds?)?(?:\b|,)',
                     lambda m: f'hold {min(int(m.group(1)), max_duration)} sec,', text)

        return text

    def get_unique_stretch(self, max_duration: int = 20):
        """Get a stretch using smart distribution"""
        generator = self._get_generator()
        stretch = generator.get_smart_stretch()
        # Store for later recording when break completes
        generator.last_stretch = stretch
        # Don't clear last_exercise here - we might have both

        # Translate first, then adjust duration
        from .fitness_translations import translate_stretch
        translated = translate_stretch(stretch.description, self.language)
        return self._adjust_duration_in_text(translated, max_duration)

    def get_unique_exercise(self, max_duration: int = 20):
        """Get an exercise using smart distribution"""
        generator = self._get_generator()
        exercise = generator.get_smart_exercise()
        # Store for later recording when break completes
        generator.last_exercise = exercise
        # Don't clear last_stretch here - we might have both

        # Translate first, then adjust duration
        from .fitness_translations import translate_exercise
        translated = translate_exercise(exercise.description, self.language)
        return self._adjust_duration_in_text(translated, max_duration)

    def generate_stretch_message(self, count_break: bool = False, break_seconds: int = 30) -> str:
        """Generate a stretching-focused message."""
        safe_duration = max(5, break_seconds - 10)
        stretch = self.get_unique_stretch(safe_duration)
        activity, benefit, motivation = self.generator.generate_message(count_break=count_break)

        formats = [
            f"Time to stretch!\n\n{stretch}\n\n{motivation}",
            f"Stretching break:\n\n{stretch}\n\nBenefit: {benefit}",
            f"Release the tension:\n\n{stretch}\n\n{motivation}",
            f"Stretch it out!\n\n{stretch}\n\n{benefit}",
            f"Your stretch:\n\n{stretch}\n\n{motivation}",
        ]

        return self.choice(formats)

    def generate_exercise_message(self, count_break: bool = False, break_seconds: int = 30) -> str:
        """Generate an exercise-focused message."""
        safe_duration = max(5, break_seconds - 10)
        exercise = self.get_unique_exercise(safe_duration)
        activity, benefit, motivation = self.generator.generate_message(count_break=count_break)

        formats = [
            f"Time for movement!\n\n{exercise}\n\n{motivation}",
            f"Exercise time!\n\n{exercise}\n\nBenefit: {benefit}",
            f"Your exercise:\n\n{exercise}\n\n{motivation}",
            f"Get moving!\n\n{exercise}\n\n{benefit}",
            f"Break activity:\n\n{exercise}\n\n{motivation}",
        ]

        return self.choice(formats)

    def generate_combined_message(self, break_seconds: int = 60, count_break: bool = True) -> str:
        """Generate a message based on user's activity type preference and break duration."""
        from .config import load_settings
        from .fitness_translations import translate_motivation, get_fitness_translation

        settings = load_settings()
        activity_type = getattr(settings, 'activity_type', 'both')

        # Track break if needed (this also generates and stores the activity)
        if count_break:
            generator = self._get_generator()
            generator.tracker.record_break_shown()

        # Get a random motivation and translate it
        motivation = self.choice(self.MOTIVATIONS)
        motivation = translate_motivation(motivation, self.language)

        if break_seconds < 60:
            # For breaks under 1 minute, alternate between stretch and exercise (don't show both)
            if activity_type == "both":
                # Alternate between stretch and exercise
                if hasattr(self, '_last_activity'):
                    next_activity = "exercise" if self._last_activity == "stretch" else "stretch"
                else:
                    next_activity = "stretch"  # Start with stretch
                self._last_activity = next_activity
            elif activity_type == "stretch":
                next_activity = "stretch"
            elif activity_type == "exercise":
                next_activity = "exercise"
            else:
                next_activity = "stretch"  # Default fallback

            if next_activity == "stretch":
                stretch = self.get_unique_stretch(break_seconds)
                # Clear exercise since we're only showing stretch
                generator = self._get_generator()
                generator.last_exercise = None
                # Translation already done in get_unique_stretch
                return {
                    'title': get_fitness_translation('time_to_stretch', self.language),
                    'single_activity': stretch,
                    'motivation': motivation
                }
            else:
                exercise = self.get_unique_exercise(break_seconds)
                # Clear stretch since we're only showing exercise
                generator = self._get_generator()
                generator.last_stretch = None
                # Translation already done in get_unique_exercise
                return {
                    'title': get_fitness_translation('movement_time', self.language),
                    'single_activity': exercise,
                    'motivation': motivation
                }
        else:
            # For breaks 1+ minutes, split time between activities based on preference
            if activity_type == "stretch":
                stretch = self.get_unique_stretch(break_seconds)
                # Clear exercise since we're only showing stretch
                generator = self._get_generator()
                generator.last_exercise = None
                # Translation already done in get_unique_stretch
                return {
                    'title': get_fitness_translation('time_to_stretch', self.language),
                    'single_activity': stretch,
                    'motivation': motivation
                }
            elif activity_type == "exercise":
                exercise = self.get_unique_exercise(break_seconds)
                # Clear stretch since we're only showing exercise
                generator = self._get_generator()
                generator.last_stretch = None
                # Translation already done in get_unique_exercise
                return {
                    'title': get_fitness_translation('movement_time', self.language),
                    'single_activity': exercise,
                    'motivation': motivation
                }
            else:  # activity_type == "both"
                # Split time between both activities
                half_time = break_seconds // 2
                stretch = self.get_unique_stretch(half_time)
                exercise = self.get_unique_exercise(half_time)

                # Translation already done in get_unique_stretch and get_unique_exercise

                return {
                    'title': get_fitness_translation('wellness_break', self.language),
                    'stretch_header': get_fitness_translation('stretch_header', self.language),
                    'stretch_text': stretch,
                    'exercise_header': get_fitness_translation('exercise_header', self.language),
                    'exercise_text': exercise,
                    'motivation': motivation
                }

    def sentence(self, count_break: bool = True) -> str:
        """Generate a random break message with smart distribution."""
        activity, benefit, motivation = self.generator.generate_message(count_break=count_break)

        # Add daily summary every 5th break
        self.messages_generated += 1
        if self.messages_generated % 5 == 0:
            summary = self.generator.get_daily_summary()
            return f"=== MOVEMENT BREAK ===\n\n{activity}\n\nBenefit: {benefit}\n\n{motivation}\n\n--- {summary} ---"

        return f"=== MOVEMENT BREAK ===\n\n{activity}\n\nBenefit: {benefit}\n\n{motivation}"

    def get_dismiss_button_text(self) -> str:
        """Get a funny 1-3 word dismiss button text."""
        from .fitness_translations import get_dismiss_buttons

        dismiss_texts = get_dismiss_buttons(self.language)
        return self.choice(dismiss_texts)

    def get_body_map_data(self) -> Dict[str, int]:
        """Get muscle group work counts for visualization"""
        return self.generator.tracker.get_body_map_data()


# Module-level instance for easy access
_default_generator = None

def get_generator() -> SmartMessageGenerator:
    """Get the default message generator instance"""
    global _default_generator
    if _default_generator is None:
        _default_generator = SmartMessageGenerator()
    return _default_generator

def generate_message(include_emojis: bool = True, count_break: bool = True) -> str:
    """Generate a movement break message"""
    generator = get_generator()
    activity, benefit, motivation = generator.generate_message(count_break=count_break)

    # Format message
    parts = []

    # Add header
    if include_emojis:
        if 'stretch' in activity.lower():
            parts.append("STRETCH BREAK")
        else:
            parts.append("MOVEMENT BREAK")
    else:
        parts.append("=== MOVEMENT BREAK ===")

    parts.append("")
    parts.append(activity)
    parts.append("")
    parts.append(f"Benefit: {benefit}")
    parts.append("")
    parts.append(motivation)

    return "\n".join(parts)

def get_daily_summary() -> str:
    """Get today's activity summary"""
    return get_generator().get_daily_summary()

def get_body_visualization_data() -> Dict:
    """Get data for body map visualization"""
    generator = get_generator()
    return {
        'muscle_work_counts': generator.tracker.get_body_map_data(),
        'coverage_stats': generator.tracker.get_coverage_stats()
    }

# For testing
if __name__ == "__main__":
    # Test message generation
    print("Testing Smart Message Generation\n" + "="*50)

    generator = SmartMessageGenerator()

    # Generate 10 test messages
    for i in range(10):
        activity, benefit, motivation = generator.generate_message()
        print(f"\n--- Message {i+1} ---")
        print(f"Activity: {activity}")
        print(f"Benefit: {benefit}")
        print(f"Motivation: {motivation}")

    # Show daily summary
    print("\n" + "="*50)
    print(generator.get_daily_summary())

    # Show body map data
    print("\n" + "="*50)
    print("Body Map Data:")
    body_data = generator.tracker.get_body_map_data()
    for muscle, count in sorted(body_data.items(), key=lambda x: x[1], reverse=True):
        print(f"  {muscle}: {'█' * count} ({count})")