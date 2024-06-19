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
        self.start_time = None
        self.elapsed_time = 0

    @threaded
    def clock(self):
        self.track = True
        self.start_time = time.time()
        while self.track:
            self.elapsed_time = time.time() - self.start_time
            time.sleep(1)

    def stop(self):
        self.track = False

    def get_time(self):
        if not self.track:
            return None
        return self.elapsed_time
