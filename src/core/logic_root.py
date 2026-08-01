from .logic.app_tracker import AppTracker
from .logic.time_tracker import TimeTracker
from .logic.file_handler import FileHandler
from .logic.user_trackers import MouseTracker
from .logic.project_handler import ProjectHandler

class LogicRoot():
    def __init__(self, parent):
        self.parent = parent

        self.project_handler = ProjectHandler(self.parent, self)
        self.file_handler = FileHandler(self.parent, self)
        self.time_tracker = TimeTracker(self.parent, self)
        self.app_tracker = AppTracker(self.parent, self)
        self.mouse_tracker = MouseTracker(self.parent, self)
    
    def close(self):
        self.time_tracker.stop()
        self.app_tracker.stop()
        self.mouse_tracker.stop()
