"""
SVG-based body map visualization for GitFit.dev
Shows muscle groups worked in an anatomical view
"""

def generate_body_svg(muscle_data: dict, width: int = 400, height: int = 600) -> str:
    """
    Generate an SVG representation of a human body with muscle groups highlighted.

    Args:
        muscle_data: Dictionary with muscle group names as keys and work counts as values
        width: SVG width in pixels
        height: SVG height in pixels

    Returns:
        SVG string
    """
    from .translations import get_translation
    from .config import load_settings

    settings = load_settings()
    lang = settings.language

    # Get translations for the SVG
    muscle_activity_label = get_translation("muscle_activity_label", lang)
    not_worked = get_translation("not_worked", lang)
    light_activity = get_translation("light_activity", lang)
    medium_activity = get_translation("medium_activity", lang)
    heavy_activity = get_translation("heavy_activity", lang)
    body_coverage_map = get_translation("body_coverage_map", lang)

    # Calculate opacity based on work count (max 5 for full opacity)
    def get_opacity(count: int) -> float:
        if count == 0:
            return 0.1
        return min(0.2 + (count * 0.16), 1.0)

    # Get color based on work count
    def get_color(count: int) -> str:
        if count == 0:
            return "#cccccc"
        elif count <= 2:
            return "#4ade80"  # Light green
        elif count <= 4:
            return "#22c55e"  # Medium green
        else:
            return "#16a34a"  # Dark green

    # Extract muscle work counts with defaults
    neck_count = muscle_data.get('neck', 0)
    shoulders_count = muscle_data.get('shoulders', 0)
    chest_count = muscle_data.get('chest', 0)
    core_count = muscle_data.get('core', 0) + muscle_data.get('abs', 0)
    back_count = muscle_data.get('back', 0)
    arms_count = muscle_data.get('arms', 0) + muscle_data.get('biceps', 0) + muscle_data.get('triceps', 0)
    forearms_count = muscle_data.get('forearms', 0) + muscle_data.get('wrists', 0)
    quads_count = muscle_data.get('quads', 0) + muscle_data.get('legs', 0)
    hamstrings_count = muscle_data.get('hamstrings', 0)
    calves_count = muscle_data.get('calves', 0)
    glutes_count = muscle_data.get('glutes', 0)

    svg = f'''<svg width="{width}" height="{height}" viewBox="0 0 400 600" xmlns="http://www.w3.org/2000/svg">
    <!-- Background -->
    <rect width="400" height="600" fill="#1e293b"/>

    <!-- Body outline -->
    <g id="body-outline" stroke="#475569" stroke-width="2" fill="none">
        <!-- Head -->
        <circle cx="200" cy="50" r="25"/>

        <!-- Torso -->
        <path d="M 175 75 L 175 250 L 225 250 L 225 75 Z"/>

        <!-- Arms -->
        <path d="M 175 100 L 140 100 L 120 200 L 135 210"/>
        <path d="M 225 100 L 260 100 L 280 200 L 265 210"/>

        <!-- Legs -->
        <path d="M 175 250 L 165 400 L 180 550 L 185 580"/>
        <path d="M 225 250 L 235 400 L 220 550 L 215 580"/>
    </g>

    <!-- Muscle groups -->
    <g id="muscle-groups" stroke="none">
        <!-- Neck -->
        <rect x="185" y="65" width="30" height="15"
              fill="{get_color(neck_count)}" opacity="{get_opacity(neck_count)}" rx="3">
            <title>Neck: {neck_count}x</title>
        </rect>

        <!-- Shoulders -->
        <ellipse cx="165" cy="95" rx="20" ry="15"
                 fill="{get_color(shoulders_count)}" opacity="{get_opacity(shoulders_count)}">
            <title>Shoulders: {shoulders_count}x</title>
        </ellipse>
        <ellipse cx="235" cy="95" rx="20" ry="15"
                 fill="{get_color(shoulders_count)}" opacity="{get_opacity(shoulders_count)}">
            <title>Shoulders: {shoulders_count}x</title>
        </ellipse>

        <!-- Chest -->
        <path d="M 175 100 Q 200 110 225 100 L 225 140 Q 200 150 175 140 Z"
              fill="{get_color(chest_count)}" opacity="{get_opacity(chest_count)}">
            <title>Chest: {chest_count}x</title>
        </path>

        <!-- Core/Abs -->
        <rect x="180" y="150" width="40" height="80"
              fill="{get_color(core_count)}" opacity="{get_opacity(core_count)}" rx="5">
            <title>Core: {core_count}x</title>
        </rect>

        <!-- Back (shown as side view) -->
        <rect x="175" y="100" width="50" height="120"
              fill="{get_color(back_count)}" opacity="{get_opacity(back_count) * 0.5}" rx="5">
            <title>Back: {back_count}x</title>
        </rect>

        <!-- Arms (Biceps/Triceps) -->
        <ellipse cx="150" cy="140" rx="12" ry="40"
                 fill="{get_color(arms_count)}" opacity="{get_opacity(arms_count)}">
            <title>Arms: {arms_count}x</title>
        </ellipse>
        <ellipse cx="250" cy="140" rx="12" ry="40"
                 fill="{get_color(arms_count)}" opacity="{get_opacity(arms_count)}">
            <title>Arms: {arms_count}x</title>
        </ellipse>

        <!-- Forearms/Wrists -->
        <ellipse cx="130" cy="190" rx="8" ry="25"
                 fill="{get_color(forearms_count)}" opacity="{get_opacity(forearms_count)}">
            <title>Forearms: {forearms_count}x</title>
        </ellipse>
        <ellipse cx="270" cy="190" rx="8" ry="25"
                 fill="{get_color(forearms_count)}" opacity="{get_opacity(forearms_count)}">
            <title>Forearms: {forearms_count}x</title>
        </ellipse>

        <!-- Glutes -->
        <ellipse cx="200" cy="260" rx="35" ry="20"
                 fill="{get_color(glutes_count)}" opacity="{get_opacity(glutes_count)}">
            <title>Glutes: {glutes_count}x</title>
        </ellipse>

        <!-- Quads (front thigh) -->
        <ellipse cx="175" cy="320" rx="15" ry="50"
                 fill="{get_color(quads_count)}" opacity="{get_opacity(quads_count)}">
            <title>Quads: {quads_count}x</title>
        </ellipse>
        <ellipse cx="225" cy="320" rx="15" ry="50"
                 fill="{get_color(quads_count)}" opacity="{get_opacity(quads_count)}">
            <title>Quads: {quads_count}x</title>
        </ellipse>

        <!-- Hamstrings (back thigh - shown as overlay) -->
        <ellipse cx="175" cy="330" rx="12" ry="40"
                 fill="{get_color(hamstrings_count)}" opacity="{get_opacity(hamstrings_count) * 0.7}">
            <title>Hamstrings: {hamstrings_count}x</title>
        </ellipse>
        <ellipse cx="225" cy="330" rx="12" ry="40"
                 fill="{get_color(hamstrings_count)}" opacity="{get_opacity(hamstrings_count) * 0.7}">
            <title>Hamstrings: {hamstrings_count}x</title>
        </ellipse>

        <!-- Calves -->
        <ellipse cx="180" cy="480" rx="10" ry="35"
                 fill="{get_color(calves_count)}" opacity="{get_opacity(calves_count)}">
            <title>Calves: {calves_count}x</title>
        </ellipse>
        <ellipse cx="220" cy="480" rx="10" ry="35"
                 fill="{get_color(calves_count)}" opacity="{get_opacity(calves_count)}">
            <title>Calves: {calves_count}x</title>
        </ellipse>
    </g>

    <!-- Legend -->
    <g id="legend" font-family="Arial, sans-serif" font-size="12" fill="#94a3b8">
        <text x="20" y="30">{muscle_activity_label}</text>
        <rect x="20" y="40" width="15" height="15" fill="#cccccc" opacity="0.3"/>
        <text x="40" y="52">{not_worked}</text>

        <rect x="20" y="60" width="15" height="15" fill="#4ade80"/>
        <text x="40" y="72">{light_activity}</text>

        <rect x="20" y="80" width="15" height="15" fill="#22c55e"/>
        <text x="40" y="92">{medium_activity}</text>

        <rect x="20" y="100" width="15" height="15" fill="#16a34a"/>
        <text x="40" y="112">{heavy_activity}</text>
    </g>

    <!-- Title -->
    <text x="200" y="20" font-family="Arial, sans-serif" font-size="16"
          fill="#f1f5f9" text-anchor="middle" font-weight="bold">
        {body_coverage_map}
    </text>
</svg>'''

    return svg


