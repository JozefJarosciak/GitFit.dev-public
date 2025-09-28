# GitFit.dev Linux Usage Guide

GitFit.dev works excellently on Linux! The application now automatically shows a **Control Panel** window when you start it, giving you easy access to all features without needing to use keyboard shortcuts or command line options.

## 🚀 Quick Start

1. **Run the application:**
   ```bash
   ./GitFitDev
   ```
   A control panel window will automatically appear in the top-right corner with buttons for:
   - ⚙️ Open Settings
   - ⏸️ Pause/Resume Breaks
   - 💪 Break Now
   - Minimize (hides to system tray if available)

2. **Optional: Run setup script for additional features:**
   ```bash
   chmod +x linux-setup.sh
   ./linux-setup.sh
   ```

## 🎯 Control Panel Features

The control panel is shown by default and provides:
- **Easy GUI access** to all GitFit.dev features
- **No keyboard shortcuts needed** - just click the buttons
- **Minimize option** to hide the panel when not needed
- **Auto-restore** when clicking the system tray icon (if available)

### Disabling the Control Panel
If you prefer to use keyboard shortcuts or command line:
```bash
touch ~/.gitfitdev/disable_control_panel
```

To re-enable it:
```bash
rm ~/.gitfitdev/disable_control_panel
```

## 🎯 Alternative Access Methods (Optional)

### 1. Keyboard Shortcuts (Best for GNOME)
- **Super+G** - Open settings
- **Super+Shift+G** - Toggle pause/resume

*Auto-configured on GNOME. For other DEs, see manual setup below.*

### 2. Command Line Interface
```bash
./GitFitDev --show-settings    # Open settings
./GitFitDev --toggle-pause     # Toggle pause/resume
```

### 3. File-Based Controls
```bash
# Quick actions via file touches
touch ~/.gitfitdev/control/show_settings
touch ~/.gitfitdev/control/toggle_pause
touch ~/.gitfitdev/control/trigger_break
touch ~/.gitfitdev/control/quit
```

## 🖥️ Desktop Environment Specific

### GNOME
- ✅ Control Panel shows automatically
- ✅ Keyboard shortcuts auto-configured as backup
- ⚠️ System tray may not be clickable
- 🎯 **Recommended:** Use the Control Panel window

### KDE Plasma
- ✅ Control Panel shows automatically
- ✅ System tray usually works too
- 🎯 **Recommended:** Use Control Panel or system tray

### XFCE
- ✅ Control Panel shows automatically
- ✅ System tray usually works too
- 🎯 **Recommended:** Use Control Panel or system tray

### Others (i3, dwm, etc.)
- ✅ Control Panel shows automatically
- 🎯 **Recommended:** Use the Control Panel window
- 💡 **Alternative:** File-based controls or command line

## 🛠️ Manual Keyboard Shortcut Setup

If auto-configuration fails, manually add these shortcuts:

**Command:** `./GitFitDev --show-settings`
**Shortcut:** Super+G

**Command:** `./GitFitDev --toggle-pause`
**Shortcut:** Super+Shift+G

## 📁 File Locations

- **Config:** `~/.gitfitdev/config.json`
- **Logs:** `~/.gitfitdev/debug.log`
- **Controls:** `~/.gitfitdev/control/`
- **Mini Window:** `~/.gitfitdev/show_mini_control`

## 🔧 Troubleshooting

### Control Panel Not Showing
If the control panel doesn't appear:
1. Check if you disabled it: `ls ~/.gitfitdev/disable_control_panel`
2. Re-enable it: `rm ~/.gitfitdev/disable_control_panel`
3. Restart the application

### System Tray Not Working
This is normal on many Linux setups. The Control Panel window provides full access to all features without needing the system tray.

### Keyboard Shortcuts Not Working
1. Check if shortcuts are registered: `gsettings list-recursively | grep gitfit`
2. Manually configure in your DE's shortcut settings
3. Use file-based controls as fallback

### Break Overlays Not Appearing
1. Check if running: `ps aux | grep GitFitDev`
2. Check logs: `tail -f ~/.gitfitdev/debug.log`
3. Test manually: `touch ~/.gitfitdev/control/trigger_break`

## 💡 Pro Tips

1. **Create desktop shortcut:**
   ```bash
   ./linux-setup.sh  # Auto-creates ~/Desktop/GitFitDev-Settings.desktop
   ```

2. **Add to PATH for easy access:**
   ```bash
   sudo ln -s $(pwd)/GitFitDev /usr/local/bin/gitfit
   # Now you can use: gitfit --show-settings
   ```

3. **Autostart configuration:**
   Enable in settings or manually create:
   `~/.config/autostart/GitFitDev.desktop`

4. **Status checking:**
   ```bash
   # Check if running
   ps aux | grep GitFitDev

   # View current settings
   cat ~/.gitfitdev/config.json | jq .
   ```

## 🆘 Getting Help

If you need help:
1. Check logs: `~/.gitfitdev/debug.log`
2. Run setup script: `./linux-setup.sh`
3. Test with: `./GitFitDev --show-settings`
4. File an issue with your desktop environment details

## 🎉 Enjoy!

GitFit.dev is designed to work reliably across all Linux environments. The automatic Control Panel window ensures you can always access all features with a simple GUI, regardless of your desktop environment or system tray support!