import time

from core.utils.logic_utils import threaded

class TimeTracker:
    def __init__(self, parent, logic_controller):
        self.parent = parent

        # note: logic controller is defined as the only controller
        self.controller = logic_controller

        self.track = False
        self.start_time = None
        self.elapsed_time = 0.0
        self.total_time = 0.0
        self.paused_time = 0.0
        self.resumed_time = 0.0
        self.offset_time = 0.0
        self.is_paused = False

    @threaded
    def clock(self):
        """This method runs in a separate 
        thread and updates the elapsed time."""
        self.start_time = time.time()
        while self.track:
            # time does not elapse when paused
            if not self.is_paused:
                self.elapsed_time = time.time() - self.start_time - self.offset_time
            # sleep needs to be kept low here for accuracy
            time.sleep(0.1)

    def start(self):
        self.track = True

    def stop(self):
        self.track = False

    def pause(self):
        if self.track and not self.is_paused:
            self.is_paused = True
            self.paused_time = time.time()

    def resume(self):
        """Resumes the tracker, subtracts the time paused."""
        if self.track and self.is_paused:
            self.is_paused = False
            self.resumed_time = time.time()
            self.offset_time += self.resumed_time - self.paused_time

    def get_is_paused(self):
        return self.is_paused

    def get_time(self, saved=False):
        if not self.track and saved is False:
            return None
        return self.elapsed_time

    def get_total_time(self):
        return self.total_time + self.elapsed_time

    def is_running(self):
        return self.track

    def reset(self, add_time=0.0):
        self.elapsed_time = 0.0
        self.offset_time = 0.0
        self.paused_time = 0.0
        self.resumed_time = 0.0
        self.total_time = add_time
        self.track = False
        self.start_time = None
