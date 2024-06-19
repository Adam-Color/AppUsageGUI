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
    def __init__(self):
        print("TimeTracker initialized")
        self.track = False
        self.time = None

    
    @threaded
    def clock(self):
        while self.track:
            time.sleep(0.1)
            self.time = time.time()
    
    def get_time(self):
        return self.time
