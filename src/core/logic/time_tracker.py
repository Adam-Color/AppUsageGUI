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
        self.elapsed_time = 0

    @threaded
    def clock(self):
        self.start_time = time.time()
        while self.track:
            self.elapsed_time = time.time() - self.start_time
            time.sleep(1)

    def start(self):
        self.track = True

    def stop(self):
        self.track = False

    def get_time(self, saved=False):
        if not self.track and saved is False:
            return None
        if self.controller.session_files.get_continuing_session():
            self.elapsed_time += self.controller.session_files.get_data()['time_spent']
        return self.elapsed_time
    
    def is_running(self):
        return self.track
    
    def reset(self):
        self.elapsed_time = 0
        self.track = False
        self.start_time = None
