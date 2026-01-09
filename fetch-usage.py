#!/usr/bin/env python3
"""
Fetch Claude usage data by running `claude /usage` and parsing the TUI output.
"""

import json
import os
import re
import sys
import pexpect
from datetime import datetime

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'usage-data.json')


def parse_time_to_iso(time_str, date_str=None):
    """Convert time string to ISO timestamp."""
    now = datetime.now()

    # Parse the time (e.g., "1am", "6am", "12:59am")
    time_match = re.match(r'(\d+)(?::(\d+))?([ap]m)', time_str.lower())
    if not time_match:
        return None

    hour = int(time_match.group(1))
    minute = int(time_match.group(2)) if time_match.group(2) else 0
    ampm = time_match.group(3)

    if ampm == 'pm' and hour != 12:
        hour += 12
    elif ampm == 'am' and hour == 12:
        hour = 0

    if date_str:
        # Parse date like "Jan 15"
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        date_match = re.match(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+(\d+)', date_str.lower())
        if date_match:
            month = month_map[date_match.group(1)]
            day = int(date_match.group(2))
            year = now.year if month >= now.month else now.year + 1
            reset_dt = datetime(year, month, day, hour, minute)
            return reset_dt.isoformat()
    else:
        # Session reset - today or tomorrow
        reset_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if reset_dt <= now:
            reset_dt = reset_dt.replace(day=reset_dt.day + 1)
        return reset_dt.isoformat()

    return None


def parse_usage_output(output):
    """Parse the TUI output to extract usage percentages and reset times."""
    data = {
        'lastUpdated': datetime.now().isoformat(),
        'claude': {
            'session': {'percentUsed': 0},
            'weekly': {'percentUsed': 0},
            'weeklySonnet': {'percentUsed': 0},
        }
    }

    # Parse session usage (e.g., "91% used")
    session_match = re.search(r'Current session.*?(\d+)%\s*used', output, re.DOTALL)
    if session_match:
        data['claude']['session']['percentUsed'] = int(session_match.group(1))

    # Parse session reset time (e.g., "Resets 1am (America/Chicago)")
    session_reset = re.search(r'Current session.*?Resets\s+(\d+(?::\d+)?[ap]m)', output, re.DOTALL | re.IGNORECASE)
    if session_reset:
        iso_time = parse_time_to_iso(session_reset.group(1))
        if iso_time:
            data['claude']['session']['resetAt'] = iso_time

    # Parse weekly usage (all models)
    weekly_match = re.search(r'all models.*?(\d+)%\s*used', output, re.DOTALL)
    if weekly_match:
        data['claude']['weekly']['percentUsed'] = int(weekly_match.group(1))

    # Parse weekly reset time (e.g., "Resets Jan 15, 6am")
    weekly_reset = re.search(
        r'all models.*?Resets\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d+),?\s*(\d+(?::\d+)?[ap]m)',
        output, re.DOTALL | re.IGNORECASE
    )
    if weekly_reset:
        date_str = f"{weekly_reset.group(1)} {weekly_reset.group(2)}"
        iso_time = parse_time_to_iso(weekly_reset.group(3), date_str)
        if iso_time:
            data['claude']['weekly']['resetAt'] = iso_time
            data['claude']['weeklySonnet']['resetAt'] = iso_time

    # Parse Sonnet usage
    sonnet_match = re.search(r'Sonnet only.*?(\d+)%\s*used', output, re.DOTALL)
    if sonnet_match:
        data['claude']['weeklySonnet']['percentUsed'] = int(sonnet_match.group(1))

    return data


def fetch_usage():
    """Run claude /usage and capture the output."""
    try:
        # Spawn claude /usage with proper terminal dimensions
        child = pexpect.spawn(
            'claude /usage',
            encoding='utf-8',
            timeout=30,
            dimensions=(40, 120)  # rows, cols
        )

        # Give it time to render
        import time
        time.sleep(3)

        # Try to read whatever output is available
        try:
            child.expect(r'.+', timeout=5)
            output = child.before + child.match.group(0)
        except:
            output = child.before if child.before else ""

        # Read any additional output
        try:
            while True:
                child.expect(r'.+', timeout=1)
                output += child.match.group(0)
        except:
            pass

        # Send Escape to exit
        child.send('\x1b')  # ESC key
        time.sleep(0.5)
        child.send('\x1b')  # ESC again
        child.send('q')     # 'q' to quit
        child.send('\x03')  # Ctrl+C

        try:
            child.expect(pexpect.EOF, timeout=3)
        except:
            child.close(force=True)

        return output
    except pexpect.TIMEOUT:
        print("Timeout waiting for claude /usage", file=sys.stderr)
        return None
    except pexpect.EOF:
        print("Unexpected EOF from claude", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def main():
    print("Fetching Claude usage data...")

    output = fetch_usage()
    if not output:
        print("Failed to fetch usage data", file=sys.stderr)
        sys.exit(1)

    # Debug: print raw output
    if '--debug' in sys.argv:
        print("Raw output:")
        print(output)
        print("\n---\n")

    data = parse_usage_output(output)

    # Write to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Usage data saved to {OUTPUT_FILE}")
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
