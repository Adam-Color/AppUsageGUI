import os
import sys
import time
import tkinter as tk
from tkinter.ttk import *  # noqa: F403
import platform
if os.name == "nt":
    import msvcrt
else:
    import fcntl

from core.utils.tk_utils import center, messagebox
from core.utils.file_utils import sessions_exist, user_dir_exists, config_file, read_file, write_file, lock_file
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
    import requests
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
        from traceback import format_exc
        print(f"Error checking for updates: Network error - {str(e) + ' - ' + str(format_exc())}")
    except (KeyError, ValueError, IndexError) as e:
        from traceback import format_exc
        print(f"Error checking for updates: Parsing error - {str(e) + ' - ' + str(format_exc())}")
    except Exception:
        from traceback import format_exc
        error = f"An unexpected error occurred while checking for updates:\n{str(format_exc())}"
        messagebox.showerror("Error", error)
        print(error)
    return False

def is_running(lock_path=lock_file()):
    """Return True if another instance of this app is already running."""
    global lock_file
    lock_file = open(lock_path, "w")

    try:
        if os.name == "nt":
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return False  # Lock acquired → no other instance
    except (OSError, IOError):
        return True  # Lock failed → already running


def splash_screen(root):
    """Display a splash screen while the application loads."""
    splash_window = tk.Toplevel(root)
    splash_window.geometry("300x340")
    splash_window.title("AppUsageGUI - Loading...")
    splash_window.overrideredirect(True)
    center(splash_window)
    splash_window.configure(bg="#2E2E2E")

    #HACK for debugging import times (python -X importtime src/main.py | sort):
    #sys.exit(0)

    # Setup layout
    frame = tk.Frame(splash_window, bg="#2E2E2E")
    frame.pack(expand=True, fill="both")

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # App icon
    from PIL import ImageTk, Image
    icon_img_path = "core/resources/icon.png"
    icon_img = Image.open(resource_path(icon_img_path)).resize((256, 256), Image.Resampling.LANCZOS)
    icon_img = ImageTk.PhotoImage(icon_img)
    icon_label = tk.Label(frame, image=icon_img, bg="#2E2E2E")
    icon_label.image = icon_img  # keep reference
    icon_label.grid(row=0, column=0, pady=(10, 0))

    # Progress bar
    # Apply a modern-looking style to the progress bar
    style = Style()  # noqa: F405
    style.theme_use('alt')

    style.configure("custom.Horizontal.TProgressbar",
                troughcolor="#3C3F41",  # Dark trough background
                background="#61AFEF",   # Qt-style blue progress fill
                bordercolor="#3C3F41",  # Match trough to look seamless
                lightcolor="#61AFEF",
                darkcolor="#61AFEF",
                thickness=10)
    
    progress = Progressbar(frame, orient="horizontal", length=200, mode="determinate",  # noqa: F405
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
                messagebox.showerror("Error", "The application is already running.\n\nExiting.")
                splash_window.destroy()
                sys.exit(0)

            update_progress(50)
            if new_updates():
                ask_update = messagebox.askquestion(
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
                    import webbrowser
                    if suffix is None:
                        webbrowser.open_new_tab("https://github.com/adam-color/AppUsageGUI/releases/latest")
                        messagebox.showinfo("Update", "Your platform is currently unsupported.")
                    elif download_url is not None:
                        webbrowser.open_new_tab(download_url)
                        webbrowser.open_new_tab("https://github.com/adam-color/AppUsageGUI/releases/latest")
                        messagebox.showinfo("Update", "Please install the latest version after it downloads,\nautomatic updates are not yet available.\n\nPlease close AppUsageGUI after you download the new installer.")

            update_progress(70)
            from core.gui_root import GUIRoot
            win = GUIRoot(root)

            update_progress(100)
            root.update()
            root.deiconify()
            splash_window.after(300, splash_window.destroy)
            root.after(300, lambda: win.pack(side="top", fill="both", expand=True))

        except Exception:
            from traceback import format_exc
            splash_window.destroy()
            error = str(format_exc())
            print(error)
            messagebox.showerror("Startup Error", error)
            sys.exit(1)

    splash_window.after(100, load_app)
