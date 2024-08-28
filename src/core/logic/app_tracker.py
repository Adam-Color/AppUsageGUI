import threading
import psutil


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


class AppTracker:
    def __init__(self):
        self.app_names = []
        self.selected_app = None
        self.lock = threading.Lock()
        self.stop_flag = True
        print("init app tracker")

    @threaded
    def update_app_names(self):
        print("update app tracker")
        apps = []
        seen_names = set()
        for process in psutil.process_iter(['name']):
            if self.stop_flag:
                break
            app_name = process.info['name'].split(" ")[0]
            app_name = app_name.split(".")[0]
            # print(app_name) #!
            if app_name not in seen_names:
                apps.append(app_name)
                seen_names.add(app_name)
        with self.lock:
            self.app_names = sorted(apps)
        

    def get_app_names(self):
        return self.app_names

    def get_selected_app(self):
        return self.selected_app
    
    def set_selected_app(self, app):
        self.selected_app = app

    def stop(self):
        self.stop_flag = True

    def start(self):
        self.stop_flag = False
