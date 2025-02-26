"""
User customizable trackers for pausing or exiting 
the timer during the session.
"""

import threading
import pyautogui
import time

class MouseTracker:
    """Tracks mouse movement over a user configurable time frame."""
    def __init__(self, parent, logic_controller):
        self.parent = parent
        self.idle_time_limit = 300
        x = 0
        y = 0
        self.logic_controller = logic_controller
        self.mouse_position = x, y
        self.last_mouse_position = x , y
        self.stop_event = threading.Event()  # Used to stop the thread gracefully

        self.update_thread = threading.Thread(target=self._update_mouse_position)

    def _update_mouse_position(self):
        while not self.stop_event.is_set():
            self.last_mouse_position = self.mouse_position
            #! debug print
            print("Mouse pos: ", self.last_mouse_position)
            time.sleep(self.idle_time_limit)
            x, y = pyautogui.position()
            self.mouse_position = x, y
            #! debug print
            print("last mouse pos: ", self.mouse_position)

    def start_tracking(self):
        if self.update_thread is None:
            self.update_thread.start()

    def stop(self):
        if self.update_thread is not None:
            self.stop_event.set()
            self.update_thread.join()

    def set_idle_time_limit(self, idle_time_limit):
        """Set the idle time limit for comparing mouse positions"""
        self.idle_time_limit = idle_time_limit

    def get_last_mouse_position(self):
        return self.last_mouse_position

    def get_mouse_position(self):
        return self.mouse_position

    def get_idle_time_limit(self):
        return self.idle_time_limit
