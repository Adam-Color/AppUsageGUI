"""
User customizable trackers for pausing or exiting 
the timer during the session.
"""

import threading
import time
import pyautogui

from core.utils.file_utils import read_file, config_file

class MouseTracker:
    """Tracks mouse movement over a user configurable time frame."""
    def __init__(self, parent, logic_controller):
        self.parent = parent
        try:
            self.idle_time_limit = read_file(config_file())["mouse_idle_time_limit"]
        except FileNotFoundError:
            self.idle_time_limit = 300  # Default value
        x = 0
        y = 0
        self.logic_controller = logic_controller
        self.mouse_position = x, y
        self.last_mouse_position = x , y
        self.stop_event = threading.Event()  # Used to stop the thread gracefully
        try:
            self.enabled = read_file(config_file())["mouse_tracker_enabled"]
        except FileNotFoundError:
            self.enabled = False  # Default value

        self.update_thread = threading.Thread(target=self._update_mouse_position)

    def _update_mouse_position(self):
        while not self.stop_event.is_set():
            self.last_mouse_position = self.mouse_position
            print(self.last_mouse_position) #! debug
            time.sleep(self.idle_time_limit)
            x, y = pyautogui.position()
            self.mouse_position = x, y
            print(self.mouse_position) #! debug
            if self.last_mouse_position == self.mouse_position:
                self.logic_controller.time_tracker.pause()
                print("mouse tracker paused the timer") #! debug
            elif self.logic_controller.time_tracker.get_is_paused():
                self.logic_controller.time_tracker.resume()
                print("mouse tracker resumed the timer") #! debug

    def start(self):
        if self.enabled:
            self.update_thread.start()

    def stop(self):
        if self.update_thread is not None:
            self.stop_event.set()
            self.update_thread.join()
    
    def set_enabled(self, enabled=bool):
        self.enabled = enabled

    def set_idle_time_limit(self, idle_time_limit):
        """Set the idle time limit for comparing mouse positions"""
        self.idle_time_limit = idle_time_limit

    def get_idle_time_limit(self):
        return self.idle_time_limit
    
    def is_enabled(self):
        return self.enabled
