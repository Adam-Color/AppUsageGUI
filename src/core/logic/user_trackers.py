"""
User customizable trackers for pausing or exiting 
the timer during the session.
"""

import threading
import pynput

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
        self.logic = logic_controller
        self.mouse_position = x, y
        self.last_mouse_position = x, y
        self.stop_event = threading.Event()  # Used to stop the thread gracefully
        try:
            self.enabled = read_file(config_file())["mouse_tracker_enabled"]
        except FileNotFoundError:
            self.enabled = False  # Default value

        self.pausing = False

        self.update_thread = threading.Thread(target=self._update_mouse_position, name="mouse_tracker")

    def _update_mouse_position(self):
        while not self.stop_event.is_set():
            self.last_mouse_position = self.mouse_position

            wait_time = self.idle_time_limit if not self.logic.time_tracker.get_is_paused() else 1

            # Wait for the idle time or exit early if stop_event is set
            if self.stop_event.wait(timeout=wait_time):
                break

            x, y = pynput.mouse.Controller().position
            self.mouse_position = x, y

            # Pause the timer if mouse hasn’t moved
            if self.last_mouse_position == self.mouse_position:
                self.logic.time_tracker.pause()
                self.pausing = True
            elif self.pausing:
                self.logic.time_tracker.resume()
                self.pausing = False


    def start(self):
        if self.enabled:
            self.stop_event = threading.Event()  # Reset the stop event to allow the thread to run again
            self.update_thread = threading.Thread(target=self._update_mouse_position, name="mouse_tracker")
            self.update_thread.start()

    def stop(self):
        self.stop_event.set()
        if self.update_thread is not None:
            try:
                self.update_thread.join()
            except RuntimeError:
                pass
    
    def set_enabled(self, enabled=bool):
        self.enabled = enabled

    def set_idle_time_limit(self, idle_time_limit):
        """Set the idle time limit for comparing mouse positions"""
        self.idle_time_limit = idle_time_limit

    def get_idle_time_limit(self):
        return self.idle_time_limit
    
    def is_pausing(self):
        return self.pausing
    
    def is_enabled(self):
        return self.enabled

class ResolveProjectTracker:
    """Tracks if the user is in a specified DaVinci Resolve project or not"""
    def __init__(self, parent, logic_controller):
        self.parent = parent
        self.logic = logic_controller
        self.paused = False
        self.project_name = None
        self.project_open = False
        self.stop_event = threading.Event()  # Used to stop the thread gracefully
        try:
            self.enabled = read_file(config_file())["resolve_tracker_enabled"]
        except FileNotFoundError or KeyError: #! KeyError for dev
            self.enabled = False  # Default value
        self.update_thread = threading.Thread(target=self._update_project_status)
