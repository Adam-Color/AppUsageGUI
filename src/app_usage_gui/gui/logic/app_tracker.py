import psutil
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

class AppTracker:
    def __init__(self):
        print("AppTracker initialized.")
    
    @threaded
    def get_app_names(self):
        apps = []
        for process in psutil.process_iter(['name']):
            # TODO: Exclude subprocess by looking for duplicate names
            apps.append(process.info['name'])
        return sorted(apps)