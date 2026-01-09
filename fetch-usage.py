#!/usr/bin/env python3
"""
Fetch Claude usage data from the official API endpoint.
Uses credentials stored in macOS Keychain by Claude Code.
"""

import json
import os
import subprocess
import sys
from datetime import datetime

OUTPUT_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'usage-data.json'
)

API_URL = "https://api.anthropic.com/api/oauth/usage"


def get_access_token():
    """Get Claude access token from macOS Keychain."""
    try:
        result = subprocess.run(
            ['security', 'find-generic-password', '-s', 'Claude Code-credentials', '-w'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            print(f"Failed to get credentials: {result.stderr}", file=sys.stderr)
            return None

        # Parse the JSON credentials
        creds = json.loads(result.stdout.strip())
        return creds.get('claudeAiOauth', {}).get('accessToken')
    except json.JSONDecodeError as e:
        print(f"Failed to parse credentials JSON: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error getting access token: {e}", file=sys.stderr)
        return None


def fetch_usage_from_api(access_token):
    """Fetch usage data from the Claude API."""
    import urllib.request
    import urllib.error

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'claude-code/2.1.2',
        'anthropic-beta': 'oauth-2025-04-20',
    }

    req = urllib.request.Request(API_URL, headers=headers, method='GET')

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP error {e.code}: {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error fetching usage: {e}", file=sys.stderr)
        return None


def convert_to_output_format(api_data):
    """Convert API response to our output format."""
    data = {
        'lastUpdated': datetime.now().isoformat(),
        'claude': {
            'session': {'percentUsed': 0},
            'weekly': {'percentUsed': 0},
            'weeklySonnet': {'percentUsed': 0},
        }
    }

    if not api_data:
        return data

    # Map five_hour to session
    if 'five_hour' in api_data:
        five_hour = api_data['five_hour']
        data['claude']['session']['percentUsed'] = round(five_hour.get('utilization', 0))
        if 'resets_at' in five_hour:
            data['claude']['session']['resetAt'] = five_hour['resets_at']

    # Map seven_day to weekly
    if 'seven_day' in api_data:
        seven_day = api_data['seven_day']
        data['claude']['weekly']['percentUsed'] = round(seven_day.get('utilization', 0))
        if 'resets_at' in seven_day:
            data['claude']['weekly']['resetAt'] = seven_day['resets_at']
            # Copy reset time to sonnet as well
            data['claude']['weeklySonnet']['resetAt'] = seven_day['resets_at']

    # Check for sonnet-specific data if available
    if 'sonnet' in api_data:
        sonnet = api_data['sonnet']
        data['claude']['weeklySonnet']['percentUsed'] = round(sonnet.get('utilization', 0))
        if 'resets_at' in sonnet:
            data['claude']['weeklySonnet']['resetAt'] = sonnet['resets_at']

    return data


def main():
    debug = '--debug' in sys.argv

    if debug:
        print("Fetching Claude usage data from API...")

    # Get access token from Keychain
    access_token = get_access_token()
    if not access_token:
        print("Could not get access token from Keychain", file=sys.stderr)
        print("Make sure Claude Code is installed and you're logged in", file=sys.stderr)
        sys.exit(1)

    if debug:
        print(f"Got access token: {access_token[:20]}...")

    # Fetch from API
    api_data = fetch_usage_from_api(access_token)
    if debug:
        print(f"API response: {json.dumps(api_data, indent=2)}")

    # Convert to our format
    data = convert_to_output_format(api_data)

    # Write to file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Usage data saved to {OUTPUT_FILE}")
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
