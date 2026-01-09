#!/bin/bash
set -e

# Claude Battery Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/dlouks/aibattery/master/install.sh | bash

INSTALL_DIR="$HOME/.aibattery"
PLIST_NAME="com.aibattery.plist"
LAUNCHAGENTS_DIR="$HOME/Library/LaunchAgents"

echo "🔋 Installing Claude Battery..."

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

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install --user rumps pillow pexpect >/dev/null 2>&1 || pip3 install rumps pillow pexpect

# Install Node dependencies and build CLI
echo "📦 Installing Node dependencies..."
npm install >/dev/null 2>&1
npm run build >/dev/null 2>&1

# Link CLI globally
echo "🔗 Linking CLI command..."
npm link >/dev/null 2>&1 || true

# Generate icons if not present
if [ ! -f "$INSTALL_DIR/icons/battery_50.png" ]; then
    echo "🎨 Generating icons..."
    python3 generate_icons.py >/dev/null 2>&1
fi

# Setup LaunchAgent for auto-start
echo "🚀 Setting up auto-start..."
mkdir -p "$LAUNCHAGENTS_DIR"

# Update plist with actual install path
sed "s|INSTALL_PATH|$INSTALL_DIR|g" "$INSTALL_DIR/com.aibattery.plist" > "$LAUNCHAGENTS_DIR/$PLIST_NAME"

# Stop existing instance if running
launchctl unload "$LAUNCHAGENTS_DIR/$PLIST_NAME" 2>/dev/null || true
pkill -f "aibattery.*tray.py" 2>/dev/null || true

# Start the service
launchctl load "$LAUNCHAGENTS_DIR/$PLIST_NAME"

# Also start the tray app directly (launchctl can be slow)
python3 "$INSTALL_DIR/tray.py" &

echo ""
echo "✅ Claude Battery installed!"
echo ""
echo "   Menu bar icon should appear now."
echo "   It will auto-start on login."
echo ""
echo "   Commands:"
echo "   - aibattery          Run CLI"
echo "   - aibattery --help   Show options"
echo ""
echo "   To uninstall:"
echo "   ~/.aibattery/uninstall.sh"
