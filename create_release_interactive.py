#!/usr/bin/env python3
"""
Create GitHub release for GitFit.dev v1.0.0 - Interactive version
"""
import requests
import json
import os
import sys
from datetime import datetime

# Release information
REPO_OWNER = "JozefJarosciak"
REPO_NAME = "GitFit.dev-public"
TAG_NAME = "v1.0.0"
RELEASE_NAME = "GitFit.dev v1.0.0 - Initial Release"

RELEASE_BODY = """## 🎉 GitFit.dev v1.0.0 - Initial Release

**GitFit.dev** is a cross-platform desktop application that displays fullscreen break reminders with fitness-themed messages at configurable intervals, helping developers maintain their health and productivity.

### ✨ Key Features
- 🔒 **Fullscreen break reminders** that cannot be dismissed until timer expires
- ⚡ **Smart scheduling** with sub-hourly intervals and precise timing (e.g., every 30 min at :00/:30)
- 🎨 **10 beautiful themes** to choose from (green, blue, purple, dark, sunset, pink, teal, indigo, red, forest)
- 🔔 **Native notifications** with toast and flash warnings before breaks
- 📅 **Active hours support** that respects your work schedule (9 AM - 5 PM default)
- 🚀 **System tray integration** that runs quietly in the background
- 💪 **Fitness-focused messages** with motivational exercise suggestions
- 🌍 **Multi-language support** (English, Slovak)
- 🎯 **Automatic version checking** for updates

### 📦 Downloads Available
- **Windows Portable**: `GitFitDev.exe` (no installation required - just run it!)
- **Windows ZIP**: `GitFitDev-Windows.zip` (packaged version)

### 🛠️ Quick Installation
1. **Download** `GitFitDev.exe` from the assets below
2. **Run** the executable - no installation required!
3. **Accept** the health disclaimer to continue
4. **Configure** your break intervals and active hours in settings
5. **Stay healthy** while coding! 💚

### 🔧 Default Configuration
- **Break Interval**: Every 60 minutes
- **Break Duration**: 60 seconds
- **Active Hours**: 9:00 AM - 5:00 PM
- **Theme**: Fresh Green
- **Language**: English
- **Pre-warning**: 30 seconds before break

### ⚙️ System Requirements
- **Windows**: 10+ (64-bit)
- **Memory**: 50 MB RAM
- **Disk**: 25 MB free space
- **Network**: Optional (for update checking)

### 🎨 Available Themes
Choose from 10 beautiful color themes in settings:
- **Green** (default) - Fresh and energetic
- **Blue** - Calm and professional
- **Purple** - Creative and inspiring
- **Dark** - Easy on the eyes
- **Sunset** - Warm and cozy
- **Pink** - Soft and friendly
- **Teal** - Modern and clean
- **Indigo** - Deep and focused
- **Red** - Bold and energizing
- **Forest** - Natural and grounding

### 💪 Break Activities
- **Stretching exercises** for neck, shoulders, back, and legs
- **Eye movement** exercises to reduce strain
- **Quick cardio** activities to boost energy
- **Posture corrections** and ergonomic tips
- **Breathing exercises** for relaxation

### 🔄 Smart Scheduling
- **Sub-hourly intervals**: Breaks at predictable times (e.g., 30 min = :00 and :30)
- **Hourly+ intervals**: Customizable minute offset for precision timing
- **Active hours**: Only shows breaks during your work schedule
- **Pause functionality**: Temporarily disable breaks for meetings
- **Skip next break**: One-time skip without changing schedule

### 📝 Release Notes
- Initial public release of GitFit.dev
- Complete break reminder system with customizable intervals (5-480 minutes)
- System tray integration with pause/resume functionality
- Multiple themes and fitness activity types
- Comprehensive settings and configuration options
- Professional build system with GitHub Actions
- Automatic update checking from public repository
- Multi-language support (English/Slovak)
- Health disclaimer and liability protection

### 🤝 Open Source
This project is open source under **AGPL v3.0**!
- 💻 **Source Code**: [GitHub Repository](https://github.com/JozefJarosciak/GitFit.dev-public)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/JozefJarosciak/GitFit.dev-public/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/JozefJarosciak/GitFit.dev-public/discussions)

### 🌐 Website & Support
- 🌐 **Official Website**: [gitfit.dev](https://gitfit.dev)
- 📧 **Contact**: Available through website
- 📖 **Documentation**: Included in application and GitHub README

### 🙏 Acknowledgments
Special thanks to the Python community and all developers who prioritize their health while coding!

---

**Take care of your body. It's the only place you have to live. 💪**

*Made with ❤️ for the developer community*"""

def get_github_token():
    """Get GitHub token from environment or user input"""
    # Try environment variable first
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        return token

    # Ask user for token
    print("GitHub token not found in environment.")
    print("Please enter your GitHub Personal Access Token:")
    print("(Create one at: https://github.com/settings/tokens)")
    token = input("GitHub Token: ").strip()

    if not token:
        print("❌ No token provided")
        return None

    return token

def test_github_api(token):
    """Test if the GitHub token is valid"""
    print("🔍 Testing GitHub API access...")

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    try:
        # Test with a simple API call
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        response.raise_for_status()

        user_info = response.json()
        print(f"✅ GitHub API access successful!")
        print(f"👤 Authenticated as: {user_info.get('login', 'Unknown')}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ GitHub API test failed: {e}")
        return False

def create_release(token):
    """Create the GitHub release"""
    print("🚀 Creating GitFit.dev v1.0.0 Release...")

    # Create release
    api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    release_data = {
        'tag_name': TAG_NAME,
        'target_commitish': 'main',
        'name': RELEASE_NAME,
        'body': RELEASE_BODY,
        'draft': False,
        'prerelease': False
    }

    try:
        response = requests.post(api_url, headers=headers, json=release_data, timeout=30)
        response.raise_for_status()

        release_info = response.json()
        print(f"✅ Release created successfully!")
        print(f"🔗 Release URL: {release_info['html_url']}")
        print(f"📤 Upload assets at: {release_info['html_url']}")

        return release_info

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to create release: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None

def main():
    """Main function"""
    print("🎉 GitFit.dev v1.0.0 Release Creator")
    print("=" * 50)

    # Get GitHub token
    token = get_github_token()
    if not token:
        print("❌ Cannot proceed without GitHub token")
        return False

    # Test API access
    if not test_github_api(token):
        print("❌ Cannot proceed with invalid token")
        return False

    # Create release
    release_info = create_release(token)
    if not release_info:
        print("❌ Release creation failed")
        return False

    print("\n🎉 GitFit.dev v1.0.0 released successfully!")
    print(f"📥 Download build artifacts from:")
    print(f"   https://github.com/{REPO_OWNER}/{REPO_NAME}/actions")
    print(f"📤 Upload artifacts to release at:")
    print(f"   {release_info['html_url']}")
    print(f"\n🌐 Visit your new release: {release_info['html_url']}")

    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    print("\n✅ All done! GitFit.dev v1.0.0 is now live! 🚀")