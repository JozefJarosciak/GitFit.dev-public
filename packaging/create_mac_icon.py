#!/usr/bin/env python3
"""
Create macOS .icns icon file for GitFit.dev
"""
import os
import subprocess
from PIL import Image, ImageDraw
import tempfile
import shutil

def create_dumbbell_icon(size=1024):
    """Create a high-res dumbbell icon"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Calculate dimensions
    padding = size // 8
    bar_height = size // 6
    bar_y = size // 2 - bar_height // 2

    # Colors - green theme matching the app
    bar_color = (34, 197, 94, 255)  # Green-500
    plate_color = (22, 163, 74, 255)  # Green-600
    shadow_color = (21, 128, 61, 100)  # Semi-transparent darker green

    # Draw shadow
    shadow_offset = size // 50
    draw.rounded_rectangle(
        [padding + shadow_offset, bar_y + shadow_offset,
         size - padding + shadow_offset, bar_y + bar_height + shadow_offset],
        radius=bar_height // 2,
        fill=shadow_color
    )

    # Draw main bar
    draw.rounded_rectangle(
        [padding, bar_y, size - padding, bar_y + bar_height],
        radius=bar_height // 2,
        fill=bar_color
    )

    # Draw weight plates
    plate_width = size // 5
    plate_height = size // 3

    # Left plate
    left_x = padding - plate_width // 3
    draw.rounded_rectangle(
        [left_x, size // 2 - plate_height // 2,
         left_x + plate_width, size // 2 + plate_height // 2],
        radius=size // 20,
        fill=plate_color
    )

    # Right plate
    right_x = size - padding - plate_width + plate_width // 3
    draw.rounded_rectangle(
        [right_x, size // 2 - plate_height // 2,
         right_x + plate_width, size // 2 + plate_height // 2],
        radius=size // 20,
        fill=plate_color
    )

    # Add highlights for depth
    highlight_color = (74, 222, 128, 180)  # Light green

    # Bar highlight
    draw.rounded_rectangle(
        [padding + size//30, bar_y + size//50,
         size - padding - size//30, bar_y + bar_height // 3],
        radius=bar_height // 6,
        fill=highlight_color
    )

    return img

def create_iconset():
    """Create macOS iconset with all required sizes"""

    print("Creating GitFit.dev icon for macOS...")

    # Create base icon at maximum resolution
    base_icon = create_dumbbell_icon(1024)

    # Create temporary iconset directory
    temp_dir = tempfile.mkdtemp()
    iconset_path = os.path.join(temp_dir, "icon.iconset")
    os.makedirs(iconset_path)

    # Required sizes for macOS iconset
    sizes = [
        (16, "16x16"),
        (32, "16x16@2x"),
        (32, "32x32"),
        (64, "32x32@2x"),
        (128, "128x128"),
        (256, "128x128@2x"),
        (256, "256x256"),
        (512, "256x256@2x"),
        (512, "512x512"),
        (1024, "512x512@2x"),
    ]

    # Generate all sizes
    for size, name in sizes:
        resized = base_icon.resize((size, size), Image.Resampling.LANCZOS)
        icon_path = os.path.join(iconset_path, f"icon_{name}.png")
        resized.save(icon_path, "PNG")
        print(f"  Created {name}")

    # Ensure assets directory exists
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # Output path for .icns file
    output_path = os.path.join(assets_dir, "icon.icns")

    # Convert iconset to icns using iconutil (macOS only)
    try:
        # This command only works on macOS
        subprocess.run(
            ["iconutil", "-c", "icns", "-o", output_path, iconset_path],
            check=True
        )
        print(f"[OK] Created {output_path}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Note: iconutil not found (expected on non-macOS systems)")
        print("The .icns file will be created when you run this on MacInCloud")

        # As fallback, save a PNG that can be converted on Mac
        fallback_path = os.path.join(assets_dir, "icon_1024.png")
        base_icon.save(fallback_path, "PNG")
        print(f"[OK] Saved fallback PNG: {fallback_path}")
        print("  Run this script on macOS to generate the .icns file")

    # Clean up
    shutil.rmtree(temp_dir)

    return output_path

if __name__ == "__main__":
    icon_path = create_iconset()
    print("\nIcon creation complete!")
    print("Next step: Run packaging/build_macos.sh on MacInCloud")