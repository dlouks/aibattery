#!/usr/bin/env python3
"""Generate example icons for the three dual-metric approaches"""

from PIL import Image, ImageDraw
import math
import os

SIZE = 64  # Larger for visibility
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Example values: session 32% remaining, weekly 85% remaining
SESSION = 32
WEEKLY = 85


def create_nested_arcs(session_pct, weekly_pct, filename):
    """Option 1: Nested arcs - outer for weekly, inner for session"""
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = SIZE // 2

    # Outer arc (weekly) - larger radius
    outer_r = (SIZE - 4) // 2
    outer_bbox = [center - outer_r, center - outer_r, center + outer_r, center + outer_r]
    start_angle = 135
    sweep = 270

    # Background arc (faint)
    draw.arc(outer_bbox, start_angle, start_angle + sweep, fill=(0, 0, 0, 70), width=3)
    # Filled portion (weekly)
    if weekly_pct > 0:
        fill_sweep = (weekly_pct / 100) * sweep
        draw.arc(outer_bbox, start_angle, start_angle + fill_sweep, fill=(0, 0, 0, 255), width=3)

    # Inner arc (session) - smaller radius
    inner_r = outer_r - 8
    inner_bbox = [center - inner_r, center - inner_r, center + inner_r, center + inner_r]

    # Background arc (faint)
    draw.arc(inner_bbox, start_angle, start_angle + sweep, fill=(0, 0, 0, 70), width=3)
    # Filled portion (session)
    if session_pct > 0:
        fill_sweep = (session_pct / 100) * sweep
        draw.arc(inner_bbox, start_angle, start_angle + fill_sweep, fill=(0, 0, 0, 255), width=3)

    img.save(os.path.join(OUTPUT_DIR, filename))
    print(f"Created {filename}")


def create_split_arc(session_pct, weekly_pct, filename):
    """Option 2: Split arc - left half session, right half weekly"""
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = SIZE // 2
    radius = (SIZE - 6) // 2
    bbox = [center - radius, center - radius, center + radius, center + radius]

    # Left side (session) - from 135 to 270 degrees (135 degree sweep)
    left_start = 135
    left_sweep = 135

    # Background (faint)
    draw.arc(bbox, left_start, left_start + left_sweep, fill=(0, 0, 0, 70), width=4)
    # Filled (session)
    if session_pct > 0:
        fill_sweep = (session_pct / 100) * left_sweep
        draw.arc(bbox, left_start, left_start + fill_sweep, fill=(0, 0, 0, 255), width=4)

    # Right side (weekly) - from 270 to 405 degrees (135 degree sweep)
    right_start = 270
    right_sweep = 135

    # Background (faint)
    draw.arc(bbox, right_start, right_start + right_sweep, fill=(0, 0, 0, 70), width=4)
    # Filled (weekly)
    if weekly_pct > 0:
        fill_sweep = (weekly_pct / 100) * right_sweep
        draw.arc(bbox, right_start, right_start + fill_sweep, fill=(0, 0, 0, 255), width=4)

    # Small gap indicator at bottom center
    gap_angle = math.radians(270)
    gap_x = center + int((radius - 2) * math.cos(gap_angle))
    gap_y = center + int((radius - 2) * math.sin(gap_angle))
    draw.ellipse([gap_x - 2, gap_y - 2, gap_x + 2, gap_y + 2], fill=(0, 0, 0, 100))

    img.save(os.path.join(OUTPUT_DIR, filename))
    print(f"Created {filename}")


def create_stacked_dots(session_pct, weekly_pct, filename):
    """Option 3: Single arc with two marker dots"""
    img = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = SIZE // 2
    radius = (SIZE - 6) // 2
    bbox = [center - radius, center - radius, center + radius, center + radius]

    start_angle = 135
    sweep = 270

    # Full background arc (faint)
    draw.arc(bbox, start_angle, start_angle + sweep, fill=(0, 0, 0, 70), width=4)

    # Draw filled arc up to the higher value
    higher = max(session_pct, weekly_pct)
    if higher > 0:
        fill_sweep = (higher / 100) * sweep
        draw.arc(bbox, start_angle, start_angle + fill_sweep, fill=(0, 0, 0, 180), width=4)

    # Draw filled arc up to the lower value (darker)
    lower = min(session_pct, weekly_pct)
    if lower > 0:
        fill_sweep = (lower / 100) * sweep
        draw.arc(bbox, start_angle, start_angle + fill_sweep, fill=(0, 0, 0, 255), width=4)

    # Session dot (smaller, inner position)
    session_angle = math.radians(start_angle + (session_pct / 100) * sweep)
    dot_radius_inner = radius - 1
    session_x = center + int(dot_radius_inner * math.cos(session_angle))
    session_y = center + int(dot_radius_inner * math.sin(session_angle))
    draw.ellipse([session_x - 3, session_y - 3, session_x + 3, session_y + 3], fill=(0, 0, 0, 255))

    # Weekly dot (larger, outer position) - slightly offset
    weekly_angle = math.radians(start_angle + (weekly_pct / 100) * sweep)
    dot_radius_outer = radius + 1
    weekly_x = center + int(dot_radius_outer * math.cos(weekly_angle))
    weekly_y = center + int(dot_radius_outer * math.sin(weekly_angle))
    # Draw as ring instead of solid dot to differentiate
    draw.ellipse([weekly_x - 4, weekly_y - 4, weekly_x + 4, weekly_y + 4], outline=(0, 0, 0, 255), width=2)

    img.save(os.path.join(OUTPUT_DIR, filename))
    print(f"Created {filename}")


if __name__ == "__main__":
    print(f"Generating examples with Session={SESSION}%, Weekly={WEEKLY}%\n")

    create_nested_arcs(SESSION, WEEKLY, "example_1_nested_arcs.png")
    create_split_arc(SESSION, WEEKLY, "example_2_split_arc.png")
    create_stacked_dots(SESSION, WEEKLY, "example_3_stacked_dots.png")

    print(f"\nDone! Check the files in {OUTPUT_DIR}")
