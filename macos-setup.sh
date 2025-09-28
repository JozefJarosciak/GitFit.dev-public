#!/bin/bash
# GitFit.dev macOS Setup Helper
# This script helps configure GitFit.dev for optimal macOS experience

echo "============================================"
echo "   GitFit.dev macOS Configuration Helper"
echo "============================================"
echo

# Check if we're on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo "❌ This script is for macOS only. Current system: $(uname)"
    exit 1
fi

# Create config directories
mkdir -p ~/.gitfitdev/control
mkdir -p ~/.gitfitdev/scripts
mkdir -p ~/Library/Application\ Scripts/com.gitfit.breaks

echo "✅ Created config directories"

# Check macOS version
macos_version=$(sw_vers -productVersion)
echo "🖥️  macOS Version: $macos_version"

# Check if GitFitDev executable exists
if [ ! -f "./GitFitDev" ]; then
    echo "⚠️  GitFitDev executable not found in current directory"
    echo "    Make sure you're running this from the GitFit.dev directory"
fi

echo
echo "🚀 GitFit.dev Access Methods for macOS:"
echo
echo "1. MENU BAR ICON (Primary):"
echo "   • Right-click menu bar icon for full menu"
echo "   • Left-click for quick settings access"
echo "   ⚠️  If menu bar icon doesn't work, use alternatives below"
echo
echo "2. DOCK INTEGRATION:"
echo "   • Right-click dock icon for context menu"
echo "   • App appears in dock when running"
echo
echo "3. COMMAND LINE:"
echo "   • ./GitFitDev --show-settings"
echo "   • ./GitFitDev --toggle-pause"
echo
echo "4. KEYBOARD SHORTCUTS (Manual Setup Required):"
echo "   • Go to System Preferences > Keyboard > Shortcuts"
echo "   • Add custom shortcuts:"
echo "     - Settings: ~/.gitfitdev/scripts/open_settings.sh"
echo "     - Pause:    ~/.gitfitdev/scripts/toggle_pause.sh"
echo "   • Suggested shortcuts:"
echo "     - Cmd+Option+G: Settings"
echo "     - Cmd+Option+Shift+G: Pause Toggle"
echo
echo "5. FILE-BASED CONTROLS:"
echo "   • touch ~/.gitfitdev/control/show_settings"
echo "   • touch ~/.gitfitdev/control/toggle_pause"
echo "   • touch ~/.gitfitdev/control/trigger_break"
echo "   • touch ~/.gitfitdev/control/quit"
echo
echo "6. APPLESCRIPT INTEGRATION:"
echo "   • Scripts created in ~/Library/Application Scripts/"
echo "   • Can be used with Automator or other tools"
echo

echo "📋 Quick Setup Commands:"
echo

# Create shortcut scripts
echo "# Creating keyboard shortcut scripts..."
cat > ~/.gitfitdev/scripts/open_settings.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/../.."
exec ./GitFitDev --show-settings
EOF

cat > ~/.gitfitdev/scripts/toggle_pause.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/../.."
exec ./GitFitDev --toggle-pause
EOF

chmod +x ~/.gitfitdev/scripts/open_settings.sh
chmod +x ~/.gitfitdev/scripts/toggle_pause.sh

echo "✅ Created keyboard shortcut scripts"

# Create AppleScript files
cat > ~/Library/Application\ Scripts/com.gitfit.breaks/open_settings.scpt << 'EOF'
tell application "System Events"
    set appPath to POSIX path of (path to application "GitFitDev")
    do shell script quoted form of appPath & " --show-settings"
end tell
EOF

cat > ~/Library/Application\ Scripts/com.gitfit.breaks/toggle_pause.scpt << 'EOF'
tell application "System Events"
    set appPath to POSIX path of (path to application "GitFitDev")
    do shell script quoted form of appPath & " --toggle-pause"
end tell
EOF

echo "✅ Created AppleScript handlers"

# Create Automator Quick Actions (optional)
cat > ~/Desktop/GitFitDev-Settings.app << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
exec ./GitFitDev --show-settings
EOF

if [ -f ~/Desktop/GitFitDev-Settings.app ]; then
    chmod +x ~/Desktop/GitFitDev-Settings.app
    echo "✅ Created desktop shortcut: ~/Desktop/GitFitDev-Settings.app"
fi

echo
echo "🎯 RECOMMENDATIONS FOR macOS:"
echo
echo "PRIMARY: Try the menu bar icon first"
echo "  • Look for the dumbbell icon in your menu bar"
echo "  • Right-click for full menu, left-click for settings"
echo
echo "BACKUP: Set up keyboard shortcuts"
echo "  1. Open System Preferences > Keyboard > Shortcuts"
echo "  2. Click 'App Shortcuts' in left sidebar"
echo "  3. Click '+' to add new shortcut"
echo "  4. Choose 'All Applications'"
echo "  5. Add these shortcuts:"
echo "     Menu Title: 'Open Settings'"
echo "     Keyboard Shortcut: Cmd+Option+G"
echo "     Script: ~/.gitfitdev/scripts/open_settings.sh"
echo
echo "ALTERNATIVE: Use command line or file controls"
echo "  • Command: ./GitFitDev --show-settings"
echo "  • Touch file: touch ~/.gitfitdev/control/show_settings"
echo
echo "TROUBLESHOOTING:"
echo
echo "If menu bar icon doesn't appear:"
echo "  1. Check if app is running: ps aux | grep GitFitDev"
echo "  2. Restart the app"
echo "  3. Check System Preferences > Security & Privacy > Accessibility"
echo "  4. Use alternative access methods above"
echo
echo "If keyboard shortcuts don't work:"
echo "  1. Check System Preferences > Keyboard > Shortcuts"
echo "  2. Ensure scripts have execute permissions"
echo "  3. Try running scripts manually first"
echo
echo "For debugging:"
echo "  • Check logs: ~/.gitfitdev/debug.log"
echo "  • Test manually: ./GitFitDev --show-settings"
echo
echo "Setup complete! 🎉"
echo
echo "To start GitFit.dev now:"
echo "./GitFitDev"