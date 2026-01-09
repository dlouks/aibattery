#!/usr/bin/env python3
"""Generate the macOS app icon for AI Battery."""

from PIL import Image, ImageDraw
import os
import subprocess

def create_arc_icon(size, outer_pct=90, inner_pct=75):
    """Create nested arc icon at given size."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = size // 2

    # Colors
    outer_color = (100, 180, 255, 255)  # Blue for weekly
    inner_color = (80, 220, 140, 255)   # Green for session
    bg_color = (60, 60, 70, 255)        # Dark gray background

    # Outer arc (weekly) - larger
    outer_radius = int(size * 0.42)
    outer_width = int(size * 0.08)

    # Background arc (full circle)
    draw.arc(
        [center - outer_radius, center - outer_radius,
         center + outer_radius, center + outer_radius],
        start=135, end=405,
        fill=bg_color,
        width=outer_width
    )

    # Filled arc based on percentage
    outer_angle = int(270 * outer_pct / 100)
    if outer_angle > 0:
        draw.arc(
            [center - outer_radius, center - outer_radius,
             center + outer_radius, center + outer_radius],
            start=135, end=135 + outer_angle,
            fill=outer_color,
            width=outer_width
        )

    # Inner arc (session) - smaller
    inner_radius = int(size * 0.28)
    inner_width = int(size * 0.08)

    # Background arc
    draw.arc(
        [center - inner_radius, center - inner_radius,
         center + inner_radius, center + inner_radius],
        start=135, end=405,
        fill=bg_color,
        width=inner_width
    )

    # Filled arc
    inner_angle = int(270 * inner_pct / 100)
    if inner_angle > 0:
        draw.arc(
            [center - inner_radius, center - inner_radius,
             center + inner_radius, center + inner_radius],
            start=135, end=135 + inner_angle,
            fill=inner_color,
            width=inner_width
        )

    return img

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    iconset_dir = os.path.join(script_dir, 'AIBattery.app', 'Contents', 'Resources', 'AppIcon.iconset')

    os.makedirs(iconset_dir, exist_ok=True)

    # Required sizes for macOS app icons
    sizes = [16, 32, 64, 128, 256, 512, 1024]

    for size in sizes:
        icon = create_arc_icon(size, outer_pct=90, inner_pct=75)

        # Save regular size
        if size <= 512:
            icon.save(os.path.join(iconset_dir, f'icon_{size}x{size}.png'))

        # Save @2x version (half the name, full size)
        half_size = size // 2
        if half_size >= 16:
            icon.save(os.path.join(iconset_dir, f'icon_{half_size}x{half_size}@2x.png'))

    print(f"Created iconset at {iconset_dir}")

    # Convert to icns using iconutil
    icns_path = os.path.join(script_dir, 'AIBattery.app', 'Contents', 'Resources', 'AppIcon.icns')
    result = subprocess.run(
        ['iconutil', '-c', 'icns', iconset_dir, '-o', icns_path],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"Created {icns_path}")
        # Clean up iconset
        import shutil
        shutil.rmtree(iconset_dir)
    else:
        print(f"iconutil failed: {result.stderr}")
        return

    # Update Info.plist to reference the icon
    print("App icon created successfully!")

if __name__ == '__main__':
    main()
