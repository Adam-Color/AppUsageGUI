import time
import threading

def threaded(fn):
    def wrapper(*args, **kwargs):
        result = []
        def run_and_capture():
            result.append(fn(*args, **kwargs))
        thread = threading.Thread(target=run_and_capture)
        thread.start()
        return thread, result
    return wrapper

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

        # {'starts': [], 'stops': [], 'pauses': [{start: 0, how_long: 0}, ...]}
        if self.controller.file_handler.get_continuing_tracker():
            try:
                self.captures = self.controller.file_handler.get_data()['time_captures']
            except KeyError:
                self.captures = {'starts': [], 'stops': [], 'pauses': []}
        else:
            self.captures = {'starts': [], 'stops': [], 'pauses': []}

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
        self.captures['starts'].append(time.time())

    def stop(self):
        self.track = False
        self.captures['stops'].append(time.time())

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
            self.captures['pauses'].append({'start': self.paused_time,
                                            'how_long': self.offset_time})

    def get_is_paused(self):
        return self.is_paused

    def get_time(self, saved=False):
        if not self.track and saved is False:
            return None
        return self.elapsed_time

    def get_total_time(self):
        return self.total_time + self.elapsed_time
    
    def get_paused_time(self):
        return self.paused_time
    
    def get_time_captures(self):
        return self.captures

    def is_running(self):
        return self.track

    def reset(self, add_time=0.0):
        self.elapsed_time = 0.0
        self.total_time = add_time
        self.track = False
        self.start_time = None
