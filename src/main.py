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
import requests
import socket

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

def apply_dark_theme(root):
    dark_bg = "#2E2E2E"  # Dark gray background
    dark_fg = "#FFFFFF"  # White text

    root.tk_setPalette(background=dark_bg, foreground=dark_fg)

def new_updates():
    """Check for new updates on GitHub. Returns a boolean"""
    try:
        response = requests.get("https://api.github.com/repos/adam-color/AppUsageGUI/releases/latest", timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        data = response.json()
        latest_version = data["tag_name"].lstrip('v').split('.')
        current_version = __version__.split('.')

        # Compare version numbers
        for latest, current in zip(latest_version, current_version):
            if int(latest) > int(current):
                return True
            elif int(latest) < int(current):
                return False

        # If we've gotten here, the versions are equal
        return False

    except requests.RequestException as e:
        print(f"Error checking for updates: Network error - {str(e)}")
    except (KeyError, ValueError, IndexError) as e:
        print(f"Error checking for updates: Parsing error - {str(e)}")
    except Exception as e:
        print(f"Error checking for updates: Unexpected error - {str(e)}")
    return False

def splash_screen():
    """Display a splash screen while the application loads."""
    splash_window = tk.Tk()
    splash_window.attributes("-topmost", True)
    splash_window.geometry("200x50")
    splash_window.title("AppUsageGUI - Loading...")
    splash_window.update_idletasks()
    splash_window.update()

    # calls to create the app directories
    sessions_exist(p=True)
    user_dir_exists(p=True)
    
    # check if app is already running
    try:
        # create a socket to check if the app is already running
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 0))  # bind to an available port
        sock.listen(1)  # listen for incoming connections
    except socket.error:
        # if there is an error, it means the app is already running
        print("App is already running")
        sys.exit()

    # Check for new updates
    if new_updates():
        ask_update = tk.messagebox.askquestion('AppUsageGUI Updates', "A new update is available. Would you like to download it from the github page?")
        if ask_update == "yes":
            webbrowser.open_new_tab("https://github.com/adam-color/AppUsageGUI/releases/latest")

    # Display loading text
    loading_label = tk.Label(splash_window, text="\nLoading...")
    loading_label.pack()

    splash_window.destroy()

def main():
    splash_screen()
    root = tk.Tk()

    icon_name = "core/resources/icon.ico" if os.name == 'nt' else "core/resources/icon.icns"
    icon_path = resource_path(icon_name)

    root.iconbitmap(icon_path)
    root.title(f"AppUsageGUI - v{__version__}")

    win = GUIRoot(root)
    win.pack(side="top", fill="both", expand=True)

    if os.name == 'nt' and is_dark_mode():
        apply_dark_theme(root)

    root.mainloop()

if __name__ == "__main__":
    main()
