import threading
import os
import psutil
import sys

if os.name == 'nt':
    from pywinauto import Desktop
    from pywinauto.findwindows import ElementNotFoundError
    windows = Desktop(backend="uia").windows()
elif sys.platform == 'darwin':
    from AppKit import NSWorkspace

from core.utils.file_utils import read_file, write_file, apps_file, user_dir_exists, config_file

EXCLUDED_APP_PIDS = []
INCLUDED_APP_PIDS = []

if user_dir_exists() and os.path.exists(apps_file()):
    EXCLUDED_APP_PIDS = read_file(apps_file())['excluded_app_pids']
    INCLUDED_APP_PIDS = read_file(apps_file())['included_app_pids']

class AppTracker:
    def __init__(self, parent, logic_controller):
        self.app_names = []
        self.selected_app = None
        self.update_thread = None
        self.stop_event = threading.Event()  # Used to stop the thread gracefully
        self.cached_process_count = 0  # Tracks the last known process count
        try:
            self.is_filter_enabled = read_file(config_file())['is_filter_enabled']
        except (KeyError, FileNotFoundError):
            self.is_filter_enabled = True

        # exclude apps that are not relevant to the user
        self._update_excluded_apps()

        self._start_tracking()  # Start the tracking thread

    def _start_tracking(self):
        if self.update_thread is None:
            self.update_thread = threading.Thread(target=self._monitor_processes, name="app_tracker")
            self.update_thread.start()

    def _fetch_app_names(self):
        apps = []
        seen_names = ["AppUsageGUI", "Python"]

        for process in psutil.process_iter(['pid', 'name']):
            try:
                pid = process.info['pid']
                app_name = process.info['name']
                app_name = app_name.split(".")[0]  # Use the base name of the process
                if (
                    app_name not in seen_names
                    and pid not in EXCLUDED_APP_PIDS
                    and len(app_name) > 0
                ):
                    apps.append(app_name)
                    seen_names.append(app_name)
                    if app_name == self.selected_app:
                        #print(f"Selected app found: {app_name}")  # Debugging line
                        break
                    #print(app_name)  # Debugging line to help optimize
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
        self.stop_event.set()
        if self.update_thread is not None:
            try:
                self.update_thread.join()
            except RuntimeError:
                pass

    def start(self):
        self.stop_event = threading.Event()
        self._start_tracking()

    def reset(self):
        self.selected_app = None
        self.update_thread = None
    
    def set_filter_enabled(self, enabled=True):
        self.is_filter_enabled = enabled 
    
    def start_filter_reset(self, refresh=False, update_pids=False):
        if os.name == 'nt':
            self.temp_reset_thread = threading.Thread(target=self._reset_excluded_pids(refresh, update_pids), name="reset_filter")
            self.temp_reset_thread.start()

    def _reset_excluded_pids(self, refresh, update_pids):
        global EXCLUDED_APP_PIDS
        global INCLUDED_APP_PIDS
        EXCLUDED_APP_PIDS = []
        INCLUDED_APP_PIDS = []
        if refresh:
            self.app_names = self._fetch_app_names()
        if update_pids:
            self._update_excluded_apps()

    def _update_excluded_apps(self):
        seen_pids = []
        i = 0
        for process in psutil.process_iter(['pid', 'status']):
            try:
                pid = process.info['pid']
                if pid in seen_pids:
                    continue
                #print(f"Checking process: (PID: {pid})")  # Debugging line
                seen_pids.append(pid)
                if process.info['status'] == psutil.STATUS_RUNNING and pid not in INCLUDED_APP_PIDS and pid not in EXCLUDED_APP_PIDS:
                    if self._has_gui(pid):
                        INCLUDED_APP_PIDS.append(pid)
                    else:
                        i += 1
                        EXCLUDED_APP_PIDS.append(pid)
                if len(seen_pids) > (400 if os.name == 'nt' else 10000):
                    # Limit the number of seen processes to avoid long loading times
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes that terminate mid-iteration or are inaccessible
                pass

        #print(f"\nExcluded app PIDs: {EXCLUDED_APP_PIDS}")  # Debugging line
        print(f"New exlusions: {i}")
        data = {'excluded_app_pids': EXCLUDED_APP_PIDS,
                'included_app_pids': INCLUDED_APP_PIDS}
        write_file(apps_file(), data)

    def _has_gui(self, process_id):
        if os.name == 'nt':
            try:
                # Enumerate all top-level windows
                for win in windows:
                    if win.process_id() == process_id:
                        # Found a visible window for this process
                        return True
            except (ElementNotFoundError, RuntimeError):
                return True  # Handle the case where the process is not found
            return False
        elif sys.platform == 'darwin':
            #TODO: Implement a better GUI check for macOS
            try:
                apps = NSWorkspace.sharedWorkspace().runningApplications()
                for app in apps:
                    if app.processIdentifier() == process_id:
                        return True
                if app.processIdentifier() == None:
                    # Handle the case where the process is not found
                    return True
                return False
            except Exception as e:
                print(f"GUI check error: {e}")
                return True
