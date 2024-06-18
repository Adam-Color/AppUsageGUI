import psutil
import threading

def get_running_apps():
    apps = []
    for process in psutil.process_iter():
        apps.append(process)
        