import threading
import time
import os
import psutil

class AppTracker:
    def __init__(self, parent, logic_controller):
        self.app_names = []
        self.selected_app = None
        self.update_thread = None
        self.stop_event = threading.Event()  # Used to stop the thread gracefully
        self.cached_process_count = 0  # Tracks the last known process count
        self._start_tracking()  # Start the tracking thread

    def _start_tracking(self):
        if self.update_thread is None:
            self.update_thread = threading.Thread(target=self._monitor_processes)
            self.update_thread.start()

    def _fetch_app_names(self):
        apps = []
        seen_names = set()
        for process in psutil.process_iter(['name']):
            try:
                app_name = process.info['name'].split(" ")[0]
                app_name = app_name.split(".")[0]  # Use the base name of the process
                if app_name not in seen_names:
                    apps.append(app_name)
                    seen_names.add(app_name)
                    #print(app_name) #! use to help optimize
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes that terminate mid-iteration or are inaccessible
                pass
        if os.name == 'nt':
            return sorted(apps, key=str.casefold)
        return sorted(apps)

    def _monitor_processes(self):
        """keeps track of the number of processes"""
        while not self.stop_event.is_set():
            current_process_count = len(psutil.pids())
            if current_process_count != self.cached_process_count:
                # Process count has changed; update app names
                self.cached_process_count = current_process_count
                self.app_names = self._fetch_app_names()
            time.sleep(1)  # Check periodically to avoid excessive CPU usage

    def get_app_names(self):
        return self.app_names

    def get_selected_app(self):
        return self.selected_app
    
    def set_selected_app(self, app):
        self.selected_app = app

    def stop(self):
        if self.update_thread is not None:
            self.stop_event.set()
            self.update_thread.join()

    def start(self):
        self.stop_event = threading.Event()
        self._start_tracking()

    def reset(self):
        self.selected_app = None
        self.update_thread = None
