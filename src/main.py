import tkinter as tk

from src._version import __version__

from core.gui_root import GUIRoot
from core.utils.file_utils import sessions_exist, user_dir_exists

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
    """Apply a dark theme to Tkinter."""
    dark_bg = "#2E2E2E"  # Dark gray background
    dark_fg = "#FFFFFF"  # White text

    root.tk_setPalette(background=dark_bg, foreground=dark_fg)

    style_settings = {
        "TLabel": {"background": dark_bg, "foreground": dark_fg},
        "TButton": {"background": dark_bg, "foreground": dark_fg},
        "TEntry": {"background": "#3A3A3A", "foreground": dark_fg},
    }

    for widget, settings in style_settings.items():
        root.option_add(f"*{widget}*Background", settings["background"])
        root.option_add(f"*{widget}*Foreground", settings["foreground"])

    root.configure(bg=dark_bg)

def main():
    # calls to create the app directories
    sessions_exist()
    user_dir_exists()

    root = tk.Tk()
    root.title(f"App Usage GUI - v{__version__}")

    if is_dark_mode():
        apply_dark_theme(root)

    win = GUIRoot(root)
    win.pack(side="top", fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()
