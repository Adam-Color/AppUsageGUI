import tkinter as tk

from gui.logic.app_tracker import AppTracker

class TrackerWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, controller)
        self.controller = controller
        self.track_time = "Looking for app..."