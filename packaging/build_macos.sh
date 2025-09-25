#!/bin/bash
# GitFit.dev macOS Build Script
# Run this on MacInCloud or any Mac system

set -e  # Exit on error

echo "============================"
echo " GitFit.dev macOS Builder"
echo "============================"
echo ""

# Auto-install Homebrew if needed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Configuration
APP_NAME="GitFit.dev"
APP_VERSION="1.0.3"
BUNDLE_ID="dev.gitfit.app"
BUILD_DIR="dist"
DMG_NAME="GitFitDev-${APP_VERSION}-macOS"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "${YELLOW}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install it first.${NC}"
    echo "Run: brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d" " -f2)
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip3 install --upgrade pip
pip3 install pyinstaller pillow pystray pyobjc-framework-Cocoa

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf build dist *.spec
echo -e "${GREEN}✓ Cleaned${NC}"

# Create app icon if not exists
if [ ! -f "assets/icon.icns" ]; then
    echo -e "${YELLOW}Creating macOS icon...${NC}"
    python3 packaging/create_mac_icon.py
    echo -e "${GREEN}✓ Icon created${NC}"
fi

# Build with PyInstaller
echo -e "${YELLOW}Building application...${NC}"
python3 -m PyInstaller \
    --name="${APP_NAME}" \
    --windowed \
    --onefile \
    --icon="assets/icon.icns" \
    --osx-bundle-identifier="${BUNDLE_ID}" \
    --add-data "gitfitdev/lang_en.py:gitfitdev" \
    --add-data "gitfitdev/lang_sk.py:gitfitdev" \
    --hidden-import="gitfitdev.lang_en" \
    --hidden-import="gitfitdev.lang_sk" \
    --hidden-import="pystray._darwin" \
    --exclude-module="tk" \
    --exclude-module="tkinter" \
    --noupx \
    packaging/entry.py

echo -e "${GREEN}✓ Application built${NC}"

# Fix permissions
chmod +x "${BUILD_DIR}/${APP_NAME}.app/Contents/MacOS/${APP_NAME}"

# Create DMG installer
echo -e "${YELLOW}Creating DMG installer...${NC}"

# Create temporary DMG directory
DMG_TEMP="${BUILD_DIR}/dmg_temp"
rm -rf "${DMG_TEMP}"
mkdir -p "${DMG_TEMP}"

# Copy app to DMG directory
cp -R "${BUILD_DIR}/${APP_NAME}.app" "${DMG_TEMP}/"

# Create Applications symlink
ln -s /Applications "${DMG_TEMP}/Applications"

# Create README
cat > "${DMG_TEMP}/README.txt" << EOF
GitFit.dev - Fitness Break Reminder
Version ${APP_VERSION}

INSTALLATION:
1. Drag GitFit.dev to Applications folder
2. Double-click to launch from Applications
3. Look for the icon in your menu bar (top of screen)

FIRST RUN:
- macOS may warn about unidentified developer
- Right-click the app and select "Open"
- Click "Open" in the dialog
- This only needs to be done once

FEATURES:
- Runs in menu bar
- Customizable break intervals
- Exercise and stretching routines
- Daily progress tracking
- Multi-language support (EN/SK)

SUPPORT:
https://github.com/JozefJarosciak/GitFitBreaks

© 2024 GitFit
EOF

# Create DMG
hdiutil create -volname "${APP_NAME}" \
    -srcfolder "${DMG_TEMP}" \
    -ov \
    -format UDZO \
    "${BUILD_DIR}/${DMG_NAME}.dmg"

# Clean up
rm -rf "${DMG_TEMP}"

echo -e "${GREEN}✓ DMG installer created${NC}"

# Calculate sizes
APP_SIZE=$(du -sh "${BUILD_DIR}/${APP_NAME}.app" | cut -f1)
DMG_SIZE=$(du -sh "${BUILD_DIR}/${DMG_NAME}.dmg" | cut -f1)

echo ""
echo "========================================="
echo -e "${GREEN}✅ Build Complete!${NC}"
echo "========================================="
echo "App Bundle: ${BUILD_DIR}/${APP_NAME}.app (${APP_SIZE})"
echo "Installer:  ${BUILD_DIR}/${DMG_NAME}.dmg (${DMG_SIZE})"
echo ""
echo "To test locally:"
echo "  open ${BUILD_DIR}/${APP_NAME}.app"
echo ""
echo "To distribute:"
echo "  Share ${BUILD_DIR}/${DMG_NAME}.dmg"
echo ""