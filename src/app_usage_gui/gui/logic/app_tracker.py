import psutil

class AppTracker():
    def __init__(self):
        print("AppTracker thread initialized.")
    
    def get_app_names(self):
        apps = []
        for process in psutil.process_iter(['name']):
            #TODO: Exclude subprocess by looking for duplicate names
            apps.append(process.info['name'])
        return sorted(apps)
