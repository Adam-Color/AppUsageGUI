import os
import sys
import tkinter as tk
from tkinter.ttk import *  # noqa: F403
if os.name == "nt":
    import msvcrt
else:
    import fcntl

from core.utils.tk_utils import center, messagebox
from core.utils.file_utils import sessions_exist, user_dir_exists, lock_file
from _path import resource_path

import logging
logger = logging.getLogger(__name__)

def is_running(lock_path=lock_file()):
    """Return True if another instance of this app is already running."""
    global lock_file
    lock_file = open(lock_path, "w")

    try:
        if os.name == "nt":
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return False  # Lock acquired, no other instance
    except (OSError, IOError):
        return True  # Lock failed, already running


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
                logger.error("The application is already running. Exiting.")
                splash_window.destroy()
                sys.exit(0)

            update_progress(50)
            from core.utils.app_utils import new_updates
            if new_updates():
                from core.utils.app_utils import update
                update()
            update_progress(70)
            from core.gui_root import GUIRoot
            update_progress(80)
            win = GUIRoot(root)
            
            update_progress(100)
            root.update()
            root.deiconify()
            splash_window.destroy()
            root.resizable(False, False)
            root.after('idle', lambda: win.pack(side="top", fill="both", expand=True))

        except Exception:
            from traceback import format_exc
            splash_window.destroy()
            error = str(format_exc())
            logger.error(error)
            messagebox.showerror("Startup Error", error)
            sys.exit(1)

    splash_window.after(100, load_app)
