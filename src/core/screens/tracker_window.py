import tkinter as tk
import threading
import queue
from tkinter import messagebox

from core.utils.time_utils import format_time

class TrackerWindow(tk.Frame):
    TIME_UPDATE = "time"
    APP_UPDATE = "app"

    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic = logic_controller
        self.app = ""
        self.track_time_disp = "Looking for app..."
        self.rec_time = 0
        self.stop_event = threading.Event()
        self.stop_button_pressed = False

        self._setup_widgets()

        self.update_queue = queue.Queue()
        self.update_thread = threading.Thread(target=self._update_time_label, name="update_time_label", daemon=True)

        self._periodic_update()

    def _setup_widgets(self):
        self.note_label = tk.Label(self, text="Tracking stops automatically when tracked app is fully closed")
        self.note_label.pack(pady=5)

        self.page_label = tk.Label(self, text="Tracking the selected app:")
        self.page_label.pack(pady=5)

        self.time_label = tk.Label(self, text=self.track_time_disp)
        self.time_label.pack(pady=10)

        self.pause_toggle_text = tk.StringVar(value="Pause")
        pause_button = tk.Button(self, textvariable=self.pause_toggle_text, command=self.toggle_pause_tracker, width=10)
        pause_button.pack(pady=5)

        self.stop_button = tk.Button(self, text="Stop", command=self._stop, width=10)
        self.stop_button.pack(pady=5)

    def _update_time_label(self):
        while not self.stop_event.is_set():
            self.app = self.logic.app_tracker.get_selected_app()

            app_names = self.logic.app_tracker.get_app_names()

            if self._should_start_tracking():
                self._start_tracking()

            elif self.logic.file_handler.get_continuing_tracker():
                self.logic.mouse_tracker.start()

            if self._should_stop_tracking(app_names):
                self._stop_tracking()
                break

            if self.logic.time_tracker.is_running():
                self._update_display()
            else:
                self.update_queue.put((self.TIME_UPDATE, "Looking for application..."))

            self.stop_event.wait(timeout=0.1)

        if not self.stop_event.is_set():
            self.controller.show_frame("SaveWindow")

    def _should_start_tracking(self):
        return self.app and not self.logic.time_tracker.is_running()

    def _should_stop_tracking(self, app_names):
        return self.stop_button_pressed or (
            self.logic.time_tracker.is_running() and
            self.app not in app_names and
            not self.logic.file_handler.get_continuing_tracker()
        )

    def _start_tracking(self):
        self.logic.time_tracker.start()
        self.logic.time_tracker.clock()
        self.logic.mouse_tracker.start()
        self.update_queue.put((self.APP_UPDATE, self.app))

    def _stop_tracking(self):
        self.logic.time_tracker.resume()
        self.logic.time_tracker.stop()
        self.logic.mouse_tracker.stop()
        self.rec_time = 0
        self.app = ""
        self.track_time_disp = "Looking for target app..."

    def _update_display(self):
        secs = self.logic.time_tracker.get_time()
        if secs is not None:
            time_text = f"{format_time(int(secs))} recorded."
        else:
            time_text = "No time data available"

        if self.logic.mouse_tracker.is_pausing():
            self.page_label.config(text="Tracking paused, mouse is idle...")
            self.pause_toggle_text.set("Resume")
        else:
            new_text = f"Tracking the selected app: {self.app}"
            if self.page_label["text"] != new_text:
                self.pause_toggle_text.set("Pause")
                self.page_label.config(text=new_text)

        self.update_queue.put((self.TIME_UPDATE, time_text))
        self.logic.file_handler.set_continuing_tracker(False)

    def toggle_pause_tracker(self, button=True):
        if self.pause_toggle_text.get() == "Pause":
            self.pause_toggle_text.set("Resume")
        else:
            self.pause_toggle_text.set("Pause")

        if button:
            if self.logic.time_tracker.get_is_paused():
                self.logic.time_tracker.resume()
            else:
                self.logic.time_tracker.pause()

    def _stop(self):
        confirm = messagebox.askyesno("Confirm Stop Tracking", "Are you sure you want to stop tracking?\nProgress will be saved.")
        if confirm:
            self.stop_button_pressed = True

    def _periodic_update(self):
        try:
            while True:
                item = self.update_queue.get_nowait()
                if item[0] == self.TIME_UPDATE:
                    self.time_label.config(text=item[1])
                elif item[0] == self.APP_UPDATE:
                    self.page_label.config(text=f"Tracking: {item[1]}")
        except queue.Empty:
            pass
        self.after(250, self._periodic_update)

    def start_update_thread(self):
        self.update_thread.start()

    def stop_threads(self):
        self.stop_event.set()
