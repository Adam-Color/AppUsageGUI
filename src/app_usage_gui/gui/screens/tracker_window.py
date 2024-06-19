import tkinter as tk
import threading
import queue
import time

from gui.utils.time_utils import format_time

class TrackerWindow(tk.Frame):
    def __init__(self, parent, controller):
        print("TrackerWindow initialized")
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.app = ""
        self.track_time_disp = "Looking for app..."

        self.time_label = tk.Label(self, text=self.track_time_disp)
        self.time_label.pack(pady=10)

        self.update_queue = queue.Queue()

        self.update_thread = threading.Thread(target=self.update_time_label)
        self.update_thread.daemon = True
        self.update_thread.start()

        self.periodic_update()

    def update_time_label(self):
        while True:
            self.app = self.controller.tracker.get_selected_app()
            print(f"Selected app: {self.app}")  #! Debugging statement
            if self.app:
                self.controller.time_tracker.clock()
                while True:
                    secs = self.controller.time_tracker.get_time()
                    print(f"Elapsed seconds: {secs}")  #! Debugging statement
                    if secs is not None:
                        track_time_disp = format_time(round(secs))
                    else:
                        track_time_disp = "No time data available"
                    self.update_queue.put(track_time_disp)
                    time.sleep(1)  # Use time.sleep instead of threading.Event().wait
            else:
                self.update_queue.put("Looking for application...")
                time.sleep(1)

    def periodic_update(self):
        try:
            while True:
                track_time_disp = self.update_queue.get_nowait()
                self.time_label.config(text=track_time_disp)
        except queue.Empty:
            pass
        self.after(100, self.periodic_update)
