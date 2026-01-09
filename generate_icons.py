#!/usr/bin/env python3
"""Generate gauge arc icons with dot marker for Claude Battery"""

from PIL import Image, ImageDraw
import math
import os

ICON_DIR = os.path.join(os.path.dirname(__file__), 'icons')
SIZE = 22

def create_gauge_icon(fill_percent, filename):
    """Create a gauge-style arc with dot at current position"""
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = SIZE // 2, SIZE // 2
    r = (SIZE // 2) - 3
    line_width = 3

    # Gauge spans 270 degrees (gap at bottom)
    start_angle = 135
    sweep = 270

    # Draw background arc (faint)
    draw.arc(
        [cx - r, cy - r, cx + r, cy + r],
        start=start_angle, end=start_angle + sweep,
        fill=(0, 0, 0, 70),
        width=line_width
    )

    # Draw filled portion
    if fill_percent > 0:
        fill_sweep = (fill_percent / 100) * sweep
        draw.arc(
            [cx - r, cy - r, cx + r, cy + r],
            start=start_angle, end=start_angle + fill_sweep,
            fill=(0, 0, 0, 255),
            width=line_width
        )

        # Draw dot at current position
        angle_deg = start_angle + fill_sweep
        angle_rad = math.radians(angle_deg)
        dot_x = cx + r * math.cos(angle_rad)
        dot_y = cy + r * math.sin(angle_rad)
        dot_r = 2  # Smaller dot
        draw.ellipse(
            [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
            fill=(0, 0, 0, 255)
        )

    img.save(os.path.join(ICON_DIR, filename))

def main():
    os.makedirs(ICON_DIR, exist_ok=True)

    for percent in range(0, 101):
        filename = f'battery_{percent}.png'
        create_gauge_icon(percent, filename)
        if percent % 10 == 0:
            print(f"Created {filename}")

    print(f"\n101 icons created in {ICON_DIR}")

if __name__ == '__main__':
    main()
