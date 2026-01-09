#!/bin/bash
set -e

# AI Battery Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/dlouks/aibattery/main/install.sh | bash

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
    # Remove copied node_modules (has broken symlinks), will reinstall fresh
    [ -d "$INSTALL_DIR/node_modules" ] && rm -rf "$INSTALL_DIR/node_modules"
else
    echo "📦 Downloading..."
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
pkill -f "tray.py" 2>/dev/null || true
sleep 1

# Make app executable (git may not preserve permissions)
chmod +x "$INSTALL_DIR/AIBattery.app/Contents/MacOS/AIBattery"

# Fetch initial usage data
"$INSTALL_DIR/venv/bin/python" "$INSTALL_DIR/fetch-usage.py" >/dev/null 2>&1 || true

# Start the service for login auto-start
launchctl load "$LAUNCHAGENTS_DIR/$PLIST_NAME" 2>/dev/null || true

# Explicitly start the service now (launchctl load only schedules for login)
launchctl start com.aibattery 2>/dev/null || true

# Start the app using osascript (survives pipe context)
sleep 1
if ! pgrep -f "tray.py" > /dev/null; then
    osascript -e "do shell script \"open '$INSTALL_DIR/AIBattery.app'\"" &
fi

echo ""
echo "✅ AI Battery installed!"
echo ""
echo "   CLI: aibattery"
echo "   Uninstall: ~/.aibattery/uninstall.sh"
