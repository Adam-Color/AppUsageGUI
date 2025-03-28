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
        self.stop_event = threading.Event()

        # Display the note label
        self.note_label = tk.Label(self, text="Tracking stops automatically when tracked app is fully closed")
        self.note_label.pack(pady=5)

        # Display the page label
        self.page_label = tk.Label(self, text="Tracking the selected app:")
        self.page_label.pack(pady=5)

        # Display the time label
        self.time_label = tk.Label(self, text=self.track_time_disp)
        self.time_label.pack(pady=10)

        # TODO: pause and resume buttons need to be beutified

        pause_button = tk.Button(self, text="Pause", command=self.logic_controller.time_tracker.pause)
        pause_button.pack(pady=5)
        resume_button = tk.Button(self, text="Resume", command=self.logic_controller.time_tracker.resume)
        resume_button.pack(pady=5)

        self.update_queue = queue.Queue()

        self.update_thread = threading.Thread(target=self.update_time_label)
        self.update_thread.daemon = True

        self.periodic_update()

    def update_time_label(self):
        secs = 0
        while not self.stop_event.is_set():
            self.app = self.logic_controller.app_tracker.get_selected_app()

            app_names = self.logic_controller.app_tracker.get_app_names()

            # start the tracking
            if self.app and not self.logic_controller.time_tracker.is_running():
                self.logic_controller.time_tracker.start()
                self.logic_controller.time_tracker.clock()
                self.update_queue.put(("app", self.app))

                # user trackers, enable/disable handled by the user tracker class
                #TODO: needs to be more scalable
                self.logic_controller.mouse_tracker.start()
            elif self.logic_controller.file_handler.get_continuing_tracker():
                self.logic_controller.mouse_tracker.start()

            # Stop tracking when the app closes
            # includes exception for continuing tracking from a previous session.
            if self.logic_controller.time_tracker.is_running() and self.app not in app_names and self.logic_controller.file_handler.get_continuing_tracker() is False:
                # handle situations where the time tracker is paused
                self.logic_controller.time_tracker.resume()

                self.logic_controller.time_tracker.stop()
                self.logic_controller.mouse_tracker.stop()
                self.rec_time = 0
                self.app = ""
                self.track_time_disp = "Looking for target app..."
                break

            # Update the time label
            if self.logic_controller.time_tracker.is_running():
                secs = self.logic_controller.time_tracker.get_time()
                if secs is not None:
                    track_time_disp = f"{format_time(round(secs))} recorded."
                    
                    # update the app label if tracking is paused
                    #TODO: needs a more scalable implementation
                    if self.logic_controller.mouse_tracker.is_pausing():
                        self.page_label.config(text="Tracking paused, mouse is idle...")
                    else:
                        self.page_label.config(text=f"Tracking the selected app: {self.app}")

                    #HACK: needed to allow app to be detected before break
                    self.logic_controller.file_handler.set_continuing_tracker(False)
                else:
                    track_time_disp = "No time data available"
                self.update_queue.put(("time", track_time_disp))
            else:
                self.update_queue.put(("time", "Looking for application..."))

            time.sleep(0.1)
        if not self.stop_event.is_set():
            self.controller.show_frame("SaveWindow")


    def periodic_update(self):
        """Update the GUI clock"""
        try:
            while True:
                item = self.update_queue.get_nowait()
                if item[0] == "time":
                    self.time_label.config(text=f"{item[1]}")
                elif item[0] == "app":
                    self.page_label.config(text=f"Tracking: {item[1]}")
        except queue.Empty:
            pass
        self.after(500, self.periodic_update)
    
    def start_update_thread(self):
        self.update_thread.start()

    def stop_threads(self):
        self.stop_event.set()
