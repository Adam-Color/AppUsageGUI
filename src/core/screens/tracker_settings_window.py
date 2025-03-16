import tkinter as tk

def validate_numeric(value):
    """Check if value is a numeric and greater than or equal to 0"""
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

        mouse_tracker_time_text = tk.StringVar()
        mouse_tracker_time_text.set(str(self.logic_controller.mouse_tracker.get_idle_time_limit()))

        mouse_tracker_time_label = tk.Label(self, text="Mouse idle time limit: ")
        mouse_tracker_time_label.pack(side="top", padx=1)

        mouse_tracker_time_entry = tk.Entry(self,
                                            name="mouse_tracker",
                                            textvariable=mouse_tracker_time_text,
                                            validate="key",
                                            validatecommand=vcmd, width=3)
        mouse_tracker_time_entry.pack(side="top", padx=1, expand=False)

        mouse_tracker_time_label_a = tk.Label(self, text="seconds")
        mouse_tracker_time_label_a.pack(side="top", padx=1)

        apply_button = tk.Button(self, text="Apply", command=print(1))
        apply_button.pack(side="bottom", fill="y", padx=1)