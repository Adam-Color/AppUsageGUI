"""
    Application runtime tracker.

    Copyright (C) 2025 Adam Blair-Smith

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import tkinter as tk
import os
import sys
import webbrowser
import socket
import time
import requests
from PIL import ImageTk, Image
from tkinter.ttk import *

from _version import __version__

from core.gui_root import GUIRoot
from core.utils.file_utils import sessions_exist, user_dir_exists, config_file, read_file, write_file
from core.utils.tk_utils import center

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def is_dark_mode():
    """Check if the system is in dark mode"""
    if os.name == 'nt':  # Windows
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize") as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return value == 0
        except Exception:
            return False
    elif sys.platform == 'darwin':  # macOS
        try:
            from AppKit import NSUserDefaults
            defaults = NSUserDefaults.standardUserDefaults()
            return defaults.boolForKey_("AppleInterfaceStyle") == "Dark"
        except ImportError:
            return False
    elif sys.platform.startswith('linux'):  # Linux
        try:
            with open(os.path.expanduser("~/.config/gtk-3.0/settings.ini"), 'r') as f:
                for line in f:
                    if "gtk-theme-name" in line:
                        return "dark" in line.lower()
        except FileNotFoundError:
            return False

def is_running():
    """Check if the application is already running"""
    try:
        # Try to create a socket to check if the port is available
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('localhost', 0))  # Bind to an available port
        sock.close()
        return False  # If we can bind, the app is not running
    except OSError:
        return True  # If we can't bind, the app is likely running

def apply_dark_theme(root):
    dark_bg = "#2E2E2E"  # Dark gray background
    dark_fg = "#FFFFFF"  # White text

    root.tk_setPalette(background=dark_bg, foreground=dark_fg)

def new_updates():
    """Check for new updates on GitHub. Returns a boolean"""
    if os.path.exists(config_file()):
        try:
            last_update_check = read_file(config_file())["last_update_check"]
            settings = read_file(config_file())
        except (KeyError):
         # If the config file doesn't have the key
            last_update_check = time.time()
            settings = read_file(config_file())
            settings.update({"last_update_check": last_update_check})
            write_file(config_file(), settings)
    else:
        os.makedirs(os.path.dirname(config_file()), exist_ok=True)
        last_update_check = time.time()  # if the file doesn't exist
        settings = read_file(config_file())
        settings.update({"last_update_check": last_update_check})
        write_file(config_file(), settings)
    
    if time.time() - last_update_check < 43200:
        return False  # Check for updates only once every 12 hours
    
    settings.update({"last_update_check": time.time()})
    write_file(config_file(), settings)
    try:
        print("Checking for updates...")
        response = requests.get("https://api.github.com/repos/adam-color/AppUsageGUI/releases/latest", timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        data = response.json()
        latest_version = data["tag_name"].lstrip('v').split('.')
        current_version = __version__.split('.')

        # Compare version numbers
        for latest, current in zip(latest_version, current_version):
            if int(latest) > int(current):
                print("New updates available!")
                return True
            elif int(latest) < int(current):
                print("No new updates available.")
                return False

        # If we've gotten here, the versions are equal
        print("No new updates available.")
        return False

    except requests.RequestException as e:
        print(f"Error checking for updates: Network error - {str(e)}")
    except (KeyError, ValueError, IndexError) as e:
        print(f"Error checking for updates: Parsing error - {str(e)}")
    except Exception as e:
        tk.messagebox.showerror("Error", f"An unexpected error occurred while checking for updates: {str(e)}")
    return False

def splash_screen(root):
    """Display a splash screen while the application loads."""
    splash_window = tk.Toplevel(root)
    splash_window.geometry("300x340")
    splash_window.title("AppUsageGUI - Loading...")
    splash_window.overrideredirect(True)
    splash_window.attributes("-topmost", True)
    center(splash_window)
    splash_window.configure(bg="#2E2E2E")

    # Setup layout
    frame = tk.Frame(splash_window, bg="#2E2E2E")
    frame.pack(expand=True, fill="both")

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # App icon
    icon_img_path = "core/resources/icon-resources/icon.png"
    icon_img = Image.open(resource_path(icon_img_path)).resize((256, 256), Image.Resampling.LANCZOS)
    icon_img = ImageTk.PhotoImage(icon_img)
    icon_label = tk.Label(frame, image=icon_img, bg="#2E2E2E")
    icon_label.image = icon_img  # keep reference
    icon_label.grid(row=0, column=0, pady=(10, 0))

    # Progress bar
    progress = Progressbar(frame, orient="horizontal", length=200, mode="determinate", maximum=100)
    progress.grid(row=1, column=0, pady=(10, 0))

    # First run message / loading message
    if not user_dir_exists(p=True):
        first_run_note = tk.Label(frame, text="Note: first-time loading may take longer...",
                                  bg="#2E2E2E", fg="#AAAAAA")
        first_run_note.grid(row=2, column=0, pady=(5, 0))
    else:
        loading_note = tk.Label(frame, text="Loading...", bg="#2E2E2E", fg="#AAAAAA")
        loading_note.grid(row=2, column=0, pady=(5, 0))

    def update_progress(value):
        """Update the progress bar."""
        progress["value"] = value
        splash_window.update_idletasks()

    def load_app():
        try:
            update_progress(10)
            sessions_exist(p=True)

            update_progress(30)
            if is_running():
                print("AppUsageGUI is already running. Exiting the new instance.")
                splash_window.destroy()
                sys.exit(0)

            update_progress(50)
            if new_updates():
                ask_update = tk.messagebox.askquestion(
                    'AppUsageGUI Updates',
                    "A new update is available. Would you like to download it from the GitHub page?"
                )
                if ask_update == "yes":
                    webbrowser.open_new_tab("https://github.com/adam-color/AppUsageGUI/releases/latest")
                    sys.exit(0)

            update_progress(70)
            win = GUIRoot(root)

            update_progress(100)
            splash_window.after(300, splash_window.destroy)
            root.after(300, lambda: win.pack(side="top", fill="both", expand=True))

        except Exception as e:
            splash_window.destroy()
            tk.messagebox.showerror("Startup Error", str(e))
            sys.exit(1)

    splash_window.after(100, load_app)

def main():

    root = tk.Tk()

    if is_dark_mode():
        apply_dark_theme(root)

    icon_name = "core/resources/icon.ico" if os.name == 'nt' else "core/resources/icon.icns"
    icon_path = resource_path(icon_name)

    root.iconbitmap(icon_path)
    root.title(f"AppUsageGUI - v{__version__}")

    splash_screen(root)
    root.mainloop()

if __name__ == "__main__":
    main()
