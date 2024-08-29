import psutil
import threading

class AppTracker:
    def __init__(self, parent, logic_controller):
        self.app_names = []
        self.selected_app = None
        self.update_thread = None
        self.stop_event = threading.Event()  # Used to stop the thread gracefully
        self._start_tracking()  # Start the tracking thread

    def _start_tracking(self):
        if self.update_thread is None:
            self.update_thread = threading.Thread(target=self.update_app_names)
            self.update_thread.start()

    def _fetch_app_names(self):
        apps = []
        seen_names = set()
        for process in psutil.process_iter(['name']):
            app_name = process.info['name'].split(" ")[0]
            app_name = app_name.split(".")[0]  # Use the base name of the process
            print(app_name) #!
            if app_name not in seen_names:
                apps.append(app_name)
                seen_names.add(app_name)
        return sorted(apps)

    def update_app_names(self):
        """Updates the app_names list once."""
        if not self.stop_event.is_set():
            self.app_names = self._fetch_app_names()

    def get_app_names(self):
        return self.app_names

    def get_selected_app(self):
        return self.selected_app
    
    def set_selected_app(self, app):
        self.selected_app = app

    def stop(self):
        """Call this method to stop the tracking thread."""
        if self.update_thread is not None:
            self.stop_event.set()
            self.update_thread.join()
