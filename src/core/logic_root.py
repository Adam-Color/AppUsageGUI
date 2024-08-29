from .logic.app_tracker import AppTracker
from .logic.time_tracker import TimeTracker
from .logic.file_handler import FileHandler

class LogicRoot():
    def __init__(self, parent):
        self.parent = parent

        self.session_files = FileHandler(self.parent, self)
        self.time_tracker = TimeTracker(self.parent, self)
        self.tracker = AppTracker(self.parent, self)
