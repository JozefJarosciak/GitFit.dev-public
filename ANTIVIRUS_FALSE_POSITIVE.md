# 🛡️ Antivirus False Positive Notice

## ⚠️ Known Issue: Windows Defender Detection

If you're seeing a warning like:
- `Trojan:Script/Wacatac.B!ml`
- "This program is dangerous and executes commands from an attacker"
- Chrome blocking the download

**This is a FALSE POSITIVE** - your antivirus software is incorrectly flagging our legitimate application.

## 🔍 Why This Happens

GitFit.dev is built using PyInstaller, which packages Python applications into standalone executables. Unfortunately, this technique is also used by malware, causing antivirus software to flag legitimate applications.

**This is a well-known issue affecting many legitimate Python applications.**

## ✅ Safe Download Instructions

### For Windows Defender:
1. **Temporarily disable real-time protection**:
   - Windows Settings → Update & Security → Windows Security → Virus & threat protection
   - Click "Manage settings" under Virus & threat protection settings
   - Turn off "Real-time protection" temporarily
   - Download and install GitFit.dev
   - Turn real-time protection back on

2. **Add exclusion** (recommended):
   - Windows Settings → Update & Security → Windows Security → Virus & threat protection
   - Click "Manage settings" under Virus & threat protection settings
   - Click "Add or remove exclusions"
   - Add exclusion for the downloaded GitFitDev installer and installation folder

### For Chrome Downloads:
1. When Chrome blocks the download, click the up arrow (^) next to the download
2. Click "Keep" to download anyway
3. If Chrome shows "This file is dangerous", click "Keep anyway"

### For Other Antivirus Software:
- Add GitFitDev to your antivirus whitelist/exclusions
- Temporarily disable antivirus during installation
- Report as false positive to your antivirus vendor

## 🔐 Verification (Advanced Users)

You can verify the authenticity of our releases:

1. **Check GitHub Release Page**: All official releases are published at:
   https://github.com/JozefJarosciak/GitFit.dev-public/releases

2. **Verify Source Code**: The complete source code is available for inspection:
   https://github.com/JozefJarosciak/GitFit.dev-public

3. **VirusTotal Scan**: Upload the installer to https://virustotal.com
   - Most engines will show "clean"
   - A few may flag it due to PyInstaller (this is normal)

## 🛠️ For Developers

If you're building GitFit.dev from source, you can:

1. **Build it yourself** from the source code
2. **Use code signing** to prevent false positives:
   - Run `BUILD.bat` → Option [S] for code signing setup
   - Purchase a code signing certificate (~$200-400/year)
   - Self-sign for personal use (users will see "Unknown Publisher")

## 📞 Need Help?

If you're still concerned or need assistance:
- Open an issue at: https://github.com/JozefJarosciak/GitFit.dev-public/issues
- Include your antivirus software name and version
- We're working on implementing code signing to eliminate these false positives

## 🎯 Future Plans

We are actively working on:
- [ ] Implementing code signing certificates
- [ ] Alternative distribution methods (Windows Store, etc.)
- [ ] Working with antivirus vendors to whitelist our application

Thank you for your patience and for supporting GitFit.dev! 💪