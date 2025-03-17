import tkinter as tk
import pickle

class CreateSessionWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic_controller = logic_controller

        name_label = tk.Label(self, text="Name this session:")
        name_label.pack(side="top", fill="x", pady=5)

        # User inputs session name
        self.session_name_input = tk.Entry(self, text="")
        self.session_name_input.pack(side="top", fill="x", pady=5, padx=20)

        # Confirm session name entry
        confirm_button = tk.Button(self, text="Confirm", command=self.on_confirm)
        confirm_button.pack(side="top", fill="x", pady=5)

    def on_confirm(self):
        """Resets trackers upon confirmation"""
        session_name = self.session_name_input.get()
        self.session_save(session_name)
        self.logic_controller.time_tracker.reset()
        self.logic_controller.app_tracker.reset()
        self.controller.show_frame("SessionTotalWindow")

    def session_save(self, session_name):
        self.logic_controller.file_handler.set_file_name(session_name)
        session_time = self.logic_controller.time_tracker.get_time(saved=True)
        print("Session time: ", session_time) #!
        session_app_name = self.logic_controller.app_tracker.get_selected_app()
        print("Session_app_name: ", session_app_name) #!

        data = {'app_name': session_app_name, 'time_spent': session_time}

        self.logic_controller.file_handler.save_session_data(data)
