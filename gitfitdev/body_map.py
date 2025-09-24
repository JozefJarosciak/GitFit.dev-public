"""
Body map visualization for showing which muscle groups have been exercised
"""
from typing import Dict, List, Optional
from .fitness_data import MuscleGroup
from .tiny_lm import get_body_visualization_data


class BodyMapVisualizer:
    """Generate visual representation of worked muscle groups"""

    def __init__(self):
        self.reset_map()

    def reset_map(self):
        """Initialize empty body map"""
        self.body_map = {
            'front': self._create_front_view(),
            'back': self._create_back_view()
        }

    def _create_front_view(self) -> List[str]:
        """Create ASCII art front view of body"""
        return [
            "     FRONT VIEW     ",
            "                    ",
            "        ___         ",
            "       (o o)        ",  # Head
            "        \\_/         ",
            "         |          ",  # Neck
            "     ___|||___      ",  # Shoulders
            "    /   |||   \\     ",  # Upper arms
            "   |    |||    |    ",  # Chest/Upper back
            "   |    |||    |    ",  # Core
            "   |    |||    |    ",  # Lower core
            "    \\___|||___/     ",  # Hips
            "      ||| |||       ",  # Upper legs
            "      ||| |||       ",  # Thighs
            "      ||| |||       ",  # Lower thighs
            "      ||| |||       ",  # Knees
            "      ||| |||       ",  # Calves
            "     _|||_|||_      ",  # Ankles
            "    /___|___|_\\     ",  # Feet
        ]

    def _create_back_view(self) -> List[str]:
        """Create ASCII art back view of body"""
        return [
            "      BACK VIEW     ",
            "                    ",
            "        ___         ",
            "       (   )        ",  # Head
            "        \\_/         ",
            "         |          ",  # Neck
            "     ___|||___      ",  # Shoulders
            "    /   |||   \\     ",  # Upper arms
            "   |    |||    |    ",  # Upper back
            "   |    |||    |    ",  # Mid back
            "   |    |||    |    ",  # Lower back
            "    \\___|||___/     ",  # Glutes
            "      ||| |||       ",  # Hamstrings
            "      ||| |||       ",  # Hamstrings
            "      ||| |||       ",  # Lower hamstrings
            "      ||| |||       ",  # Knees
            "      ||| |||       ",  # Calves
            "     _|||_|||_      ",  # Ankles
            "    /___|___|_\\     ",  # Heels
        ]

    def generate_intensity_map(self, muscle_work_counts: Dict[str, int]) -> Dict[str, str]:
        """Generate intensity indicators for each muscle group"""
        if not muscle_work_counts:
            return {}

        # Find max count for normalization
        max_count = max(muscle_work_counts.values()) if muscle_work_counts else 1

        intensity_map = {}
        for muscle, count in muscle_work_counts.items():
            if count == 0:
                intensity_map[muscle] = ' '
            elif count <= max_count * 0.25:
                intensity_map[muscle] = '.'  # Light
            elif count <= max_count * 0.5:
                intensity_map[muscle] = 'o'  # Medium
            elif count <= max_count * 0.75:
                intensity_map[muscle] = 'O'  # Heavy
            else:
                intensity_map[muscle] = '#'  # Full

        return intensity_map

    def create_highlighted_view(self, muscle_work_counts: Dict[str, int]) -> str:
        """Create a highlighted body map showing worked muscles"""
        intensity = self.generate_intensity_map(muscle_work_counts)

        # Create muscle group legend
        legend_items = []
        for muscle_group in MuscleGroup:
            count = muscle_work_counts.get(muscle_group.value, 0)
            if count > 0:
                symbol = intensity.get(muscle_group.value, ' ')
                legend_items.append(f"{symbol} {muscle_group.value.replace('_', ' ').title()}: {count}x")

        # Sort legend by count (descending)
        legend_items.sort(key=lambda x: int(x.split(':')[1].replace('x', '')), reverse=True)

        # Build complete visualization
        output = []
        output.append("="*40)
        output.append("      MUSCLE GROUP COVERAGE")
        output.append("="*40)
        output.append("")

        # Add simple text representation
        output.append("Worked Muscle Groups:")
        output.append("-"*20)

        if legend_items:
            for item in legend_items[:10]:  # Show top 10
                output.append(f"  {item}")
        else:
            output.append("  No exercises completed yet today")

        output.append("")

        # Add intensity legend
        output.append("Intensity Legend:")
        output.append("  . Light (1-25%)")
        output.append("  o Medium (26-50%)")
        output.append("  O Heavy (51-75%)")
        output.append("  # Full (76-100%)")

        return "\n".join(output)

    def create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create a progress bar visualization"""
        filled = int(width * percentage / 100)
        empty = width - filled
        return f"[{'#' * filled}{'.' * empty}] {percentage:.0f}%"

    def generate_daily_report(self) -> str:
        """Generate a comprehensive daily progress report"""
        data = get_body_visualization_data()
        muscle_counts = data['muscle_work_counts']
        stats = data['coverage_stats']

        output = []
        output.append("="*50)
        output.append("          DAILY FITNESS REPORT")
        output.append("="*50)
        output.append("")

        # Overall progress
        output.append(f"Total Breaks Completed: {stats['total_breaks']}")
        output.append(f"Exercises Done: {stats['exercises_done']}")
        output.append(f"Stretches Done: {stats['stretches_done']}")
        output.append("")

        # Coverage bar
        output.append("Full Body Coverage:")
        coverage_bar = self.create_progress_bar(stats['coverage_percentage'])
        output.append(f"  {coverage_bar}")
        output.append(f"  {stats['muscle_groups_covered']}/{stats['total_muscle_groups']} muscle groups")
        output.append("")

        # Muscle group breakdown
        if muscle_counts:
            output.append("Muscle Groups Worked Today:")
            output.append("-"*30)

            # Group by body region
            upper_body = ['neck', 'shoulders', 'chest', 'upper_back', 'arms', 'wrists']
            core_region = ['core', 'lower_back']
            lower_body = ['hips', 'glutes', 'quads', 'hamstrings', 'calves', 'ankles']

            regions = {
                'Upper Body': upper_body,
                'Core': core_region,
                'Lower Body': lower_body
            }

            for region_name, muscles in regions.items():
                region_total = sum(muscle_counts.get(m, 0) for m in muscles)
                if region_total > 0:
                    output.append(f"\n{region_name}:")
                    for muscle in muscles:
                        count = muscle_counts.get(muscle, 0)
                        if count > 0:
                            bar_width = min(count * 2, 20)
                            bar = '#' * bar_width
                            muscle_display = muscle.replace('_', ' ').title()
                            output.append(f"  {muscle_display:15} {bar} ({count})")

            # Check for full body exercises
            if muscle_counts.get('full_body', 0) > 0:
                output.append(f"\nFull Body: {muscle_counts['full_body']} exercises")

        # Recommendations
        output.append("")
        output.append("="*50)
        output.append("RECOMMENDATIONS:")

        if stats['coverage_percentage'] < 40:
            output.append("• Keep going! Aim for more variety in muscle groups")
        elif stats['coverage_percentage'] < 70:
            output.append("• Good progress! Try to work some neglected areas")
        else:
            output.append("• Excellent coverage! You're working your whole body")

        # Find least worked muscles
        if muscle_counts:
            all_muscles = set(mg.value for mg in MuscleGroup)
            unworked = all_muscles - set(muscle_counts.keys())
            if unworked:
                output.append(f"• Consider working: {', '.join(list(unworked)[:3]).replace('_', ' ').title()}")

        output.append("="*50)

        return "\n".join(output)

    def get_simple_status(self, language: str = "en") -> str:
        """Get a simple one-line status for display"""
        from .translations import get_translation
        data = get_body_visualization_data()
        stats = data['coverage_stats']

        if stats['total_breaks'] == 0:
            return get_translation("coverage_start", language)

        coverage = stats['coverage_percentage']
        if coverage >= 80:
            emoji = get_translation("status_champion", language)
            status = "Champion"
        elif coverage >= 60:
            emoji = get_translation("status_great", language)
            status = "Great"
        elif coverage >= 40:
            emoji = get_translation("status_good", language)
            status = "Good"
        else:
            emoji = get_translation("status_building", language)
            status = "Building"

        # Calculate expected breaks based on user settings and current time
        from datetime import datetime
        from .config import load_settings

        settings = load_settings()
        try:
            now = datetime.now()
            active_from_time = datetime.strptime(settings.active_from, '%H:%M').time()
            active_to_time = datetime.strptime(settings.active_to, '%H:%M').time()

            # Create datetime objects for today's work hours
            today = now.date()
            active_from = datetime.combine(today, active_from_time)
            active_to = datetime.combine(today, active_to_time)

            # Calculate expected breaks up to now and for full day
            total_minutes = (active_to - active_from).total_seconds() / 60
            total_expected = int(total_minutes / settings.interval_minutes)

            if now < active_from:
                # Before work hours - no breaks expected yet
                expected_so_far = 0
                break_status = get_translation("work_starts", language, time=settings.active_from, total=total_expected)
            elif now >= active_to:
                # After work hours - show completion status
                expected_so_far = total_expected
                if stats['total_breaks'] >= total_expected:
                    break_status = get_translation("day_complete", language, done=stats['total_breaks'], total=total_expected)
                else:
                    missed = total_expected - stats['total_breaks']
                    break_status = get_translation("day_ended", language, done=stats['total_breaks'], total=total_expected, missed=missed)
            else:
                # During work hours - calculate expected breaks up to now
                elapsed_minutes = (now - active_from).total_seconds() / 60
                expected_so_far = int(elapsed_minutes / settings.interval_minutes)
                remaining = total_expected - stats['total_breaks']

                # Add escape info if any breaks were escaped
                escaped = stats.get('breaks_escaped', 0)
                shown = stats.get('breaks_shown', stats['total_breaks'])

                if stats['total_breaks'] >= expected_so_far:
                    if remaining > 0:
                        if escaped > 0:
                            break_status = f"{stats['total_breaks']} of {total_expected} breaks completed ({escaped} escaped, {remaining} to go)"
                        else:
                            break_status = get_translation("breaks_status", language, done=stats['total_breaks'], total=total_expected, remaining=remaining)
                    else:
                        break_status = get_translation("all_breaks_complete", language, total=total_expected)
                else:
                    behind = expected_so_far - stats['total_breaks']
                    if escaped > 0:
                        break_status = f"{stats['total_breaks']} of {total_expected} breaks completed ({escaped} escaped, {behind} behind)"
                    else:
                        break_status = get_translation("breaks_behind", language, done=stats['total_breaks'], total=total_expected, behind=behind, remaining=remaining)

            # Show descriptive format based on status level
            if status == "Champion" and remaining <= 0 and stats['total_breaks'] >= total_expected:
                # All breaks complete - use special champion message
                return get_translation("champion_coverage", language,
                                     covered=stats['muscle_groups_covered'],
                                     total=stats['total_muscle_groups'],
                                     percentage=int(coverage),
                                     breaks=total_expected)
            else:
                # Use general format for all other cases
                return f"{emoji} {status} Coverage: {stats['muscle_groups_covered']}/{stats['total_muscle_groups']} muscles ({coverage:.0f}%) | {break_status}"
        except:
            # Fallback to original format if calculation fails
            return f"{emoji} {status} Coverage: {stats['muscle_groups_covered']}/{stats['total_muscle_groups']} muscles ({coverage:.0f}%) | {stats['total_breaks']} breaks today"

    def get_frequency_recommendation(self, coverage_percentage: float, total_breaks: int, current_interval: int = 30, test_hour: int = None) -> str:
        """Get recommendation for break frequency based on coverage"""
        from datetime import datetime
        from .config import load_settings

        # Get user's actual work schedule
        settings = load_settings()
        try:
            active_from_hour = int(settings.active_from.split(':')[0])
            active_to_hour = int(settings.active_to.split(':')[0])
        except:
            # Default to 5am-5pm if settings are invalid
            active_from_hour = 5
            active_to_hour = 17

        # Calculate hours since start of work day
        if test_hour is not None:
            # For testing - use provided hour
            hour = test_hour
        else:
            now = datetime.now()
            hour = now.hour

        # Check if we're within work hours
        if hour < active_from_hour or hour >= active_to_hour:
            # Outside work hours
            return ""

        hours_since_start = hour - active_from_hour

        # Don't make recommendations too early in the day
        if hours_since_start < 2:  # Less than 2 hours into work day
            return ""

        # Expected breaks by this time (with current interval)
        # But cap it at the total expected for the full work day
        max_work_hours = active_to_hour - active_from_hour
        max_expected_breaks = max_work_hours * (60 / current_interval)
        expected_breaks = min(hours_since_start * (60 / current_interval), max_expected_breaks)

        # Check if they're skipping too many breaks
        from .translations import get_translation
        from .config import load_settings
        settings = load_settings()
        language = settings.language

        if total_breaks < expected_breaks * 0.5 and hours_since_start >= 3:
            return get_translation("tip_skipping_breaks", language)

        # If coverage is low after several hours
        if hours_since_start >= 4:  # After 4+ hours of work (9 AM if starting at 5 AM)
            if coverage_percentage < 40:
                if current_interval > 20:
                    return get_translation("tip_low_coverage_interval", language)
                else:
                    return get_translation("tip_low_coverage_variety", language)
            elif coverage_percentage < 60 and hours_since_start >= 6:
                if current_interval > 25:
                    return get_translation("tip_increase_frequency", language)
                else:
                    return get_translation("tip_good_frequency", language)
            elif coverage_percentage < 80 and hours_since_start >= 8:
                return get_translation("tip_almost_full_coverage", language)

        return ""


# Module-level functions for easy access
def get_body_map() -> str:
    """Get the current body map visualization"""
    visualizer = BodyMapVisualizer()
    data = get_body_visualization_data()
    return visualizer.create_highlighted_view(data['muscle_work_counts'])

def get_daily_report() -> str:
    """Get comprehensive daily fitness report"""
    visualizer = BodyMapVisualizer()
    return visualizer.generate_daily_report()

def get_break_status_description() -> str:
    """Get descriptive break status string used across the app"""
    from datetime import datetime
    from .config import load_settings
    from .translations import get_translation

    data = get_body_visualization_data()
    stats = data['coverage_stats']
    settings = load_settings()
    lang = getattr(settings, 'language', 'en')

    try:
        now = datetime.now()
        active_from_time = datetime.strptime(settings.active_from, '%H:%M').time()
        active_to_time = datetime.strptime(settings.active_to, '%H:%M').time()

        # Create datetime objects for today's work hours
        today = now.date()
        active_from = datetime.combine(today, active_from_time)
        active_to = datetime.combine(today, active_to_time)

        # Calculate expected breaks and descriptive status
        total_minutes = (active_to - active_from).total_seconds() / 60
        total_expected = int(total_minutes / settings.interval_minutes)

        if now < active_from:
            if lang == 'sk':
                return f"Práca začína o {settings.active_from} ({total_expected} prestávok naplánovaných dnes)"
            return f"Work starts at {settings.active_from} ({total_expected} breaks planned today)"
        elif now >= active_to:
            if stats['total_breaks'] >= total_expected:
                if lang == 'sk':
                    return f"Deň dokončený! {stats['total_breaks']} z {total_expected} prestávok hotových"
                return f"Day complete! {stats['total_breaks']} of {total_expected} breaks done"
            else:
                missed = total_expected - stats['total_breaks']
                if lang == 'sk':
                    return f"Deň skončil: {stats['total_breaks']} z {total_expected} prestávok ({missed} vynechaných)"
                return f"Day ended: {stats['total_breaks']} of {total_expected} breaks ({missed} missed)"
        else:
            elapsed_minutes = (now - active_from).total_seconds() / 60
            expected_so_far = int(elapsed_minutes / settings.interval_minutes)
            remaining = total_expected - stats['total_breaks']

            if stats['total_breaks'] >= expected_so_far:
                if remaining > 0:
                    if lang == 'sk':
                        return f"{stats['total_breaks']} z {total_expected} prestávok hotových ({remaining} zostáva)"
                    return f"{stats['total_breaks']} of {total_expected} breaks done ({remaining} to go)"
                else:
                    if lang == 'sk':
                        return f"Všetkých {total_expected} prestávok dokončených! Skvelá práca!"
                    return f"All {total_expected} breaks complete! Great job!"
            else:
                behind = expected_so_far - stats['total_breaks']
                if lang == 'sk':
                    return f"{stats['total_breaks']} z {total_expected} prestávok hotových ({behind} pozadu, {remaining} celkovo zostáva)"
                return f"{stats['total_breaks']} of {total_expected} breaks done ({behind} behind schedule, {remaining} total remaining)"
    except:
        # Fallback
        if lang == 'sk':
            return f"{stats['total_breaks']} prestávok dnes"
        return f"{stats['total_breaks']} breaks today"

def get_status_line(language: str = "en") -> str:
    """Get simple status line for UI"""
    visualizer = BodyMapVisualizer()
    return visualizer.get_simple_status(language)


# Testing
if __name__ == "__main__":
    # Test with sample data
    sample_data = {
        'neck': 3,
        'shoulders': 5,
        'chest': 2,
        'core': 8,
        'quads': 4,
        'hamstrings': 3,
        'calves': 2,
        'full_body': 1
    }

    visualizer = BodyMapVisualizer()

    print("Highlighted View:")
    print(visualizer.create_highlighted_view(sample_data))

    print("\n" + "="*50 + "\n")

    print("Daily Report:")
    print(visualizer.generate_daily_report())

    print("\n" + "="*50 + "\n")

    print("Status Line:")
    print(visualizer.get_simple_status())