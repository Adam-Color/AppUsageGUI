import os
import sys
import time
import requests
import socket
import tkinter as tk
import webbrowser
from PIL import ImageTk, Image
from tkinter.ttk import *
import traceback

from core.utils.tk_utils import center
from core.gui_root import GUIRoot
from core.utils.file_utils import sessions_exist, user_dir_exists, config_file, read_file, write_file
from _path import resource_path

from _version import __version__

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
        settings = {}
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
        global RELEASE_DATA
        RELEASE_DATA = data  # Store the release data globally
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
        tk.messagebox.showerror("Error", f"An unexpected error occurred while checking for updates: {str(traceback.format_exc())}")
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
    # Apply a modern-looking style to the progress bar
    style = Style()
    style.theme_use('default')

    style.configure("custom.Horizontal.TProgressbar",
                troughcolor="#3C3F41",  # Dark trough background
                background="#61AFEF",   # Qt-style blue progress fill
                bordercolor="#3C3F41",  # Match trough to look seamless
                lightcolor="#61AFEF",
                darkcolor="#61AFEF",
                thickness=10)
    
    progress = Progressbar(frame, orient="horizontal", length=200, mode="determinate", 
                           maximum=100, style="custom.Horizontal.TProgressbar")
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
                    if sys.platform == "win32":
                        suffix = "WINDOWS_setup.exe"
                    elif sys.platform == "darwin":
                        if platform.processor() == "arm":
                            suffix = "macOS_arm64_setup.dmg"
                        else:
                            suffix = None
                    else:
                        suffix = None
                    
                    for asset in RELEASE_DATA['assets']:
                        if asset['name'].endswith(suffix):
                            download_url = asset['browser_download_url']
                            break
                    if suffix is None:
                        webbrowser.open_new_tab("https://github.com/adam-color/AppUsageGUI/releases/latest")
                        tk.showinfo("Update", "Your platform is currently unsupported.")
                    elif download_url is not None:
                        webbrowser.open_new_tab(download_url)
                        tk.showinfo("Update", "Please install the latest version after it downloads,\nautomatic updates are not yet available.\n\nThe application will now close.")
                    sys.exit(0)

            update_progress(70)
            win = GUIRoot(root)

            update_progress(100)
            root.update()
            root.deiconify()
            splash_window.after(300, splash_window.destroy)
            root.after(300, lambda: win.pack(side="top", fill="both", expand=True))

        except Exception:
            splash_window.destroy()
            tk.messagebox.showerror("Startup Error", str(traceback.format_exc()))
            sys.exit(1)

    splash_window.after(100, load_app)
