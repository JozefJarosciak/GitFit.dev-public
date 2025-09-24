#!/usr/bin/env python3
"""
Entry point for PyInstaller build with error handling
"""
import sys
import os
import platform
import traceback

# Add parent directory to path for imports
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in normal Python
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, base_path)

def run_with_error_handling():
    """Run the app with error handling and logging"""
    try:
        # macOS specific fixes
        if platform.system() == 'Darwin':
            # Ensure we can access the display
            if 'DISPLAY' not in os.environ:
                os.environ['DISPLAY'] = ':0'

        from gitfitdev.app import main
        main()
    except Exception as e:
        # Log error to file for debugging
        error_log = os.path.expanduser('~/.gitfitdev/crash.log')
        os.makedirs(os.path.dirname(error_log), exist_ok=True)

        with open(error_log, 'w') as f:
            f.write(f"GitFit.dev Crash Report\n")
            f.write(f"Platform: {platform.system()} {platform.release()}\n")
            f.write(f"Python: {sys.version}\n")
            f.write(f"Executable: {sys.executable}\n")
            f.write(f"Error: {str(e)}\n\n")
            f.write(f"Traceback:\n")
            f.write(traceback.format_exc())

        # On macOS, also try to show a dialog
        if platform.system() == 'Darwin':
            try:
                os.system(f'osascript -e \'display dialog "GitFit.dev crashed. Check ~/.gitfitdev/crash.log for details." buttons {{"OK"}} default button 1\'')
            except:
                pass

        # Re-raise the exception
        raise

if __name__ == "__main__":
    run_with_error_handling()

