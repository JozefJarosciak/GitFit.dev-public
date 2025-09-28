#!/bin/bash
# GitFit.dev Linux Setup Helper
# This script helps configure GitFit.dev for optimal Linux experience

echo "============================================"
echo "   GitFit.dev Linux Configuration Helper"
echo "============================================"
echo

# Create config directory
mkdir -p ~/.gitfitdev/control

echo "✅ Created config directories"

# Check desktop environment
if [ "$XDG_CURRENT_DESKTOP" = "GNOME" ] || [ "$DESKTOP_SESSION" = "gnome" ]; then
    echo "🖥️  GNOME detected - keyboard shortcuts will be configured automatically"
elif [ "$XDG_CURRENT_DESKTOP" = "KDE" ] || [ "$DESKTOP_SESSION" = "kde" ]; then
    echo "🖥️  KDE detected - consider adding custom shortcuts in System Settings"
elif [ "$XDG_CURRENT_DESKTOP" = "XFCE" ] || [ "$DESKTOP_SESSION" = "xfce" ]; then
    echo "🖥️  XFCE detected - configure shortcuts in Settings > Keyboard"
else
    echo "🖥️  Desktop environment: ${XDG_CURRENT_DESKTOP:-unknown}"
fi

echo
echo "🚀 GitFit.dev Access Methods:"
echo
echo "1. KEYBOARD SHORTCUTS (Auto-configured for GNOME):"
echo "   • Super+G           → Open settings"
echo "   • Super+Shift+G     → Toggle pause/resume"
echo
echo "2. COMMAND LINE:"
echo "   • ./GitFitDev --show-settings"
echo "   • ./GitFitDev --toggle-pause"
echo
echo "3. FILE-BASED CONTROLS:"
echo "   • touch ~/.gitfitdev/control/show_settings"
echo "   • touch ~/.gitfitdev/control/toggle_pause"
echo "   • touch ~/.gitfitdev/control/trigger_break"
echo "   • touch ~/.gitfitdev/control/quit"
echo
echo "4. OPTIONAL MINI CONTROL WINDOW:"
echo "   • touch ~/.gitfitdev/show_mini_control"
echo "   • (Creates small floating control panel)"
echo

echo "📋 Quick Commands:"
echo
echo "# Open settings now:"
echo "./GitFitDev --show-settings"
echo
echo "# Enable mini control window:"
echo "touch ~/.gitfitdev/show_mini_control"
echo
echo "# Create desktop shortcut:"
cat > ~/Desktop/GitFitDev-Settings.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=GitFit.dev Settings
Comment=Open GitFit.dev settings
Exec=./GitFitDev --show-settings
Icon=applications-utilities
Categories=Utility;
EOF

if [ -f ~/Desktop/GitFitDev-Settings.desktop ]; then
    chmod +x ~/Desktop/GitFitDev-Settings.desktop
    echo "✅ Created desktop shortcut: ~/Desktop/GitFitDev-Settings.desktop"
fi

echo
echo "🎯 RECOMMENDATION FOR LINUX:"
echo "Since system tray support varies by desktop environment,"
echo "we recommend using keyboard shortcuts (Super+G) or the"
echo "command line interface for the most reliable experience."
echo
echo "For GUI access without tray, enable the mini control window:"
echo "  touch ~/.gitfitdev/show_mini_control"
echo
echo "Setup complete! 🎉"