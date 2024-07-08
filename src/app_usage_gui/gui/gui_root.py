import tkinter as tk
from .screens.main_window import MainWindow
from .screens.select_app_window import SelectAppWindow
from .screens.sessions_window import SessionsWindow
from .screens.tracker_window import TrackerWindow
from .screens.save_window import SaveWindow
from .logic.app_tracker import AppTracker
from .logic.time_tracker import TimeTracker

class GUIRoot(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.data_directory = "Data/"
        
        # Initialize the AppTracker
        self.tracker = AppTracker()
        self.time_tracker = TimeTracker()

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.init_screens()

    def init_screens(self):
        for F in (MainWindow, SessionsWindow, SelectAppWindow, TrackerWindow, SaveWindow):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainWindow")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def get_data_directory(self):
        return self.data_directory
