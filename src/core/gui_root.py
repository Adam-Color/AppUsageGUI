import tkinter as tk
from traceback import format_exc
from core.utils.tk_utils import messagebox

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

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.selected_project = None  # Store the selected project for navigation
        self.init_screens()

        # Bind the close event to ensure cleanup
        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)

    def init_screens(self):
        """Pass the logic_controller when initializing screens"""
        for F in (MainWindow, SessionsWindow, ProjectSessionsWindow, ProjectsWindow, CreateProjectWindow, 
                  SelectAppWindow, TrackerWindow, SaveWindow, CreateSessionWindow, SessionTotalWindow, TrackerSettingsWindow):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self, logic_controller=self.logic)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainWindow")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        
        # Special handling for ProjectSessionsWindow - load sessions when shown
        if page_name == "ProjectSessionsWindow":
            frame.load_sessions()
        # Special handling for CreateSessionWindow - check for pre-selected project
        elif page_name == "CreateSessionWindow":
            frame.check_pre_selected_project()
    
    def set_selected_project(self, project_name):
        """Set the selected project for navigation between windows"""
        self.selected_project = project_name
    
    def get_selected_project(self):
        """Get the currently selected project"""
        return self.selected_project

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

        except Exception as e:
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
