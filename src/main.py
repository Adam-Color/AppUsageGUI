import tkinter as tk
import os
import sys

from _version import __version__

from core.gui_root import GUIRoot
from core.utils.file_utils import sessions_exist, user_dir_exists

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def is_dark_mode():
    """Check if Windows is in dark mode."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0  # 0 means dark mode is enabled
    except Exception:
        return False  # Default to light mode if error occurs

def apply_dark_theme(root):
    dark_bg = "#2E2E2E"  # Dark gray background
    dark_fg = "#FFFFFF"  # White text

    root.tk_setPalette(background=dark_bg, foreground=dark_fg)


def main():
    # calls to create the app directories
    root = tk.Tk()

    icon_name = "core/resources/icon.ico" if os.name == 'nt' else "core/resources/icon.icns"
    icon_path = resource_path(icon_name)

    root.iconbitmap(icon_path)
    root.title(f"App Usage GUI - v{__version__}")

    win = GUIRoot(root)
    win.pack(side="top", fill="both", expand=True)

    if is_dark_mode():
        apply_dark_theme(root)

    sessions_exist()
    user_dir_exists()

    root.mainloop()

if __name__ == "__main__":
    main()