def save_svg_to_file(svg_content: str, filename: str):
    """Save SVG content to a file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg_content)


# Function to display SVG in tkinter using tkinterweb or as fallback HTML
def create_svg_widget(parent, muscle_data: dict, width: int = 400, height: int = 600):
    """
    Create a widget to display SVG in tkinter.
    Falls back to Canvas rendering if web widget not available.
    """
    svg_content = generate_body_svg(muscle_data, width, height)

    # Try to use tkinterweb if available
    try:
        from tkinterweb import HtmlFrame
        frame = HtmlFrame(parent, horizontal_scrollbar="auto")
        html = f'''
        <html>
        <head>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    background: #1e293b;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }}
            </style>
        </head>
        <body>
            {svg_content}
        </body>
        </html>
        '''
        frame.load_html(html)
        return frame
    except ImportError:
        # Fallback to Canvas rendering
        return create_canvas_body_map(parent, muscle_data, width, height)


def create_canvas_body_map(parent, muscle_data: dict, width: int = 200, height: int = 250):
    """
    Canvas-based body map visualization without legend.
    Legend should be created separately with create_legend_frame.
    """
    import tkinter as tk

    canvas = tk.Canvas(parent, width=width, height=height, bg='#1e293b', highlightthickness=0)

    # Helper to get color based on count
    def get_color(count: int) -> str:
        if count == 0:
            return "#3a3a3a"
        elif count <= 2:
            return "#4ade80"
        elif count <= 4:
            return "#22c55e"
        else:
            return "#16a34a"

    # Center the body in the canvas
    cx = width // 2

    # Draw body outline (centered)
    # Head
    canvas.create_oval(cx-13, 12, cx+12, 37, outline='#475569', width=1, fill='')

    # Neck
    neck_color = get_color(muscle_data.get('neck', 0))
    canvas.create_rectangle(cx-8, 32, cx+7, 40, fill=neck_color, outline='')

    # Torso outline
    canvas.create_rectangle(cx-20, 40, cx+20, 130, outline='#475569', width=1, fill='')

    # Shoulders
    shoulders_color = get_color(muscle_data.get('shoulders', 0))
    canvas.create_oval(cx-30, 40, cx-15, 55, fill=shoulders_color, outline='')
    canvas.create_oval(cx+15, 40, cx+30, 55, fill=shoulders_color, outline='')

    # Chest
    chest_color = get_color(muscle_data.get('chest', 0))
    canvas.create_rectangle(cx-15, 45, cx+15, 70, fill=chest_color, outline='')

    # Back (shown as overlay behind chest with transparency effect)
    back_color = get_color(muscle_data.get('back', 0) + muscle_data.get('upper_back', 0) + muscle_data.get('lower_back', 0))
    if muscle_data.get('back', 0) > 0 or muscle_data.get('upper_back', 0) > 0 or muscle_data.get('lower_back', 0) > 0:
        canvas.create_rectangle(cx-18, 47, cx+18, 115, fill=back_color, outline='', stipple='gray50')

    # Core/Abs
    core_color = get_color(muscle_data.get('core', 0) + muscle_data.get('abs', 0))
    canvas.create_rectangle(cx-13, 72, cx+12, 120, fill=core_color, outline='')

    # Arms (biceps + triceps + arms)
    arms_color = get_color(muscle_data.get('arms', 0) + muscle_data.get('biceps', 0) + muscle_data.get('triceps', 0))
    # Left arm
    canvas.create_polygon(cx-20, 45, cx-30, 45, cx-40, 100, cx-30, 105, fill=arms_color, outline='#475569', width=1)
    # Right arm
    canvas.create_polygon(cx+20, 45, cx+30, 45, cx+40, 100, cx+30, 105, fill=arms_color, outline='#475569', width=1)

    # Forearms/Wrists
    forearms_color = get_color(muscle_data.get('forearms', 0) + muscle_data.get('wrists', 0))
    if muscle_data.get('forearms', 0) > 0 or muscle_data.get('wrists', 0) > 0:
        canvas.create_oval(cx-42, 85, cx-32, 105, fill=forearms_color, outline='')
        canvas.create_oval(cx+32, 85, cx+42, 105, fill=forearms_color, outline='')

    # Glutes
    glutes_color = get_color(muscle_data.get('glutes', 0) + muscle_data.get('hips', 0))
    canvas.create_oval(cx-18, 125, cx+18, 135, fill=glutes_color, outline='')

    # Quads (front thigh)
    quads_color = get_color(muscle_data.get('quads', 0) + muscle_data.get('legs', 0))
    # Left leg
    canvas.create_polygon(cx-20, 130, cx-15, 130, cx-18, 200, cx-23, 200, fill=quads_color, outline='#475569', width=1)
    # Right leg
    canvas.create_polygon(cx+15, 130, cx+20, 130, cx+22, 200, cx+17, 200, fill=quads_color, outline='#475569', width=1)

    # Hamstrings (back thigh - shown with stipple pattern)
    hamstrings_color = get_color(muscle_data.get('hamstrings', 0))
    if muscle_data.get('hamstrings', 0) > 0:
        canvas.create_rectangle(cx-22, 140, cx-13, 190, fill=hamstrings_color, outline='', stipple='gray50')
        canvas.create_rectangle(cx+13, 140, cx+22, 190, fill=hamstrings_color, outline='', stipple='gray50')

    # Calves
    calves_color = get_color(muscle_data.get('calves', 0))
    canvas.create_oval(cx-25, 205, cx-15, 240, fill=calves_color, outline='')
    canvas.create_oval(cx+15, 205, cx+25, 240, fill=calves_color, outline='')

    return canvas


def create_legend_frame(parent, theme):
    """Create a separate legend frame for muscle activity levels"""
    import tkinter as tk
    from .translations import get_translation
    from .config import load_settings

    settings = load_settings()
    frame = tk.Frame(parent, bg=theme.background)

    # Title
    title = tk.Label(frame, text=get_translation("muscle_activity_label", settings.language),
                    font=('Arial', 11, 'bold'),
                    fg=theme.accent,
                    bg=theme.background)
    title.pack(anchor='w', pady=(0, 10))

    legend_items = [
        ("#3a3a3a", get_translation("not_worked", settings.language)),
        ("#4ade80", get_translation("light_activity", settings.language)),
        ("#22c55e", get_translation("medium_activity", settings.language)),
        ("#16a34a", get_translation("heavy_activity", settings.language))
    ]

    for color, label in legend_items:
        row = tk.Frame(frame, bg=theme.background)
        row.pack(anchor='w', pady=2)

        # Color box
        color_box = tk.Frame(row, bg=color, width=15, height=15)
        color_box.pack(side=tk.LEFT, padx=(0, 8))
        color_box.pack_propagate(False)

        # Label
        text = tk.Label(row, text=label,
                       font=('Arial', 10),
                       fg=theme.text_secondary,
                       bg=theme.background)
        text.pack(side=tk.LEFT)

    return frame