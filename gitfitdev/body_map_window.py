"""
Body Map Viewer Window - Shows detailed daily fitness progress
"""
import tkinter as tk
from tkinter import ttk
from typing import Optional
from .body_map import get_daily_report, get_body_visualization_data, BodyMapVisualizer
from .themes import get_theme
from .translations import get_translation
from .body_svg import create_canvas_body_map, create_legend_frame


class BodyMapWindow:
    """Window showing detailed body map and daily fitness progress"""

    def __init__(self, parent: Optional[tk.Tk] = None, theme_id: str = "green", language: str = "en"):
        """Create body map viewer window"""
        self.parent = parent
        self.language = language
        if parent is None:
            self.root = tk.Tk()
            self.standalone = True
        else:
            self.root = tk.Toplevel(parent)
            self.standalone = False

        self.theme = get_theme(theme_id)
        self.visualizer = BodyMapVisualizer()

        self.setup_window()
        self.create_widgets()
        self.update_display()

    def setup_window(self):
        """Configure the window"""
        self.root.title(get_translation("body_map_title", self.language))
        self.root.geometry("680x650")
        self.root.configure(bg=self.theme.background)
        self.root.minsize(680, 650)  # Set minimum size

        # Set window icon
        try:
            from .app import _dumbbell_icon
            try:
                from PIL import ImageTk
                icon_image = _dumbbell_icon(32)
                self.root.iconphoto(False, ImageTk.PhotoImage(icon_image))
            except ImportError:
                pass  # PIL not available
        except Exception:
            pass  # Fallback to default icon if there's an issue

        # Center window - increased width to accommodate stats
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (750 // 2)
        y = (self.root.winfo_screenheight() // 2) - (650 // 2)
        self.root.geometry(f"750x650+{x}+{y}")

    def create_widgets(self):
        """Create all window widgets"""
        # Main container with fixed padding
        main_frame = tk.Frame(self.root, bg=self.theme.background)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Title
        title_label = tk.Label(
            main_frame,
            text=get_translation("body_map_header", self.language),
            font=("Segoe UI", 20, "bold"),
            fg=self.theme.text_primary,
            bg=self.theme.background
        )
        title_label.pack(pady=(0, 10))

        # Stats section
        stats_frame = tk.Frame(main_frame, bg=self.theme.background)
        stats_frame.pack(fill=tk.X, pady=(0, 10))

        self.stats_display = tk.Label(
            stats_frame,
            text=get_translation("loading", self.language),
            font=("Segoe UI", 11),
            fg=self.theme.text_secondary,
            bg=self.theme.background,
            justify=tk.LEFT
        )
        self.stats_display.pack()

        # Muscle groups section (reduced height)
        muscles_frame = tk.LabelFrame(
            main_frame,
            text=get_translation("muscle_groups_worked", self.language),
            font=("Segoe UI", 12, "bold"),
            fg=self.theme.accent,
            bg=self.theme.background
        )
        muscles_frame.pack(fill=tk.X, pady=(0, 10))

        # Create non-scrollable area for muscle list (show only top ones)
        self.muscle_frame = tk.Frame(muscles_frame, bg=self.theme.background)
        self.muscle_frame.pack(padx=10, pady=5, fill=tk.X)

        # Visual Body Map section with side-by-side layout
        body_section_frame = tk.LabelFrame(
            main_frame,
            text=get_translation("body_coverage_map", self.language),
            font=("Segoe UI", 12, "bold"),
            fg=self.theme.accent,
            bg=self.theme.background
        )
        # Body section with proper sizing
        body_section_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Container for side-by-side layout
        body_content = tk.Frame(body_section_frame, bg=self.theme.background)
        body_content.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Left side: Body map
        self.body_container = tk.Frame(body_content, bg=self.theme.background, width=250, height=280)
        self.body_container.pack(side=tk.LEFT, padx=(10, 10))
        self.body_container.pack_propagate(False)  # Keep fixed size

        # Right side: Legend
        self.legend_container = tk.Frame(body_content, bg=self.theme.background)
        self.legend_container.pack(side=tk.LEFT, anchor='n', padx=(10, 10), pady=(20, 0))

        # Initialize body canvas and legend
        self.body_canvas = None
        self.legend_frame = None

        # Buttons - ensure they're always visible at bottom
        button_frame = tk.Frame(main_frame, bg=self.theme.background)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        refresh_btn = tk.Button(
            button_frame,
            text=get_translation("button_refresh", self.language),
            command=self.update_display,
            bg=self.theme.accent,
            fg=self.theme.background,
            font=("Segoe UI", 11),
            padx=20,
            pady=5
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))

        reset_btn = tk.Button(
            button_frame,
            text=get_translation("button_reset_daily", self.language),
            command=self.reset_data,
            bg=self.theme.accent_secondary,
            fg=self.theme.background,
            font=("Segoe UI", 11),
            padx=20,
            pady=5
        )
        reset_btn.pack(side=tk.LEFT, padx=(0, 10))

        close_btn = tk.Button(
            button_frame,
            text=get_translation("button_close", self.language),
            command=self.close,
            bg=self.theme.text_secondary,
            fg=self.theme.background,
            font=("Segoe UI", 11),
            padx=20,
            pady=5
        )
        close_btn.pack(side=tk.RIGHT)

    def update_display(self):
        """Update all displays with current data"""
        # Get data
        data = get_body_visualization_data()
        muscle_counts = data['muscle_work_counts']
        stats = data['coverage_stats']

        # Get descriptive break status using shared function
        from .body_map import get_break_status_description
        from .config import load_settings

        break_status = get_break_status_description()
        settings = load_settings()

        # Update stats with compact format using translations
        from .translations import get_translation
        lang = getattr(settings, 'language', 'en')

        # Calculate total exercise time
        lock_seconds = getattr(settings, 'lock_seconds', 60)
        breaks_completed = stats.get('breaks_completed', 0)
        total_seconds = breaks_completed * lock_seconds
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        # Format time display
        if hours > 0:
            time_str = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            time_str = f"{minutes}m {seconds}s"
        else:
            time_str = f"{seconds}s"

        # Translate the labels
        breaks_label = get_translation('breaks', lang).capitalize()
        exercises_label = get_translation('exercises', lang).capitalize()
        stretches_label = get_translation('stretches', lang).capitalize()
        coverage_label = get_translation('stats_coverage', lang)
        time_label = get_translation('total_exercise_time', lang)

        # Format the coverage string
        coverage_text = coverage_label.format(
            covered=stats['muscle_groups_covered'],
            total=stats['total_muscle_groups'],
            percentage=stats['coverage_percentage']
        )

        # Format stats on two lines for better readability
        line1 = f"{breaks_label}: {break_status}"
        line2 = f"{exercises_label}: {stats['exercises_done']} | {stretches_label.capitalize()}: {stats['stretches_done']} | {time_label}: {time_str}"
        line3 = f"{coverage_text} - {self._get_status_message(stats['coverage_percentage'], lang)}"

        stats_text = f"{line1}\n{line2}\n{line3}"

        self.stats_display.config(text=stats_text)

        # Update muscle groups display
        for widget in self.muscle_frame.winfo_children():
            widget.destroy()

        if muscle_counts:
            # Sort by count
            sorted_muscles = sorted(muscle_counts.items(), key=lambda x: x[1], reverse=True)

            # Only show top 5 muscle groups to save space
            for muscle, count in sorted_muscles[:5]:
                row_frame = tk.Frame(self.muscle_frame, bg=self.theme.background)
                row_frame.pack(fill=tk.X, pady=2)

                # Muscle name
                muscle_name = muscle.replace('_', ' ').title()
                name_label = tk.Label(
                    row_frame,
                    text=f"{muscle_name:20}",
                    font=("Segoe UI", 11),
                    fg=self.theme.text_primary,
                    bg=self.theme.background,
                    anchor='w',
                    width=20
                )
                name_label.pack(side=tk.LEFT)

                # Progress bar
                bar_length = min(count * 3, 30)
                bar = '#' * bar_length + '.' * (30 - bar_length)
                bar_label = tk.Label(
                    row_frame,
                    text=f"[{bar}]",
                    font=("Consolas", 10),
                    fg=self.theme.accent_secondary,
                    bg=self.theme.background
                )
                bar_label.pack(side=tk.LEFT, padx=10)

                # Count
                count_label = tk.Label(
                    row_frame,
                    text=f"{count}x",
                    font=("Segoe UI", 11, "bold"),
                    fg=self.theme.accent,
                    bg=self.theme.background,
                    width=5
                )
                count_label.pack(side=tk.LEFT)

        else:
            no_data_label = tk.Label(
                self.muscle_frame,
                text=get_translation('body_map_no_data', settings.language),
                font=("Segoe UI", 12),
                fg=self.theme.text_secondary,
                bg=self.theme.background
            )
            no_data_label.pack(pady=20)

        # Update body ASCII art
        self.update_body_display(muscle_counts)

    def update_body_display(self, muscle_counts):
        """Update the visual body map and legend"""
        # Remove old canvas if exists
        if self.body_canvas:
            self.body_canvas.destroy()
        if self.legend_frame:
            self.legend_frame.destroy()

        # Create new body map
        self.body_canvas = create_canvas_body_map(
            self.body_container,
            muscle_counts,
            width=200,
            height=250
        )
        self.body_canvas.pack()

        # Create legend
        self.legend_frame = create_legend_frame(self.legend_container, self.theme)
        self.legend_frame.pack()

    def _create_body_art(self, muscle_counts):
        """Create ASCII art representation of worked muscles"""
        # Simple text-based body map
        if not muscle_counts:
            return """
        No activity yet today

        Start exercising to see
        your muscle map!

             O
            /|\\
           / | \\
            / \\
           /   \\
"""

        # Calculate intensities
        max_count = max(muscle_counts.values()) if muscle_counts else 1

        def intensity(muscle):
            count = muscle_counts.get(muscle, 0)
            if count == 0:
                return ' '
            elif count <= max_count * 0.25:
                return '.'
            elif count <= max_count * 0.5:
                return 'o'
            elif count <= max_count * 0.75:
                return 'O'
            else:
                return '#'

        # Build body representation
        n = intensity('neck')
        s = intensity('shoulders')
        c = intensity('chest')
        ub = intensity('upper_back')
        lb = intensity('lower_back')
        a = intensity('arms')
        co = intensity('core')
        h = intensity('hips')
        g = intensity('glutes')
        q = intensity('quads')
        hm = intensity('hamstrings')
        ca = intensity('calves')

        return f"""
        MUSCLE MAP

         Intensity:
         . = Light
         o = Medium
         O = Heavy
         # = Full

            [{n}]     Neck
         [{s}] O [{s}]  Shoulders
          \\[{a}]|[{a}]/   Arms
         [{c}][{co}][{ub}]  Chest/Core/Back
         [{lb}][{co}][{lb}]  Lower Back/Core
          \\[{h}][{g}]/   Hips/Glutes
          [{q}] [{q}]   Quads
          [{hm}] [{hm}]   Hamstrings
          [{ca}] [{ca}]   Calves
"""

    def _get_status_message(self, percentage, language='en'):
        """Get encouraging status message based on coverage"""
        from .translations import get_translation

        if percentage >= 80:
            return get_translation('coverage_champion', language)
        elif percentage >= 60:
            return get_translation('coverage_great', language)
        elif percentage >= 40:
            return get_translation('coverage_good', language)
        elif percentage >= 20:
            return get_translation('coverage_building', language)
        else:
            return get_translation('coverage_start', language)

    def reset_data(self):
        """Reset daily tracking data"""
        from .tiny_lm import get_generator
        # Reset the actual tracker used by the generator
        generator = get_generator()
        generator.tracker.reset_daily_data()
        self.update_display()

    def close(self):
        """Close the window"""
        if self.standalone:
            self.root.quit()
        else:
            self.root.destroy()

    def show(self):
        """Show the window"""
        if self.standalone:
            self.root.mainloop()


# Test function
if __name__ == "__main__":
    window = BodyMapWindow()
    window.show()