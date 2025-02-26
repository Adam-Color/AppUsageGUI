from .logic.app_tracker import AppTracker
from .logic.time_tracker import TimeTracker
from .logic.file_handler import FileHandler
from.logic.user_trackers import InputTracker

class LogicRoot():
    def __init__(self, parent):
        self.parent = parent

        self.file_handler = FileHandler(self.parent, self)
        self.time_tracker = TimeTracker(self.parent, self)
        self.app_tracker = AppTracker(self.parent, self)
        self.input_tracker = InputTracker(self.parent, self)
