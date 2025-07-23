import tkinter as tk
import os
import queue

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
        self.logic = logic_controller
        self.update_queue = queue.Queue()
        self.restart_needed = False

        vcmd = (self.register(validate_numeric), '%P')
        label = tk.Label(self, text="Tracker settings:\n")
        label.pack(side="top", fill="x", padx=5)

        self.settings = {
            "mouse_tracker_enabled": False,
            "mouse_idle_time_limit": 90,
            "is_filter_enabled": True
        }

        # Read settings file if it exists
        if os.path.exists(config_file()):
            saved_settings = read_file(config_file())
            if saved_settings:
                self.settings.update(saved_settings)  # Ensure settings are properly merged

        # Temporary variables for toggles
        self.mouse_tracker_enabled_temp = self.settings["mouse_tracker_enabled"]
        self.app_filter_enabled_temp = self.settings["is_filter_enabled"]
        
        # Set button text based on tracker status
        self.mouse_toggle_text = tk.StringVar()
        self.mouse_toggle_text.set("Disable Mouse Tracker" if self.settings["mouse_tracker_enabled"] else "Enable Mouse Tracker")

        # Set app filter text
        self.app_filter_text = tk.StringVar()
        self.app_filter_text.set("Disable App Filtering" if self.logic.app_tracker.is_filter_enabled else "Enable App Filtering")

        self.mouse_tracker_time_text = tk.StringVar()
        self.mouse_tracker_time_text.set(str(self.logic.mouse_tracker.get_idle_time_limit()))
        
        # Toggle mouse tracker button
        self.mouse_tracker_enable_button = tk.Button(self, textvariable=self.mouse_toggle_text, command=self.toggle_mouse_tracker, width=25)
        self.mouse_tracker_enable_button.pack()

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

        # Toggle app filtering button
        self.app_filter_enable_button = tk.Button(self, textvariable=self.app_filter_text, command=self.toggle_app_filter, width=25)
        self.app_filter_enable_button.pack(pady=15)

        discard_button = tk.Button(self, text="Discard Changes", command=self.discard_changes)
        discard_button.pack(side="bottom", fill="y", padx=1, pady=5)

        save_button = tk.Button(self, text="   Save Changes   ", command=self.save_changes)
        save_button.pack(side="bottom", fill="y", padx=1, pady=5)

        # Start the update queue
        self.update_elements()

    def toggle_mouse_tracker(self):
        """Update the temp variable when button is toggled and refresh UI."""
        self.mouse_tracker_enabled_temp = not self.mouse_tracker_enabled_temp
        self.mouse_toggle_text.set("Disable Mouse Tracker" if self.mouse_tracker_enabled_temp else "Enable Mouse Tracker")
    
    def toggle_app_filter(self):
        """Toggle the app filter and update the button text."""
        self.restart_needed = True
        self.app_filter_enabled_temp = not self.app_filter_enabled_temp
        self.app_filter_text.set("Disable App Filtering" if self.app_filter_enabled_temp else "Enable App Filtering")
        self.update_queue.put("app_filter_toggle")

    def update_elements(self):
        """Update the GUI elements with the current settings."""
        try:
            while not self.update_queue.empty():
                item = self.update_queue.get_nowait()
                if item == "mouse_tracker_toggle":
                    self.mouse_toggle_text.set("Disable Mouse Tracker" if self.mouse_tracker_enabled_temp else "Enable Mouse Tracker")
                elif item == "app_filter_toggle":
                    self.app_filter_text.set("Disable App Filtering" if self.app_filter_enabled_temp else "Enable App Filtering")
        except queue.Empty:
            pass
        self.after(100, self.update_elements)  # Keep checking queue

    def save_changes(self):
        """Save the settings and apply changes."""
        self.settings["mouse_tracker_enabled"] = self.mouse_tracker_enabled_temp
        self.settings["is_filter_enabled"] = self.app_filter_enabled_temp
        self.logic.mouse_tracker.set_enabled(self.settings["mouse_tracker_enabled"])
        self.settings["mouse_tracker_enabled"] = self.logic.mouse_tracker.is_enabled()

        # Save idle time limit
        try:
            idle_time_limit = int(self.mouse_tracker_time_text.get())
            self.logic.mouse_tracker.set_idle_time_limit(idle_time_limit)
            self.settings["mouse_idle_time_limit"] = idle_time_limit
        except ValueError:
            pass  # Ignore invalid input, prevent crash

        # Save data to config.dat
        write_file(config_file(), self.settings)

        # Show main window
        self.controller.reset_frames()
        if self.restart_needed:
            tk.messagebox.showinfo("Restart Required", "Changes will take effect after a restart.")
        self.controller.show_frame("MainWindow")

    def discard_changes(self):
        """Return to the main window."""
        self.controller.reset_frames()
        self.controller.show_frame("MainWindow")
