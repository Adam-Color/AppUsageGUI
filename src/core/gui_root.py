import os
import sys
import tkinter as tk
from tkinter import ttk
from core.utils.tk_utils import messagebox
import platform

from _version import __version__ as version
from _path import resource_path
from core.utils.tk_utils import center_relative_to_parent, center

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


class GUIRoot(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        # Initialize LogicRoot
        from .logic_root import LogicRoot
        self.logic = LogicRoot(self)

        # Navigation history
        self.history = []
        self.history_index = -1

        # Create navigation bar
        self.nav_frame = tk.Frame(self)
        self.nav_frame.pack(side="top", fill="x")

        # Options list
        self.options = [
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

        center(self.parent, -13, -15)

        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_options(self):
        """Configure Options (About, License, etc.). Uses a Tk Menu for cross-platform behaviour.
           On macOS we also register the platform hooks so items appear in the native App menu."""
        
        if self.parent.tk.call("tk", "windowingsystem") == "aqua":
            self.parent.createcommand("tk::mac::ShowAbout", self.show_about)
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
                self.parent.createcommand("tk::mac::ShowAbout", self.show_about)
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
            f"AppUsageGUI v{version}\n\nOpen Source Application Tracker\n\n(c) 2025 Adam Blair-Smith\n\nContributors (github):\n\n- Adam-Color\n- Grippando\n\nPython Version:\n\n{sys.version}",
        )

    def show_license(self, _=None):
        """Open license file in a scrollable popup window (reusable)."""
        license_paths_to_try = [
            "_internal/LICENSE.txt",
            "LICENSE.txt",
            os.path.join(os.path.dirname(__file__), "_internal", "LICENSE.txt"),
            resource_path("LICENSE.txt")
        ]

        text = None
        for p in license_paths_to_try:
            try:
                if os.path.exists(p):
                    with open(p, "r", encoding="utf-8") as f:
                        text = f.read()
                        break
            except Exception:
                # ignore and try next
                pass

        if text is None:
            error_txt = "License file not found.\n\nPaths tried:\n" + "\n".join(license_paths_to_try)
            print(error_txt)
            messagebox.showerror("License", error_txt)
            return

        # Reusable Toplevel license window
        win = tk.Toplevel(self.parent)
        win.title("License")
        win.geometry("600x600")
        win.transient(self.parent)
        win.resizable(True, True)
        center_relative_to_parent(win, self.parent)

        # Use a frame for padding and layout
        frame = ttk.Frame(win, padding=(8, 8, 8, 8))
        frame.pack(fill="both", expand=True)

        # Text widget + scrollbar
        text_box = tk.Text(frame, wrap="word", borderwidth=0)
        text_box.insert("1.0", text)
        text_box.config(state="disabled")  # read-only
        text_box.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_box.yview)
        scrollbar.pack(side="right", fill="y")
        text_box.config(yscrollcommand=scrollbar.set)

        # Close button
        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill="x", pady=(6, 8))
        close_btn = ttk.Button(btn_frame, text="Close", command=win.destroy)
        close_btn.pack(side="right", padx=(0, 8))

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

            self.frames = {}

            # Reinitialize screens
            self.init_screens()
            
            # Restore selected project after reset
            self.selected_project = preserved_project

        except Exception:
            from traceback import format_exc
            error = "Crash in reset_frames():\n\n" + format_exc()
            messagebox.showerror("Error", error)
            print(error)

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
