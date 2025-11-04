import tkinter as tk
import os
import queue
from core.utils.tk_utils import messagebox
from core.utils.file_utils import read_file, write_file, config_file

import logging
logger = logging.getLogger(__name__)

def validate_numeric(value):
    """Check if value is numeric and greater than or equal to 0"""
    if value == "":  # Allow empty string (for backspace)
        return True
    try:
        value = float(value)
        return value >= 0
    except ValueError:
        return False

class TrackerSettingsWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic = logic_controller
        self.update_queue = queue.Queue()
        self.restart_needed = False

        vcmd = (self.register(validate_numeric), '%P')

        # Title
        title = tk.Label(self, text="Tracker Settings", font=("TkDefaultFont", 14, "bold"))
        title.pack(pady=(10, 5))

        # Subheading
        subtitle = tk.Label(self, text="Adjust how tracking and filtering work.")
        subtitle.pack(pady=(0, 15))

        self.settings = {
            "mouse_tracker_enabled": False,
            "mouse_idle_time_limit": 90,
            "is_filter_enabled": True
        }

        if os.path.exists(config_file()):
            saved_settings = read_file(config_file())
            logging.info(f"config: {saved_settings}")
            if saved_settings:
                self.settings.update(saved_settings)

        # Temporary variables for toggles
        self.mouse_tracker_enabled_temp = self.settings["mouse_tracker_enabled"]
        self.app_filter_enabled_temp = self.settings["is_filter_enabled"]

        # Toggle texts
        self.mouse_toggle_text = tk.StringVar()
        self.mouse_toggle_text.set(
            "Disable Mouse Tracker" if self.settings["mouse_tracker_enabled"] else "Enable Mouse Tracker"
        )

        self.app_filter_text = tk.StringVar()
        self.app_filter_text.set(
            "Disable App Filtering" if self.settings["is_filter_enabled"] else "Enable App Filtering"
        )

        self.mouse_tracker_time_text = tk.StringVar()
        self.mouse_tracker_time_text.set(str(self.logic.mouse_tracker.get_idle_time_limit()))

        # --- Layout starts here ---
        # Mouse tracker toggle
        self.mouse_tracker_enable_button = tk.Button(
            self, textvariable=self.mouse_toggle_text,
            command=self.toggle_mouse_tracker, width=25
        )
        self.mouse_tracker_enable_button.pack(pady=5)

        # Idle time entry in a row
        idle_frame = tk.Frame(self)
        idle_frame.pack(pady=10)

        idle_label = tk.Label(idle_frame, text="Mouse idle time limit:")
        idle_label.pack(side="left", padx=(0, 5))

        idle_entry = tk.Entry(
            idle_frame, name="mouse_tracker",
            textvariable=self.mouse_tracker_time_text,
            validate="key", validatecommand=vcmd, width=5, justify="center"
        )
        idle_entry.pack(side="left")

        idle_units = tk.Label(idle_frame, text="seconds")
        idle_units.pack(side="left", padx=(5, 0))

        # App filtering toggle
        self.app_filter_enable_button = tk.Button(
            self, textvariable=self.app_filter_text,
            command=self.toggle_app_filter, width=25
        )
        self.app_filter_enable_button.pack(pady=15)

        # Action buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", pady=10)

        discard_button = tk.Button(button_frame, text="Discard Changes", command=self.discard_changes, width=18)
        discard_button.pack(side="bottom", padx=5)

        save_button = tk.Button(button_frame, text="Save Changes", command=self.save_changes, width=18)
        save_button.pack(side="bottom", padx=5)

        # Start the update queue
        self.update_elements()

    def toggle_mouse_tracker(self):
        self.mouse_tracker_enabled_temp = not self.mouse_tracker_enabled_temp
        self.mouse_toggle_text.set(
            "Disable Mouse Tracker" if self.mouse_tracker_enabled_temp else "Enable Mouse Tracker"
        )

    def toggle_app_filter(self):
        self.restart_needed = True
        self.app_filter_enabled_temp = not self.app_filter_enabled_temp
        self.app_filter_text.set(
            "Disable App Filtering" if self.app_filter_enabled_temp else "Enable App Filtering"
        )
        self.update_queue.put("app_filter_toggle")

    def update_elements(self):
        try:
            while not self.update_queue.empty():
                item = self.update_queue.get_nowait()
                if item == "mouse_tracker_toggle":
                    self.mouse_toggle_text.set(
                        "Disable Mouse Tracker" if self.mouse_tracker_enabled_temp else "Enable Mouse Tracker"
                    )
                elif item == "app_filter_toggle":
                    self.app_filter_text.set(
                        "Disable App Filtering" if self.app_filter_enabled_temp else "Enable App Filtering"
                    )
        except queue.Empty:
            pass
        self.after(100, self.update_elements)

    def save_changes(self):
        self.settings["mouse_tracker_enabled"] = self.mouse_tracker_enabled_temp
        self.settings["is_filter_enabled"] = self.app_filter_enabled_temp
        self.logic.mouse_tracker.set_enabled(self.settings["mouse_tracker_enabled"])

        try:
            idle_time_limit = int(self.mouse_tracker_time_text.get())
            self.logic.mouse_tracker.set_idle_time_limit(idle_time_limit)
            self.settings["mouse_idle_time_limit"] = idle_time_limit
        except ValueError:
            pass

        write_file(config_file(), self.settings)

        self.controller.reset_frames()
        if self.restart_needed:
            messagebox.showinfo("Restart Required", "Changes will take effect after a restart.")
        self.controller.show_frame("MainWindow")

    def discard_changes(self):
        self.controller.reset_frames()
        self.controller.show_frame("MainWindow")
