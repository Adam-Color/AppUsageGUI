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
        label = tk.Label(self, text="Tracker settings:")
        label.pack(side="top", fill="x", pady=5)

        mouse_tracker_time_text = tk.StringVar()
        mouse_tracker_time_text.set(str(self.logic_controller.mouse_tracker.get_idle_time_limit()))

        mouse_tracker_time_entry = tk.Entry(self,
                                            textvariable=mouse_tracker_time_text,
                                            validate="key",
                                            validatecommand=vcmd, width=3)
        mouse_tracker_time_entry.pack(side="top", pady=5, expand=False)