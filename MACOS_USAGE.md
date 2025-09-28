# GitFit.dev macOS Usage Guide

GitFit.dev works great on macOS! While menu bar (system tray) support is generally good on Mac, we provide multiple access methods for maximum reliability and user preference.

## 🚀 Quick Start

1. **Run the application:**
   ```bash
   ./GitFitDev
   ```

2. **Look for the menu bar icon:**
   - Small dumbbell icon in your menu bar (top-right area)
   - Right-click for full menu, left-click for settings

3. **If menu bar doesn't work:**
   ```bash
   ./GitFitDev --show-settings
   ```

4. **Optional setup:**
   ```bash
   chmod +x macos-setup.sh
   ./macos-setup.sh
   ```

## 🎯 Access Methods (Ranked by Reliability)

### 1. Menu Bar Icon (Primary - Usually Works)
- **📍 Location:** Menu bar (top-right, near clock)
- **🖱️ Right-click:** Full context menu with all options
- **🖱️ Left-click:** Quick access to settings
- **🎯 Best for:** Most Mac users

### 2. Command Line Interface (Most Reliable)
```bash
./GitFitDev --show-settings    # Open settings
./GitFitDev --toggle-pause     # Toggle pause/resume
./GitFitDev --show-daily       # Show daily progress
```
- **🎯 Best for:** Terminal users, troubleshooting

### 3. Dock Integration
- **📍 Right-click dock icon** when app is running
- **Enhanced context menu** with common actions
- **🎯 Best for:** Users who prefer dock interaction

### 4. Keyboard Shortcuts (Manual Setup)
```bash
# Scripts are auto-created at:
~/.gitfitdev/scripts/open_settings.sh
~/.gitfitdev/scripts/toggle_pause.sh
```

**Manual Setup in System Preferences:**
1. Go to **System Preferences > Keyboard > Shortcuts**
2. Select **Services** in left sidebar
3. Click **+** to add new shortcut
4. Set up:
   - **Settings:** `Cmd+Option+G` → `~/.gitfitdev/scripts/open_settings.sh`
   - **Pause:** `Cmd+Option+Shift+G` → `~/.gitfitdev/scripts/toggle_pause.sh`

### 5. File-Based Controls (Scriptable)
```bash
# Quick actions via file touches
touch ~/.gitfitdev/control/show_settings
touch ~/.gitfitdev/control/toggle_pause
touch ~/.gitfitdev/control/trigger_break
touch ~/.gitfitdev/control/quit
```
- **🎯 Best for:** Integration with other tools, automation

### 6. AppleScript Integration (Advanced)
```applescript
# Auto-created scripts in:
~/Library/Application Scripts/com.gitfit.breaks/

# Example usage:
osascript ~/Library/Application\ Scripts/com.gitfit.breaks/open_settings.scpt
```
- **🎯 Best for:** Automator workflows, advanced automation

## 🛠️ Setup Instructions

### Automatic Setup
```bash
chmod +x macos-setup.sh
./macos-setup.sh
```

### Manual Keyboard Shortcuts
1. **Open System Preferences**
2. **Go to Keyboard > Shortcuts**
3. **Select "App Shortcuts"**
4. **Click "+" to add new shortcut**
5. **Configure:**
   - Application: All Applications
   - Menu Title: Custom
   - Keyboard Shortcut: `Cmd+Option+G`
   - Script: `~/.gitfitdev/scripts/open_settings.sh`

### Dock Context Menu Enhancement
The app automatically enhances the dock menu when running. Right-click the dock icon to see additional options.

## 📁 File Locations

- **Config:** `~/.gitfitdev/config.json`
- **Logs:** `~/.gitfitdev/debug.log`
- **Controls:** `~/.gitfitdev/control/`
- **Scripts:** `~/.gitfitdev/scripts/`
- **AppleScript:** `~/Library/Application Scripts/com.gitfit.breaks/`
- **LaunchAgent:** `~/Library/LaunchAgents/com.gitfit.breaks.plist`

