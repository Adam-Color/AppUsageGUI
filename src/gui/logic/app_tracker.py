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
        self.app_names = []
        self.selected_app = None
    
    
    @threaded
    def update_app_names(self):
        apps = []
        seen_names = set()
        for process in psutil.process_iter(['name']):
            app_name = process.info['name'].split(" ")[0]
            app_name = app_name.split(".")[0]  # Use the base name of the process
            if app_name not in seen_names:
                apps.append(app_name)
                seen_names.add(app_name)
            # else:
                # print(f"rejected: {process.info['name']}")
        self.app_names = sorted(apps)
    

    def get_app_names(self):
        return self.app_names

    def get_selected_app(self):
        return self.selected_app
    
    def set_selected_app(self, app):
        self.selected_app = app