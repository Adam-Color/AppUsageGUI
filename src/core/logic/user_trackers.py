"""
User customizable trackers for pausing or exiting 
the timer during the session.
"""

import threading

class InputTracker:
    """Tracks input movement over a user configurable time frame."""
    def __init__(self, parent, logic_controller):
        self.parent = parent
        self.idle_time_limit = 30
        self.logic_controller = logic_controller
        self.stop_event = threading.Event()  # Used to stop the thread gracefully

        self.update_thread = threading.Thread(target=self._update_input_detection)

    def _update_input_detection(self):
        while not self.stop_event.is_set():
            return 0

    def start_tracking(self):
        if self.update_thread is None:
            self.update_thread.start()

    def stop(self):
        if self.update_thread is not None:
            self.stop_event.set()
            self.update_thread.join()

    def set_idle_time_limit(self, idle_time_limit):
        """Set the idle time limit for comparing input positions"""
        self.idle_time_limit = idle_time_limit

    def get_idle_time_limit(self):
        return self.idle_time_limit
