#!/bin/bash
set -e

# AI Battery Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/dlouks/aibattery/master/install.sh | bash

INSTALL_DIR="$HOME/.aibattery"
PLIST_NAME="com.aibattery.plist"
LAUNCHAGENTS_DIR="$HOME/Library/LaunchAgents"

echo "🔋 Installing AI Battery..."

# Create install directory
mkdir -p "$INSTALL_DIR"

# If running from repo, copy files; otherwise clone
if [ -f "$(dirname "$0")/tray.py" ]; then
    echo "📦 Copying files..."
    cp -r "$(dirname "$0")"/* "$INSTALL_DIR/"
else
    echo "📦 Downloading..."
    # Replace with your actual repo URL
    git clone https://github.com/dlouks/aibattery.git "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip >/dev/null 2>&1
"$INSTALL_DIR/venv/bin/pip" install rumps pillow >/dev/null 2>&1

# Install Node dependencies and build CLI
echo "📦 Installing Node dependencies..."
npm install >/dev/null 2>&1
npm run build >/dev/null 2>&1
chmod +x "$INSTALL_DIR/dist/cli.js"

# Link CLI globally
echo "🔗 Linking CLI command..."
npm link >/dev/null 2>&1 || true

# Generate icons if not present
if [ ! -f "$INSTALL_DIR/icons/battery_50.png" ]; then
    echo "🎨 Generating icons..."
    "$INSTALL_DIR/venv/bin/python" generate_icons.py >/dev/null 2>&1
fi

# Setup LaunchAgent for auto-start
echo "🚀 Setting up auto-start..."
mkdir -p "$LAUNCHAGENTS_DIR"

# Update plist with actual install path
sed "s|INSTALL_PATH|$INSTALL_DIR|g" "$INSTALL_DIR/com.aibattery.plist" > "$LAUNCHAGENTS_DIR/$PLIST_NAME"

# Stop existing instance if running
launchctl unload "$LAUNCHAGENTS_DIR/$PLIST_NAME" 2>/dev/null || true
pkill -f "aibattery.*tray.py" 2>/dev/null || true

# Make app executable (git may not preserve permissions)
chmod +x "$INSTALL_DIR/AIBattery.app/Contents/MacOS/AIBattery"

# Fetch initial usage data
"$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/fetch-usage.py" >/dev/null 2>&1 || true

# Start the service (RunAtLoad=true will start it immediately)
launchctl load "$LAUNCHAGENTS_DIR/$PLIST_NAME"

echo ""
echo "✅ AI Battery installed!"
echo ""
echo "   Menu bar icon should appear now."
echo "   It will auto-start on login."
echo ""
echo "   CLI commands (may need new terminal):"
echo "   - aibattery          Run CLI"
echo "   - aibattery --help   Show options"
echo ""
echo "   To uninstall:"
echo "   ~/.aibattery/uninstall.sh"
