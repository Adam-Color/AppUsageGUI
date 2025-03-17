import tkinter as tk
import os

from core.utils.file_utils import read_file, write_file, config_file

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
        self.logic_controller = logic_controller

        vcmd = (self.register(validate_numeric), '%P')
        label = tk.Label(self, text="Tracker settings:\n")
        label.pack(side="top", fill="x", padx=5)

        self.settings = {
            "mouse_tracker_enabled": False,
            "mouse_idle_time_limit": 300
        }

        if os.path.exists(config_file()):
            self.settings = read_file(config_file())

        self.mouse_tracker_time_text = tk.StringVar()
        self.mouse_tracker_time_text.set(str(self.logic_controller.mouse_tracker.get_idle_time_limit()))
        self.enable_mouse_tracker = tk.IntVar()
        
        mouse_tracker_checkbox = tk.Checkbutton(self, text="Enable Mouse tracker", variable=self.enable_mouse_tracker)
        mouse_tracker_checkbox.pack()

        mouse_tracker_time_label = tk.Label(self, text="\nMouse idle time limit: ")
        mouse_tracker_time_label.pack(side="top", padx=1)

        mouse_tracker_time_entry = tk.Entry(self,
                                            name="mouse_tracker",
                                            textvariable=self.mouse_tracker_time_text,
                                            validate="key",
                                            validatecommand=vcmd, width=3)
        mouse_tracker_time_entry.pack(side="top", padx=1, expand=False)

        mouse_tracker_time_label_a = tk.Label(self, text="seconds")
        mouse_tracker_time_label_a.pack(side="top", padx=1)

        discard_button = tk.Button(self, text="Discard Changes", command=self.discard_changes)
        discard_button.pack(side="bottom", fill="y", padx=1, pady=5)

        save_button = tk.Button(self, text="Save Changes", command=self.save_changes)
        save_button.pack(side="bottom", fill="y", padx=1, pady=5)

    def save_changes(self):
        # set intvars
        self.logic_controller.mouse_tracker.set_enabled(self.enable_mouse_tracker.get() == 1)
        self.settings["mouse_tracker_enabled"] = self.logic_controller.mouse_tracker.is_enabled()

        # set text items
        self.logic_controller.mouse_tracker.set_idle_time_limit(int(self.mouse_tracker_time_text.get()))
        self.settings["mouse_idle_time_limit"] = self.logic_controller.mouse_tracker.get_idle_time_limit()

        # save data to config.dat
        write_file(config_file(), self.settings)

        # show main window
        self.controller.show_frame("MainWindow")

    def discard_changes(self):
        # intvars
        self.enable_mouse_tracker = tk.IntVar()

        # text boxes
        self.mouse_tracker_time_text = tk.StringVar()

        self.controller.show_frame("MainWindow")
