# Try PyQt5 version first, fallback to tkinter if needed
try:
    from .app_pyqt import main
    print("Running PyQt5 version with full video support...")
except ImportError:
    print("PyQt5 not available, using tkinter version...")
    from .app import main

if __name__ == "__main__":
    main()

