#!/bin/bash

# GitFit.dev Installer for macOS
# This script handles all the installation and fixes automatically

clear
echo "======================================"
echo "   GitFit.dev Installer for macOS    "
echo "======================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if GitFit.dev.app exists in the same directory as this script
if [ ! -d "$SCRIPT_DIR/GitFit.dev.app" ]; then
    echo "❌ GitFit.dev.app not found in the installer directory!"
    echo "Please make sure GitFit.dev.app is in the same folder as this installer."
    exit 1
fi

echo "📦 Found GitFit.dev.app"
echo ""

# Check if app already exists in Applications
if [ -d "/Applications/GitFit.dev.app" ]; then
    echo "⚠️  GitFit.dev is already installed."
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    echo "🗑  Removing old version..."
    rm -rf "/Applications/GitFit.dev.app"
fi

# Copy app to Applications
echo "📋 Installing GitFit.dev to Applications..."
cp -R "$SCRIPT_DIR/GitFit.dev.app" "/Applications/"

if [ $? -ne 0 ]; then
    echo "❌ Failed to copy app to Applications!"
    echo "Trying with admin privileges..."
    sudo cp -R "$SCRIPT_DIR/GitFit.dev.app" "/Applications/"
fi

# Fix all the macOS security issues
echo "🔧 Configuring macOS security settings..."

# Remove quarantine attribute
xattr -cr "/Applications/GitFit.dev.app" 2>/dev/null
sudo xattr -cr "/Applications/GitFit.dev.app" 2>/dev/null

# Add to Gatekeeper exceptions
sudo spctl --add "/Applications/GitFit.dev.app" 2>/dev/null

# Make executable
chmod +x "/Applications/GitFit.dev.app/Contents/MacOS/GitFit.dev" 2>/dev/null
sudo chmod +x "/Applications/GitFit.dev.app/Contents/MacOS/GitFit.dev" 2>/dev/null

# Ad-hoc sign the app to prevent "damaged" message
echo "✍️  Signing the application..."
# First sign all frameworks and libraries
find "/Applications/GitFit.dev.app" -name "*.dylib" -o -name "*.so" | while read lib; do
    codesign --force -s - "$lib" 2>/dev/null
done
# Then sign the main executable
codesign --force -s - "/Applications/GitFit.dev.app/Contents/MacOS/GitFit.dev" 2>/dev/null
# Finally sign the whole app bundle
codesign --force --deep -s - "/Applications/GitFit.dev.app" 2>/dev/null

echo ""
echo "✅ Installation complete!"
echo ""
echo "======================================"
echo "         How to use GitFit.dev        "
echo "======================================"
echo ""
echo "1. The app runs in the MENU BAR (top of screen)"
echo "2. Look for the icon near the clock ⏰"
echo "3. Click the icon to access settings"
echo "4. The app will NOT appear in the Dock"
echo ""
echo "======================================"
echo ""

# Ask if user wants to launch now
read -p "Would you like to start GitFit.dev now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Starting GitFit.dev..."
    # Launch the app and capture any errors
    /Applications/GitFit.dev.app/Contents/MacOS/GitFit.dev > /tmp/gitfit_launch.log 2>&1 &
    APP_PID=$!

    # Wait a moment to see if it's still running
    sleep 2

    if ps -p $APP_PID > /dev/null; then
        echo ""
        echo "✨ GitFit.dev is now running!"
        echo "Look for the icon in your menu bar (top right of screen)"
    else
        echo ""
        echo "⚠️  GitFit.dev may have crashed during startup."
        echo "Check /tmp/gitfit_launch.log or ~/.gitfitdev/crash.log for details"
        echo ""
        echo "You can also try running it manually:"
        echo "  /Applications/GitFit.dev.app/Contents/MacOS/GitFit.dev"
    fi
else
    echo "You can start GitFit.dev later from Applications folder"
fi

echo ""
echo "Press any key to close this installer..."
read -n 1 -s