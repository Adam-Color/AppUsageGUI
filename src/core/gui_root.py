import os
import sys
import tkinter as tk
from tkinter import ttk
from core.utils.tk_utils import messagebox
import platform

from _version import __version__ as version
from _path import resource_path
from _logging import get_current_log_file
from core.utils.tk_utils import center_relative_to_parent
from core.utils.app_utils import new_updates, update

from .screens.main_window import MainWindow
from .screens.select_app_window import SelectAppWindow
from .screens.sessions_window import SessionsWindow
from .screens.project_sessions_window import ProjectSessionsWindow
from .screens.projects_window import ProjectsWindow
from .screens.create_project_window import CreateProjectWindow
from .screens.tracker_window import TrackerWindow
from .screens.save_window import SaveWindow
from .screens.create_session_window import CreateSessionWindow
from .screens.session_total_window import SessionTotalWindow
from .screens.tracker_settings_window import TrackerSettingsWindow

import logging
logger = logging.getLogger(__name__)


class GUIRoot(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Initialize LogicRoot
        from .logic_root import LogicRoot
        self.logic = LogicRoot(self)

        self.log_file_path = get_current_log_file()

        # Navigation history
        self.history = []
        self.history_index = -1

        # Create navigation bar
        self.nav_frame = tk.Frame(self)
        self.nav_frame.pack(side="top", fill="x")

        # Options list
        self.options = [
            {"label": "Update Check", "callback": self.update_and_check},
            {"label": "Logs", "callback": self.show_logs},
            {"label": "License", "callback": self.show_license},
            {"label": "About", "callback": self.show_about},
        ]

        # Add options depending on OS
        self.setup_options()

        # Create container for screens
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.forward_button = tk.Button(self.nav_frame, text="→", command=self.go_forward, state="disabled")
        self.forward_button.pack(side="right")

        self.back_button = tk.Button(self.nav_frame, text="←", command=self.go_back, state="disabled")
        self.back_button.pack(side="right")

        self.frames = {}
        self.selected_project = None
        self.init_screens()
        self.show_frame("MainWindow")
        
        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_options(self):
        """Configure Options (About, License, etc.). Uses a Tk Menu for cross-platform behaviour.
           On macOS we also register the platform hooks so items appear in the native App menu."""
        
        if self.parent.tk.call("tk", "windowingsystem") == "aqua":
            self.parent.createcommand("tk::mac::standardAboutPanel", self.show_about)
            self.parent.createcommand("tk::mac::ShowPreferences", self.show_license)
            self.parent.createcommand("tk::mac::Quit", self.on_close)
            menubar = tk.Menu(self.parent)
            app_menu = tk.Menu(menubar, tearoff=0)

            # Add commands to the app menu from the single source of truth (self.options)
            for opt in self.options:
                # use lambda with default arg to avoid late-binding loop closure
                app_menu.add_command(label=opt["label"], command=opt["callback"])

            menubar.add_cascade(label="?", menu=app_menu)
            self.parent.config(menu=menubar)

        def fallback_buttons():
            """Create fallback buttons in the nav bar for non-macOS platforms."""
            for opt in self.options:
                btn = tk.Button(self.nav_frame, text=opt["label"], command=opt["callback"])
                btn.pack(side="left", pady=1)

        # macOS: register the conventional app hooks so About/Preferences show in the native Apple menu
        if platform.system() == "Darwin":
            try:
                # Map standard mac menu actions to our callbacks
                # "tk::mac::ShowAbout" -> About
                # "tk::mac::ShowPreferences" -> Preferences (we map to License here)
                self.parent.createcommand("tk::mac::standardAboutPanel", self.show_about)
                self.parent.createcommand("tk::mac::ShowPreferences", self.show_license)
            except Exception:
                # If anything goes wrong, fall back to having the menu (it's already set above)
                fallback_buttons()
                pass
        else:
            # Non-macOS: add buttons to nav bar
            fallback_buttons()


    def show_about(self, _=None):
        """Show app info popup"""
        messagebox.showinfo(
            "About",
            f"AppUsageGUI v{version}\n\nOpen Source Application Tracker\n\n(c) 2026 Adam Blair-Smith\n\nPython Version:\n\n{sys.version}",
        )

    def show_license(self, _=None):
        """Open license file in a scrollable popup window (resizable, with fixed footer)."""
        # Prevent duplicate windows
        if hasattr(self, "license_window") and self.license_window and self.license_window.winfo_exists():
            self.license_window.lift()
            self.license_window.focus_force()
            return

        license_paths_to_try = [
            "_internal/LICENSE.txt",
            "LICENSE.txt",
            os.path.join(os.path.dirname(__file__), "_internal", "LICENSE.txt"),
            resource_path("LICENSE.txt"),
        ]

        text = None
        for p in license_paths_to_try:
            try:
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f:
                        text = f.read()
                        break
            except Exception:
                pass

        if text is None:
            error_txt = "License file not found.\n\nPaths tried:\n" + "\n".join(license_paths_to_try)
            logger.error(error_txt)
            messagebox.showerror("License", error_txt)
            return

        win = tk.Toplevel(self.parent)
        self.license_window = win  # keep reference
        win.title("License")
        win.geometry("600x600")
        win.transient(self.parent)
        win.resizable(True, True)
        center_relative_to_parent(win, self.parent)
        win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), setattr(self, "license_window", None)))

        win.rowconfigure(0, weight=1)
        win.columnconfigure(0, weight=1)

        frame = ttk.Frame(win, padding=(8, 8, 8, 8))
        frame.grid(row=0, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        text_box = tk.Text(frame, wrap="word", borderwidth=0)
        text_box.insert("1.0", text)
        text_box.config(state="disabled")
        text_box.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_box.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        text_box.config(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(win)
        btn_frame.grid(row=1, column=0, sticky="ew", pady=(6, 8))
        btn_frame.columnconfigure(0, weight=1)
        ttk.Button(btn_frame, text="Close", command=win.destroy).grid(row=0, column=0, sticky="e", padx=(0, 8))

    
    def update_and_check(self, _=None):
        if new_updates(manual_check=True):
            update()
        else:
            messagebox.showinfo("Update", "No new updates available.")

    def show_logs(self, _=None):
        """Display logs in a scrollable window with fixed footer buttons."""
        # Prevent duplicate windows
        if hasattr(self, "log_window") and self.log_window and self.log_window.winfo_exists():
            self.log_window.lift()
            self.log_window.focus_force()
            return

        win = tk.Toplevel(self.parent)
        self.log_window = win  # keep reference
        win.title("Application Logs")
        win.geometry("600x600")
        win.transient(self.parent)
        center_relative_to_parent(win, self.parent)

        # Use grid instead of pack for better control
        win.rowconfigure(0, weight=1)
        win.columnconfigure(0, weight=1)

        frame = ttk.Frame(win, padding=(8, 8, 8, 8))
        frame.grid(row=0, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        win.columnconfigure(0, weight=1)

        frame = ttk.Frame(win, padding=(8, 8, 8, 8))
        frame.grid(row=0, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        # Header and text setup
        header = (
            f"=== {self.parent.title()} ===\n"
            f"Python: {sys.version.split('(')[0]}\n"
            f"Platform: {platform.system()} ({platform.machine()})\n"
            f"{'=' * 21}\n"
            f"NOTE: logs window only refreshes when reopened.\n\n"
        )

        # Read logs from the log file if available
        log_contents = ""
        if hasattr(self, "log_file_path") and os.path.exists(self.log_file_path):
            try:
                with open(self.log_file_path, "r") as log_file:
                    log_contents = log_file.read()
            except Exception as e:
                log_contents = f"(Failed to read log file: {e})\n"

        # Combine header and logs
        initial_text = header + (log_contents or self.log_stream.getvalue() or "(No logs yet)\n")

        text_box = tk.Text(frame, wrap="word")
        text_box.insert("1.0", initial_text)
        text_box.config(state="disabled")
        text_box.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_box.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        text_box.config(yscrollcommand=scrollbar.set)

        # Buttons at bottom (separate frame)
        btn_frame = ttk.Frame(win)
        btn_frame.grid(row=1, column=0, sticky="ew", pady=(6, 8))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        def logs():
            """Read the log file and return its contents."""
            try:
                if os.path.exists(self.log_file_path):
                    with open(self.log_file_path, "r") as log_file:
                        return log_file.read()
                else:
                    return "(Log file not found)"
            except Exception as e:
                return f"(Failed to read log file: {e})"
            
        def copy_logs():
            """Copy the current logs to the clipboard."""
            import pyperclip # type: ignore
            try:
                log_text = header + logs()
                pyperclip.copy(log_text)
                messagebox.showinfo("Copy Logs", "Logs copied to clipboard.")
            except Exception as e:
                messagebox.showerror("Copy Logs", f"Failed to copy logs: {e}")

        ttk.Button(btn_frame, text="Copy Logs", command=copy_logs).grid(row=0, column=0, sticky="w", padx=(8, 0))
        ttk.Button(btn_frame, text="Close", command=win.destroy).grid(row=0, column=1, sticky="e", padx=(0, 8))

        # Live Updating
        def refresh_logs():
            """Refresh the logs displayed in the logs window."""
            try:
                new_text = header + logs()  # Use logs() to get log content
                text_box.config(state="normal")
                text_box.delete(1.0, "end")  # Clear existing content
                text_box.insert("end", new_text)  # Insert new content
                text_box.config(state="disabled")  # Make it read-only
            except Exception as e:
                print(f"Failed to refresh logs: {e}")

        refresh_logs()

    def init_screens(self):
        """Pass the logic_controller when initializing screens"""
        for F in (MainWindow, SessionsWindow, ProjectSessionsWindow, ProjectsWindow, CreateProjectWindow, 
                  SelectAppWindow, TrackerWindow, SaveWindow, CreateSessionWindow, SessionTotalWindow, TrackerSettingsWindow):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self, logic_controller=self.logic)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

        # Check if the page is already the current page
        if self.history and self.history[self.history_index] == page_name:
            return  # Do nothing if the page is already the current page

        # If navigating to a new screen, clear forward history
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]

        # Add the new screen to history
        self.history.append(page_name)
        self.history_index += 1

        # Update navigation buttons
        self.update_nav_buttons()

        # Special handling for ProjectSessionsWindow - load sessions when shown
        if page_name == "ProjectSessionsWindow":
            frame.load_sessions()
        # Special handling for CreateSessionWindow - check for pre-selected project
        elif page_name == "CreateSessionWindow":
            frame.check_pre_selected_project()

        # Ensure navigation buttons are updated after any special handling
        self.update_nav_buttons()

        if page_name in ["TrackerWindow", "SessionTotalWindow", "SaveWindow"]:
            self.disable_nav_buttons()
    
    def go_back(self):
        """Navigate to the previous screen."""
        if (self.history_index > 0
            and self.history[self.history_index - 1] not in ["TrackerWindow", "SessionTotalWindow", "SaveWindow"]):
            self.history_index -= 1
            self.reset_frames()
            self.show_frame(self.history[self.history_index])
            self.update_nav_buttons()

    def go_forward(self):
        """Navigate to the next screen."""
        if (self.history_index < len(self.history) - 1
            and self.history[self.history_index + 1] not in ["TrackerWindow", "SessionTotalWindow", "SaveWindow"]):
            self.history_index += 1
            self.reset_frames()
            self.show_frame(self.history[self.history_index])
            self.update_nav_buttons()

    def update_nav_buttons(self):
        """Enable or disable navigation buttons based on history."""
        self.back_button.config(state="normal" if self.history_index > 0 else "disabled")
        self.forward_button.config(state="normal" if self.history_index < len(self.history) - 1 else "disabled")

    def disable_nav_buttons(self):
        """Disable both navigation buttons."""
        self.back_button.config(state="disabled")
        self.forward_button.config(state="disabled")

    def reset_frames(self):
        try:
            # Preserve selected project before reset
            preserved_project = self.selected_project
            
            # Stop trackers
            if self.logic.app_tracker:
                self.logic.app_tracker.reset()

            if self.logic.time_tracker:
                self.logic.time_tracker.reset()

            if self.logic.mouse_tracker:
                self.logic.mouse_tracker.stop()

            # Stop GUI threads
            self.frames["TrackerWindow"].stop_threads()
            self.frames["SessionTotalWindow"].stop_threads(wait=False)

            # Destroy frames
            for frame_name, frame in self.frames.items():
                frame.destroy()

            self.logic.file_handler.set_continuing_session(False)

            self.frames = {}

            # Reinitialize screens
            self.init_screens()
            
            # Restore selected project after reset
            self.selected_project = preserved_project
            logger.info("Frames reset...")

        except Exception:
            from traceback import format_exc
            error = "Crash in reset_frames():\n\n" + format_exc()
            messagebox.showerror("Error", error)
            logger.error(error)

    def on_close(self):
        """Handle cleanup and close the application."""

        # Stop GUI threads
        self.frames["TrackerWindow"].stop_threads()
        self.frames["SessionTotalWindow"].stop_threads(wait=False)
        
        # Stop the AppTracker thread
        if self.logic.app_tracker:
            self.logic.app_tracker.stop()

        # stop the TimeTracker thread
        if self.logic.time_tracker:
            self.logic.time_tracker.stop()
        
        # stop the MouseTracker thread
        if self.logic.mouse_tracker:
            self.logic.mouse_tracker.stop()

        # Destroy the root window
        self.parent.destroy()
