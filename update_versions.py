#!/usr/bin/env python3
"""
Automatic version updater for GitFit.dev
Updates all version references from version_config.py
"""
import os
import re
import sys
from pathlib import Path

# Import version config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from version_config import VERSION, RELEASE_DATE

def update_file_version(file_path, patterns_replacements):
    """Update version in a file using regex patterns"""
    if not os.path.exists(file_path):
        print(f"Warning: File not found: {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        for pattern, replacement in patterns_replacements:
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated: {file_path}")
            return True
        else:
            print(f"No changes: {file_path}")
            return False

    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def main():
    """Update all version references"""
    print(f"Updating all versions to {VERSION}")
    print("=" * 50)

    base_dir = Path(__file__).parent
    updated_files = []

    # 1. Update gitfitdev/version.py
    version_py = base_dir / "gitfitdev" / "version.py"
    patterns = [
        (r'__version__ = "[^"]*"', f'__version__ = "{VERSION}"'),
        (r'__release_date__ = "[^"]*"', f'__release_date__ = "{RELEASE_DATE}"')
    ]
    if update_file_version(version_py, patterns):
        updated_files.append(str(version_py))

    # 2. Update installer/gitfit_installer.iss
    installer_iss = base_dir / "installer" / "gitfit_installer.iss"
    patterns = [
        (r'#define MyAppVersion "[^"]*"', f'#define MyAppVersion "{VERSION}"')
    ]
    if update_file_version(installer_iss, patterns):
        updated_files.append(str(installer_iss))

    # 3. Update build_installer.bat
    build_bat = base_dir / "build_installer.bat"
    patterns = [
        (r'set VERSION=[^\r\n]*', f'set VERSION={VERSION}')
    ]
    if update_file_version(build_bat, patterns):
        updated_files.append(str(build_bat))

    # 4. Update packaging/build_macos.sh
    macos_sh = base_dir / "packaging" / "build_macos.sh"
    patterns = [
        (r'APP_VERSION="[^"]*"', f'APP_VERSION="{VERSION}"')
    ]
    if update_file_version(macos_sh, patterns):
        updated_files.append(str(macos_sh))

    # 5. Update GitHub Actions workflow
    workflow_yml = base_dir / ".github" / "workflows" / "build-all.yml"
    patterns = [
        (r'GitFitDev-[0-9]+\.[0-9]+\.[0-9]+-Setup\.exe', f'GitFitDev-{VERSION}-Setup.exe'),
        (r'path: dist\\\\GitFitDev-[0-9]+\.[0-9]+\.[0-9]+-Setup\.exe', f'path: dist\\\\GitFitDev-{VERSION}-Setup.exe')
    ]
    if update_file_version(workflow_yml, patterns):
        updated_files.append(str(workflow_yml))

    # 6. Update version_config.py current version (in case someone changed it manually)
    version_config = base_dir / "version_config.py"
    patterns = [
        (r'VERSION = "[^"]*"', f'VERSION = "{VERSION}"'),
        (r'RELEASE_DATE = "[^"]*"', f'RELEASE_DATE = "{RELEASE_DATE}"')
    ]
    if update_file_version(version_config, patterns):
        updated_files.append(str(version_config))

    print("=" * 50)
    print(f"Updated {len(updated_files)} files to version {VERSION}")

    if updated_files:
        print("\nUpdated files:")
        for file in updated_files:
            print(f"  - {file}")
        print(f"\nAll versions synchronized to {VERSION}")
        print("Next: Commit changes and create release")
    else:
        print("All files already at correct version")

    return len(updated_files) > 0

if __name__ == "__main__":
    main()