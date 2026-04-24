import tkinter as tk
import time
from core.utils.tk_utils import messagebox

from core.utils.file_utils import read_file, config_file
from _version import __version__

import logging
logger = logging.getLogger(__name__)

class SaveWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic = logic_controller

        # display the page label
        self.page_label = tk.Label(
            self,
            text="\n\n\nWould you like to save the recorded data?",
            font=("Arial", 20, "bold")
        )
        self.page_label.pack(pady=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        # display the yes/no buttons
        button_yes = tk.Button(button_frame, text="Yes",
            command=self.save,
            font=("Arial", 20),
            width=4, height=1,
            bg="#0985d9",
            highlightbackground="#0985d9",
            highlightcolor="#0985d9"
        )
        button_yes.pack(side='right', padx=5)
        self.bind("<Return>", lambda event: self.save())
        button_no = tk.Button(button_frame, text="No",
            command=self.dont_save,
            font=("Arial", 20),
            width=4, height=1
        )
        button_no.pack(side='left', padx=5)

        back_button = tk.Button(self, text="Main Menu", command=self.dont_save)
        back_button.pack(pady=5, side='bottom')

    def save(self):
        time.sleep(0.3)

        # Stop the time tracker before saving to ensure we have proper stop times
        if self.logic.time_tracker.is_running():
            self.logic.time_tracker.stop()

        if self.logic.file_handler.get_continuing_session():
            # Continuing an existing session - update it
            session_time = self.logic.time_tracker.get_total_time()
            session_app_name = self.logic.app_tracker.get_selected_app()
            captures = self.logic.time_tracker.get_time_captures()
            try:
                sv = self.logic.file_handler.get_data()["session_version"]
            except KeyError:
                sv = "1.0"
            try:
                self.config = read_file(config_file())
            except FileNotFoundError:
                self.config = {}

            data = {
                    'app_name': session_app_name,
                    'time_spent': session_time,
                    'session_version': sv,
                    'config': self.config,
                    'time_captures': captures # {'starts': [], 'stops': [], 'pauses': [{start: 0, how_long: 0}]}
                    }
            logger.info("save_window.py data save: " + f"{data}")

            self.logic.file_handler.save_session_data(data)

            # show to session total window
            self.controller.frames['SessionTotalWindow'].total_session_time_thread.start()
            self.controller.frames['SessionTotalWindow'].update_total_time()
            self.controller.show_frame("SessionTotalWindow")
        else:
            # New session - save it for the first time
            session_time = self.logic.time_tracker.get_time(saved=True)
            session_app_name = self.logic.app_tracker.get_selected_app()
            captures = self.logic.time_tracker.get_time_captures()
            try:
                self.config = read_file(config_file())
            except FileNotFoundError:
                self.config = {}

            data = {
                    'app_name': session_app_name,
                    'time_spent': session_time,
                    'session_version': __version__.split('.')[0] + '.' + __version__.split('.')[1],
                    'config': self.config,
                    'time_captures': captures # {'starts': [], 'stops': [], 'pauses': [{start: 0, how_long: 0}]}
                    }
            logger.info(f"Session data: {data}")

            self.logic.file_handler.save_session_data(data)

            # Load the saved session data and show session total window
            session_name = self.logic.file_handler.get_file_name()
            project_name = self.logic.file_handler.get_current_project()
            self.logic.file_handler.load_session_data(session_name, project_name)
            self.controller.frames['SessionTotalWindow'].total_session_time_thread.start()
            self.controller.frames['SessionTotalWindow'].update_total_time()
            self.controller.show_frame("SessionTotalWindow")

    def dont_save(self):
        """confirm data deletion"""
        ans = messagebox.askyesno("AppUsageGUI", "Are you sure you don't want to save?")
        if ans:
            time.sleep(0.3)
            self.logic.time_tracker.reset()
            self.logic.app_tracker.reset()
            self.controller.reset_frames()
            self.controller.show_frame("MainWindow")
