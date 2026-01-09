#!/bin/bash

# AI Battery Uninstaller

INSTALL_DIR="$HOME/.aibattery"
PLIST_NAME="com.aibattery.plist"
LAUNCHAGENTS_DIR="$HOME/Library/LaunchAgents"

echo "🔋 Uninstalling AI Battery..."

# Stop the service
launchctl unload "$LAUNCHAGENTS_DIR/$PLIST_NAME" 2>/dev/null || true
pkill -f "aibattery.*tray.py" 2>/dev/null || true

# Remove LaunchAgent
rm -f "$LAUNCHAGENTS_DIR/$PLIST_NAME"

# Remove install directory
rm -rf "$INSTALL_DIR"

# Remove global npm link
npm unlink -g aibattery 2>/dev/null || true

echo "✅ AI Battery uninstalled."
