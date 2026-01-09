#!/usr/bin/env python3
"""
AI Battery - macOS Menu Bar App
Shows AI API usage as a battery indicator
"""

import io
import json
import math
import os
import subprocess
import sys
import tempfile
from datetime import datetime

from PIL import Image, ImageDraw

import rumps

APP_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(APP_DIR, 'icons')
REFRESH_INTERVAL = 600  # 10 minutes
ICON_SIZE = 22


def create_nested_arc_icon(session_pct, weekly_pct):
    """Create nested arc icon - outer for weekly, inner for session"""
    img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center = ICON_SIZE // 2
    start_angle = 135
    sweep = 270

    # Outer arc (weekly)
    outer_r = (ICON_SIZE - 2) // 2
    outer_bbox = [center - outer_r, center - outer_r, center + outer_r, center + outer_r]

    # Background arc (faint)
    draw.arc(outer_bbox, start_angle, start_angle + sweep, fill=(0, 0, 0, 70), width=2)
    # Filled portion (weekly)
    if weekly_pct > 0:
        fill_sweep = (weekly_pct / 100) * sweep
        draw.arc(outer_bbox, start_angle, start_angle + fill_sweep, fill=(0, 0, 0, 255), width=2)

    # Inner arc (session)
    inner_r = outer_r - 5
    inner_bbox = [center - inner_r, center - inner_r, center + inner_r, center + inner_r]

    # Background arc (faint)
    draw.arc(inner_bbox, start_angle, start_angle + sweep, fill=(0, 0, 0, 70), width=2)
    # Filled portion (session)
    if session_pct > 0:
        fill_sweep = (session_pct / 100) * sweep
        draw.arc(inner_bbox, start_angle, start_angle + fill_sweep, fill=(0, 0, 0, 255), width=2)

    # Save to temp file and return path
    fd, path = tempfile.mkstemp(suffix='.png')
    os.close(fd)
    img.save(path)
    return path


def get_relative_time(iso_string):
    """Convert ISO timestamp to relative time string"""
    if not iso_string:
        return None

    try:
        reset_date = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        now = datetime.now(reset_date.tzinfo) if reset_date.tzinfo else datetime.now()
        diff = reset_date - now

        if diff.total_seconds() <= 0:
            return "now"

        diff_mins = int(diff.total_seconds() / 60)
        diff_hours = int(diff.total_seconds() / 3600)
        diff_days = int(diff.total_seconds() / 86400)

        if diff_mins < 60:
            return f"in {diff_mins} minute{'s' if diff_mins != 1 else ''}"
        if diff_hours < 24:
            return f"in {diff_hours} hour{'s' if diff_hours != 1 else ''}"
        return f"in {diff_days} day{'s' if diff_days != 1 else ''}"
    except:
        return None

class ClaudeBatteryApp(rumps.App):
    def __init__(self):
        initial_icon = os.path.join(ICON_DIR, 'battery_50.png')
        super().__init__("", icon=initial_icon, template=True, quit_button=None)
        self.usage = None
        self.refresh_usage()

        self.timer = rumps.Timer(self.refresh_usage, REFRESH_INTERVAL)
        self.timer.start()

    def noop(self, _=None):
        """No-op callback - makes items appear white instead of grey"""
        pass

    def get_battery_visual(self, remaining):
        """Create a sleek battery visualization"""
        segments = 10
        filled = round((remaining / 100) * segments)
        bar = '▓' * filled + '░' * (segments - filled)
        return f"[{bar}]"

    def get_status_icon(self, remaining):
        """Get contextual icon based on charge level"""
        if remaining < 5:
            return "🔴"
        elif remaining <= 20:
            return "🟡"
        else:
            return "🟢"

    def refresh_usage(self, _=None):
        try:
            # First try to fetch fresh data from claude /usage
            result = subprocess.run(
                [sys.executable, 'fetch-usage.py'],
                capture_output=True,
                text=True,
                cwd=APP_DIR,
                timeout=60
            )
            # Whether fetch succeeded or not, read from the JSON file
            usage_file = os.path.join(APP_DIR, 'usage-data.json')
            with open(usage_file, 'r') as f:
                data = json.load(f)

            # Convert to the format expected by update_display
            claude = data.get('claude', {})
            self.usage = {
                'session': {
                    'remaining': 100 - claude.get('session', {}).get('percentUsed', 0),
                    'resetAt': claude.get('session', {}).get('resetAt'),
                },
                'weekly': {
                    'remaining': 100 - claude.get('weekly', {}).get('percentUsed', 0),
                    'resetAt': claude.get('weekly', {}).get('resetAt'),
                },
                'weeklySonnet': {
                    'remaining': 100 - claude.get('weeklySonnet', {}).get('percentUsed', 0),
                    'resetAt': claude.get('weeklySonnet', {}).get('resetAt'),
                },
            }
            self.update_display()
        except Exception as e:
            print(f"Error: {e}")

    def update_display(self):
        if not self.usage:
            return

        session = self.usage['session']['remaining']
        weekly = self.usage['weekly']['remaining']

        # Update menu bar icon with nested arcs
        icon_path = create_nested_arc_icon(session, weekly)
        self.icon = icon_path

        # Build menu
        self.menu.clear()

        # Header
        self.menu.add(rumps.MenuItem("AI Battery", callback=None))
        self.menu.add(rumps.separator)

        # Claude section
        self.menu.add(rumps.MenuItem("Claude", callback=None))

        # Session
        session_icon = self.get_status_icon(session)
        session_bar = self.get_battery_visual(session)
        self.menu.add(rumps.MenuItem(
            f"{session_icon}  Session  {session_bar}  {session}% left", callback=None))
        reset_time = get_relative_time(self.usage['session'].get('resetAt'))
        if reset_time:
            self.menu.add(rumps.MenuItem(
                f"      Resets {reset_time}",
                callback=None
            ))

        self.menu.add(rumps.separator)

        # Weekly
        weekly_icon = self.get_status_icon(weekly)
        weekly_bar = self.get_battery_visual(weekly)
        self.menu.add(rumps.MenuItem(
            f"{weekly_icon}  Weekly  {weekly_bar}  {weekly}% left", callback=None))
        reset_time = get_relative_time(self.usage['weekly'].get('resetAt'))
        if reset_time:
            self.menu.add(rumps.MenuItem(
                f"      Resets {reset_time}",
                callback=None
            ))

        # Sonnet (if available)
        if self.usage.get('weeklySonnet'):
            sonnet = self.usage['weeklySonnet']['remaining']
            sonnet_icon = self.get_status_icon(sonnet)
            sonnet_bar = self.get_battery_visual(sonnet)

            self.menu.add(rumps.separator)
            self.menu.add(rumps.MenuItem(
                f"{sonnet_icon}  Sonnet  {sonnet_bar}  {sonnet}% left", callback=None))
            reset_time = get_relative_time(self.usage['weeklySonnet'].get('resetAt'))
            if reset_time:
                self.menu.add(rumps.MenuItem(
                    f"      Resets {reset_time}",
                    callback=None
                ))

        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("Refresh", callback=self.refresh_usage))
        self.menu.add(rumps.MenuItem("Quit", callback=rumps.quit_application))

if __name__ == "__main__":
    ClaudeBatteryApp().run()
