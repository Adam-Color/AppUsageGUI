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

        input_tracker_time_text = tk.StringVar()
        input_tracker_time_text.set(str(self.logic_controller.input_tracker.get_idle_time_limit()))

        input_tracker_time_label = tk.Label(self, text="Idle time limit: ")
        input_tracker_time_label.pack(side="left", padx=1)

        input_tracker_time_entry = tk.Entry(self,
                                            name="input_tracker",
                                            textvariable=input_tracker_time_text,
                                            validate="key",
                                            validatecommand=vcmd, width=3)
        input_tracker_time_entry.pack(side="left", padx=1, expand=False)

        input_tracker_time_label_a = tk.Label(self, text="seconds")
        input_tracker_time_label_a.pack(side="left", padx=1)
