import threading
import os
import psutil
if os.name == 'nt':
    import win32gui
    import win32process

EXCLUDED_APPS = {"AppUsageGUI"}

class AppTracker:
    def __init__(self, parent, logic_controller):
        self.app_names = []
        self.selected_app = None
        self.update_thread = None
        self.stop_event = threading.Event()  # Used to stop the thread gracefully
        self.cached_process_count = 0  # Tracks the last known process count
        self._start_tracking()  # Start the tracking thread

        # exclude apps that are not relevant to the user
        self._update_excluded_apps()

    def _start_tracking(self):
        if self.update_thread is None:
            self.update_thread = threading.Thread(target=self._monitor_processes, name="app_tracker")
            self.update_thread.start()

    def _fetch_app_names(self):
        apps = []
        seen_names = set()

        # add excluded apps to seen_names
        seen_names.update(EXCLUDED_APPS)

        for process in psutil.process_iter(['name']):
            try:
                app_name = process.info['name']
                app_name = app_name.split(".")[0]  # Use the base name of the process
                if app_name not in seen_names and len(app_name) > 0:
                    apps.append(app_name)
                    seen_names.add(app_name)
                    print(app_name) #! use to help optimize
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
            self.stop_event.wait(timeout=1)  # Check periodically to avoid excessive CPU usage

    def get_app_names(self):
        return self.app_names

    def get_selected_app(self):
        return self.selected_app
    
    def set_selected_app(self, app):
        self.selected_app = app

    def stop(self):
        print("Stopping App Tracker")
        self.stop_event.set()
        if self.update_thread is not None:
            try:
                self.update_thread.join()
            except RuntimeError:
                pass

    def start(self):
        print("Starting App Tracker")
        self.stop_event = threading.Event()
        self._start_tracking()

    def reset(self):
        self.selected_app = None
        self.update_thread = None

    def _update_excluded_apps(self):
        for process in psutil.process_iter(['name']):
            try:
                app_name = process.info['name']
                app_name = app_name.split(".")[0]  # Use the base name of the process
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes that terminate mid-iteration or are inaccessible
                pass
            if not self._has_gui(app_name):
                EXCLUDED_APPS.add(app_name)

    def _is_process_running(self, process_name):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == process_name:
                return True
        return False

    def _has_gui(self, process_name):
        if not self._is_process_running(process_name):
            return False
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                for proc in psutil.process_iter(['pid']):
                    if proc.info['pid'] == pid:
                        if proc.info['name'] == process_name:
                            return True
                return False
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return False