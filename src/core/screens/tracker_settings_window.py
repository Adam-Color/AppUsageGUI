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

        apply_button = tk.Button(self, text="Save Changes", command=print(1))
        apply_button.pack(side="bottom", fill="y", padx=1, pady=5)

        apply_button = tk.Button(self, text="Discard Changes", command=print(1))
        apply_button.pack(side="bottom", fill="y", padx=1, pady=5)

    def save_changes(self):
        self.logic_controller.mouse_tracker.set_idle_time_limit(int(self.mouse_tracker_time_text))
        self.controller.show_frame("MainWindow")

    def discard_changes(self):
        self.controller.show_frame("MainWindow")