## 🔧 Troubleshooting

### Menu Bar Icon Not Appearing

**Check if app is running:**
```bash
ps aux | grep GitFitDev
```

**Common solutions:**
1. **Restart the app** - Sometimes takes a moment to appear
2. **Check menu bar space** - Hide other icons if crowded
3. **Security permissions** - Check System Preferences > Security & Privacy > Accessibility
4. **Use alternatives** - Command line always works

### Keyboard Shortcuts Not Working

1. **Verify scripts exist:**
   ```bash
   ls -la ~/.gitfitdev/scripts/
   ```

2. **Test scripts manually:**
   ```bash
   ~/.gitfitdev/scripts/open_settings.sh
   ```

3. **Check permissions:**
   ```bash
   chmod +x ~/.gitfitdev/scripts/*.sh
   ```

4. **Recreate shortcuts in System Preferences**

### Break Overlays Not Appearing

1. **Check if running:**
   ```bash
   ps aux | grep GitFitDev
   ```

2. **Test manually:**
   ```bash
   touch ~/.gitfitdev/control/trigger_break
   ```

3. **Check logs:**
   ```bash
   tail -f ~/.gitfitdev/debug.log
   ```

### App Won't Start

1. **Check executable permissions:**
   ```bash
   chmod +x GitFitDev
   ```

2. **Run from Terminal to see errors:**
   ```bash
   ./GitFitDev
   ```

3. **Check macOS Gatekeeper:**
   - Right-click app → Open (for unsigned apps)
   - System Preferences > Security & Privacy

## 💡 Pro Tips

### 1. Create Dock Shortcut
```bash
# Add to Dock permanently
cp GitFitDev /Applications/
# Then drag from Applications to Dock
```

### 2. Status Bar Script
Create a simple status checker:
```bash
#!/bin/bash
if pgrep -f GitFitDev > /dev/null; then
    echo "✅ GitFit.dev is running"
else
    echo "❌ GitFit.dev is not running"
fi
```

### 3. Integration with Other Apps

**Raycast/Alfred integration:**
```bash
# Add to PATH
sudo ln -s $(pwd)/GitFitDev /usr/local/bin/gitfit

# Now you can use:
gitfit --show-settings
```

**Shortcuts app integration:**
- Add scripts to Shortcuts app for Siri activation
- "Hey Siri, open GitFit settings"

### 4. Notification Preferences
Configure native macOS notifications:
- System Preferences > Notifications > GitFit.dev
- Enable banners, sounds, etc.

## 🎨 Customization

### Menu Bar Icon
The app uses a dumbbell icon in the menu bar. If you don't see it:
1. Check if your menu bar is full
2. Try Command-dragging other icons to rearrange
3. Use "Bartender" or similar apps to manage menu bar icons

### Dock Badge
The app can show status in the dock badge (implementation varies by version).

## 🆘 Getting Help

### Debug Information
```bash
# System info
sw_vers
echo "macOS Version: $(sw_vers -productVersion)"

# App status
ps aux | grep GitFitDev

# Permissions
ls -la ~/.gitfitdev/

# Recent logs
tail -20 ~/.gitfitdev/debug.log
```

### Common Issues
1. **"App can't be opened"** - Gatekeeper issue, right-click → Open
2. **Menu bar icon missing** - Use command line alternatives
3. **Breaks not triggering** - Check active hours in settings
4. **Permission errors** - Check file permissions with `ls -la`

### Support Resources
- Run setup script: `./macos-setup.sh`
- Test basic functionality: `./GitFitDev --show-settings`
- Check logs for specific errors
- File issues with system details

## 🎉 Enjoy!

GitFit.dev is designed to work reliably on macOS with multiple fallback options. The menu bar integration provides native Mac experience, while command line and file-based controls ensure you always have access regardless of system state.

**Happy coding with healthy breaks! 💪**