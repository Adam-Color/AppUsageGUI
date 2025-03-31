import tkinter as tk
import re

from core.utils.file_utils import read_file, config_file

def validate_name(value):
    """Check if name is valid for saving as a file"""
    if value == "":  # Allow empty string (for backspace)
        return True

    # Check for illegal characters
    illegal_chars = r'[<>:"/\\|?*\x00-\x1F.]'
    if re.search(illegal_chars, value):
        return False

    return True

class CreateSessionWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic_controller = logic_controller

        vcmd = (self.register(validate_name), '%P')
        self.session_name = tk.StringVar()
        self.session_name.set("")

        name_label = tk.Label(self, text="Name this session:")
        name_label.pack(side="top", fill="x", pady=5)

        # User inputs session name
        self.session_name_input = tk.Entry(self, textvariable=self.session_name,
                                            validate="key", validatecommand=vcmd)
        self.session_name_input.pack(side="top", fill="x", pady=5, padx=20)

        # Confirm session name entry
        confirm_button = tk.Button(self, text="Confirm", command=self.on_confirm)
        confirm_button.pack(side="top", fill="x", pady=5)

        back_button = tk.Button(self, text="Main Menu", command=lambda: (self.controller.reset_frames(), self.controller.show_frame("MainWindow")))
        back_button.pack(pady=5, side='bottom')

    def on_confirm(self):
        """Saves session and resets trackers upon confirmation"""
        self.session_save(self.session_name.get())
        self.logic_controller.time_tracker.reset()
        self.logic_controller.app_tracker.reset()
        self.controller.show_frame("SessionTotalWindow")

    def session_save(self, session_name):
        self.logic_controller.file_handler.set_file_name(session_name)
        session_time = self.logic_controller.time_tracker.get_time(saved=True)
        session_app_name = self.logic_controller.app_tracker.get_selected_app()
        captures = self.logic_controller.time_tracker.get_time_captures()
        try:
            self.config = read_file(config_file())
        except FileNotFoundError:
            self.config = {}

        data = {
                'app_name': session_app_name,
                'time_spent': session_time,
                'config': self.config,
                'time_captures': captures # {'starts': [], 'stops': [], 'pauses': [{start: 0, how_long: 0}]}
                }

        self.logic_controller.file_handler.save_session_data(data)
