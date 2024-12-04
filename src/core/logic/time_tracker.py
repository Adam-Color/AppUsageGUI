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

    @threaded
    def clock(self):
        self.start_time = time.time()
        while self.track:
            self.elapsed_time = time.time() - self.start_time
            time.sleep(0.1)

    def start(self):
        self.track = True

    def stop(self):
        self.track = False

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
        self.total_time = add_time
        self.track = False
        self.start_time = None
