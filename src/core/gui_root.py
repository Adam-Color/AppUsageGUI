import tkinter as tk
from traceback import format_exc
from core.utils.tk_utils import messagebox
import platform

from _version import __version__ as version

from .logic_root import LogicRoot
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
        self.logic = LogicRoot(self)

        # Navigation history
        self.history = []
        self.history_index = -1

        # Create navigation bar
        self.nav_frame = tk.Frame(self)
        self.nav_frame.pack(side="top", fill="x")

        # Add About option depending on OS
        self.setup_about_option()

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

    def setup_about_option(self):
        """Configure About menu/button depending on OS."""
        def show_about(_=None):
            messagebox.showinfo(
                "About",
                f"AppUsageGUI v{version}\nOpen Source Tracker\n(c) 2025 Adam Blair-Smith"
            )

        if platform.system() == "Darwin":
            try:
                import objc
                from AppKit import NSApp, NSMenuItem

                main_menu = NSApp.mainMenu()
                app_menu = main_menu.itemAtIndex_(0).submenu()

                about_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    "About MyApp",
                    objc.selector(show_about, signature=b"v@:@"),
                    ""
                )
                app_menu.insertItem_atIndex_(about_item, 1)
                return
            except ImportError:
                # Fall back if PyObjC not installed
                pass

        # Non-macOS → add About button to nav frame
        about_btn = tk.Button(self.nav_frame, text="About", command=show_about)
        about_btn.pack(side="left", padx=5)

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
            messagebox.showerror("Error", f"Crash in reset_frames(): {str(format_exc())}")

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
