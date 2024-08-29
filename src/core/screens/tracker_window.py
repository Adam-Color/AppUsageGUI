import tkinter as tk
import threading
import queue
import time

from core.utils.time_utils import format_time

class TrackerWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic_controller = logic_controller
        self.app = ""
        self.track_time_disp = "Looking for app..."
        self.rec_time = 0

        # Display the page label
        self.page_label = tk.Label(self, text="Tracking the selected app:")
        self.page_label.pack(pady=5)

        self.time_label = tk.Label(self, text=self.track_time_disp)
        self.time_label.pack(pady=10)

        self.update_queue = queue.Queue()

        self.update_thread = threading.Thread(target=self.update_time_label)
        self.update_thread.daemon = True
        self.update_thread.start()

        self.periodic_update()

    def update_time_label(self):
        secs = 0
        while True:
            self.app = self.logic_controller.tracker.get_selected_app()

            # Update the app list periodically to ensure it's up to date
            self.logic_controller.tracker.update_app_names()
            app_names = self.logic_controller.tracker.get_app_names()

            if self.app and not self.logic_controller.time_tracker.is_running():
                self.logic_controller.time_tracker.start()
                self.logic_controller.time_tracker.clock()
                self.update_queue.put(("app", self.app))

            # Stop tracking when the app closes
            if self.logic_controller.time_tracker.is_running() and self.app not in app_names:
                self.logic_controller.time_tracker.stop()
                self.rec_time = secs
                break

            if self.logic_controller.time_tracker.is_running():
                secs = self.logic_controller.time_tracker.get_time()
                if secs is not None:
                    track_time_disp = f"{format_time(round(secs))} recorded."
                else:
                    track_time_disp = "No time data available"
                self.update_queue.put(("time", track_time_disp))
            else:
                self.update_queue.put(("time", "Looking for application..."))

            time.sleep(1)
        self.controller.show_frame("SaveWindow")

    def periodic_update(self):
        try:
            while True:
                item = self.update_queue.get_nowait()
                if item[0] == "time":
                    self.time_label.config(text=f"{item[1]}")
                elif item[0] == "app":
                    self.page_label.config(text=f"Tracking: {item[1]}")
        except queue.Empty:
            pass
        self.after(100, self.periodic_update)

    def get_rec_time(self):
        return self.rec_time
