import tkinter as tk
import os
import threading
import queue
from PIL import Image, ImageTk

from core.utils.tk_utils import messagebox
from core.utils.time_utils import format_time

from _path import resource_path

def load_white_icon(path, size=(50,50)):
    # Load image
    img = Image.open(path).convert("RGBA")

    # don't modify the original image if macOS
    if os.name == 'posix' and 'Darwin' in os.uname().sysname:
        if size:
            img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    # Replace non-transparent pixels with white
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[3] > 0:  # keep transparency
            new_data.append((255, 255, 255, item[3]))  # white
        else:
            new_data.append(item)
    img.putdata(new_data)

    # Resize if needed
    if size:
        img = img.resize(size, Image.LANCZOS)

    return ImageTk.PhotoImage(img)

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
        self.update_thread = None
        
        # images
        self.pause_photo = load_white_icon(os.path.join(resource_path("core"), "resources", "button-resources", "pause_button.png"))

        self.play_photo = load_white_icon(os.path.join(resource_path("core"), "resources", "button-resources", "play_button.png"))

        self.stop_photo = load_white_icon(os.path.join(resource_path("core"), "resources", "button-resources", "stop_button.png"))

        self._setup_widgets()

        self.update_queue = queue.Queue()
        self._periodic_update()

    def _setup_widgets(self):
        # Info note
        self.note_label = tk.Label(
            self,
            text="Tracking stops automatically when the tracked app is closed",
            font=("TkDefaultFont", 10)
        )
        self.note_label.pack(pady=(10, 5))

        # Current app being tracked
        self.page_label = tk.Label(
            self,
            text="Tracking the selected app:",
            font=("TkDefaultFont", 11, "italic")
        )
        self.page_label.pack(pady=5)

        # Large time display
        self.time_label = tk.Label(
            self,
            text=self.track_time_disp,
            font=("TkDefaultFont", 32, "bold")
        )
        self.time_label.pack(pady=20)

        # Controls (Pause/Resume + Stop) side by side
        controls_frame = tk.Frame(self)
        controls_frame.pack(pady=15)

        # Pause/Resume button
        self.pause_toggle_text = tk.StringVar(value="Pause")
        self.pause_button = tk.Button(
            controls_frame,
            textvariable=self.pause_toggle_text,
            image=self.pause_photo,
            compound="top",
            command=self.toggle_pause_tracker,
            bd=0,                # remove border
            padx=10,             # horizontal padding
            pady=10              # vertical padding
        )
        self.pause_button.pack(side="left", padx=1)

        # Stop button
        self.stop_button = tk.Button(
            controls_frame,
            text="Stop",
            image=self.stop_photo,
            command=self._stop,
            compound="top",
            bd=0,                # remove border
            padx=10,             # horizontal padding
            pady=10              # vertical padding
        )
        self.stop_button.pack(side="left", padx=1)

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

        if round(self.logic.time_tracker.get_elapsed_time()) > 0:
            self.controller.show_frame("SaveWindow")
        else:
            error_msg = "The tracked application is not running and cannot be found.\nThis session cannot be continued because the target application is not available."
            print(error_msg)
            messagebox.showerror(
                "App Not Found",
                error_msg
            )
            self.controller.reset_frames()
            self.controller.show_frame("MainWindow")

    def _should_start_tracking(self):
        return self.app and not self.logic.time_tracker.is_running()

    def _should_stop_tracking(self, app_names):
        return (
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
            time_text = format_time(int(secs))
        else:
            time_text = "No time data available"

        if self.logic.mouse_tracker.is_pausing():
            self.page_label.config(text="Tracking paused, mouse is idle...")
            self.pause_toggle_photo = self.play_photo
            self.pause_button["state"] = "disabled"
            self.stop_button["state"] = "disabled"
            self.pause_toggle_text.set("Resume")
        else:
            new_text = f"Tracking the selected app: {self.app}"
            if self.page_label["text"] != new_text:
                self.pause_toggle_photo = self.pause_photo
                self.page_label.config(text=new_text)
                self.pause_button["state"] = "normal"
                self.stop_button["state"] = "normal"
                self.pause_toggle_text.set("Pause")

        self.update_queue.put((self.TIME_UPDATE, time_text))
        self.logic.file_handler.set_continuing_tracker(False)

    def toggle_pause_tracker(self, button=True):
        if self.pause_toggle_text.get() == "Pause":
            self.pause_button.config(image=self.play_photo)
            self.pause_toggle_text.set("Resume")
        else:
            self.pause_button.config(image=self.pause_photo)
            self.pause_toggle_text.set("Pause")

        if button:
            if self.logic.time_tracker.get_is_paused():
                self.logic.time_tracker.resume()
            else:
                self.logic.time_tracker.pause()

    def _stop(self):
        confirm = messagebox.askyesno(
            "Confirm Stop Tracking",
            "Are you sure you want to stop tracking?\nProgress will be saved."
        )
        if confirm:
            self.stop_event.set()

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
        self.stop_event.clear()
        self.update_thread = threading.Thread(
            target=self._update_time_label,
            name="update_time_label", daemon=True
        )
        self.update_thread.start()

    def stop_threads(self):
        self.stop_event.set()
