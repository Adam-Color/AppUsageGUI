import tkinter as tk
import pickle

#TODO: implement time readout

class SessionTotalWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic_controller = logic_controller

        self.time_readout = ""

        # display the page label
        self.page_label = tk.Label(self, text="Total time for this session:")
        self.page_label.pack(pady=5)

        # display the total time label
        self.total_time_label = tk.Label(self, text=self.time_readout)
        self.total_time_label.pack(pady=10)

    def update_total_time(self, time):
        self.time_readout = time
        self.total_time_label.config(text=self.time_readout)

    def session_update(self, session_name):
        self.logic_controller.session_files.set_file_name(session_name)
        session_time = self.logic_controller.time_tracker.get_time(saved=True)
        print("Session time: ", session_time) #!
        session_app_name = self.logic_controller.tracker.get_selected_app()
        print("Session_app_name: ", session_app_name) #!

        data = {'app_name': session_app_name, 'time_spent': session_time}
        print(data)

        serialized_data = pickle.dumps(data)

        self.logic_controller.session_files.save_data(serialized_data)