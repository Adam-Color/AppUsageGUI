import threading
import psutil

class AppTracker():
    def __init__(self):
        self.thread = threading.Thread(target=self)
        print("AppTracker thread initialized.")
    
    def get_app_names(self):
        self.thread.start()
        apps = []
        for process in psutil.process_iter(['name']):
            print(f"app added: {process.info['name']}")
            apps.append(process.info['name'])
        self.thread.join()
        return apps
