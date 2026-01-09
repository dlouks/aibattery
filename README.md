# AI Battery

A macOS menu bar app and CLI tool that shows your AI API usage like a battery indicator.

![Menu Bar](docs/menubar.png)

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/dlouks/aibattery/main/install.sh | bash
```

After install, start the app once with:
```bash
~/.aibattery/AIBattery.app/Contents/MacOS/AIBattery &
```

It will auto-start on future logins.

This installs:
- **Menu bar app** - Shows nested arcs (outer = weekly, inner = session usage)
- **CLI tool** - Run `aibattery` in terminal for detailed view

## Prerequisites

- **macOS** (uses native menu bar APIs)
- **Python 3** (venv created automatically)
- **Node.js** >= 18.x with npm
- **Claude CLI** installed and logged in (`claude` command must work)

### Installing Claude CLI

If you don't have the Claude CLI:
```bash
npm install -g @anthropic-ai/claude-code
claude  # Follow prompts to authenticate
```

## What You Get

### Menu Bar Icon
- Nested arc indicator in your menu bar
- Outer arc = weekly usage, Inner arc = session usage
- Click to see detailed breakdown with battery bars
- Auto-refreshes every 10 minutes

### CLI Tool
```bash
aibattery           # Interactive view with auto-refresh
aibattery --help    # Show options
```

## Manual Installation

If you prefer to install manually:

```bash
# Clone the repo
git clone https://github.com/dlouks/aibattery.git ~/.aibattery
cd ~/.aibattery

# Create Python venv and install dependencies
python3 -m venv venv
venv/bin/pip install rumps pillow

# Install Node dependencies and build CLI
npm install
npm run build

# Generate menu bar icons
venv/bin/python generate_icons.py

# Start the menu bar app
venv/bin/python tray.py
```

To auto-start on login, update and copy the LaunchAgent:
```bash
sed "s|INSTALL_PATH|$HOME/.aibattery|g" com.aibattery.plist > ~/Library/LaunchAgents/com.aibattery.plist
launchctl load ~/Library/LaunchAgents/com.aibattery.plist
```

## Uninstall

```bash
~/.aibattery/uninstall.sh
```

Or manually:
```bash
launchctl unload ~/Library/LaunchAgents/com.aibattery.plist
rm ~/Library/LaunchAgents/com.aibattery.plist
rm -rf ~/.aibattery
```

## How It Works

The app fetches usage data directly from the Anthropic API using the OAuth credentials stored by Claude Code in your macOS Keychain. This is a lightweight metadata query that doesn't consume any Claude tokens.

Usage data is cached locally in `usage-data.json` and displayed in both the menu bar icon and dropdown menu.

## Troubleshooting

**Menu bar icon doesn't appear:**
- Make sure `python3 tray.py` runs without errors
- Check that rumps is installed: `pip3 install rumps`

**Usage shows 0% or doesn't update:**
- Verify `claude /usage` works in your terminal
- Check `~/.aibattery/usage-data.json` has recent data
- Click "Refresh" in the menu bar dropdown

**"claude: command not found":**
- Install Claude CLI: `npm install -g @anthropic-ai/claude-code`
- Make sure it's in your PATH
