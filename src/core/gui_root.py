import tkinter as tk

from .logic_root import LogicRoot

from .screens.main_window import MainWindow
from .screens.select_app_window import SelectAppWindow
from .screens.sessions_window import SessionsWindow
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
        self.logic_controller = LogicRoot(self)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.init_screens()

        # Bind the close event to ensure cleanup
        self.parent.protocol("WM_DELETE_WINDOW", self.on_close)

    def init_screens(self):
        # Pass the logic_controller when initializing screens
        for F in (MainWindow, SessionsWindow, SelectAppWindow, TrackerWindow, SaveWindow, CreateSessionWindow, SessionTotalWindow, TrackerSettingsWindow):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self, logic_controller=self.logic_controller)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainWindow")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def reset_frames(self):
        # Stop the AppTracker thread
        if self.logic_controller.app_tracker:
            self.logic_controller.app_tracker.reset()

        # stop the TimeTracker thread
        if self.logic_controller.time_tracker:
            self.logic_controller.time_tracker.reset()
        
        # stop the MouseTracker thread
        if self.logic_controller.mouse_tracker:
            self.logic_controller.mouse_tracker.stop()
        
        # Reset the frames and initialize them again
        for frame in self.frames.values():
            frame.destroy()
        self.frames = {}
        self.init_screens()

    def on_close(self):
        """Handle cleanup and close the application."""
        # Stop the AppTracker thread
        if self.logic_controller.app_tracker:
            self.logic_controller.app_tracker.stop()

        # stop the TimeTracker thread
        if self.logic_controller.time_tracker:
            self.logic_controller.time_tracker.stop()
        
        # stop the MouseTracker thread
        if self.logic_controller.mouse_tracker:
            self.logic_controller.mouse_tracker.stop()

        # Destroy the root window
        self.parent.destroy()
