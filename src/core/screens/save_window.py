import tkinter as tk
import time

from core.utils.time_utils import format_time

class SaveWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic_controller = logic_controller
        
        # display the page label
        self.page_label = tk.Label(self, text="Would you like to save the recorded data?")
        self.page_label.pack(pady=5)

        # display the yes/no buttons
        button_yes = tk.Button(self, text="Yes", command=self.save)
        button_yes.pack(pady=2)
        button_no = tk.Button(self, text="No", command=self.dont_save)
        button_no.pack(pady=5)

    def save(self):
        time.sleep(0.3)
        if self.logic_controller.file_handler.get_continuing_session():
            session_time = self.logic_controller.time_tracker.get_total_time()
            session_app_name = self.logic_controller.app_tracker.get_selected_app()

            data = {'app_name': session_app_name, 'time_spent': session_time}

            print(f"app_name: {session_app_name}, time_spent: {format_time(int(session_time))}")

            self.logic_controller.file_handler.save_session_data(data)

            # show to session total window
            self.controller.show_frame("SessionTotalWindow")
        else:
            self.controller.show_frame("CreateSessionWindow")
    
    def dont_save(self):
        """confirm data deletion"""
        ans = tk.messagebox.askyesno("Delete Confirmation", "Are you sure you don't want to save?")
        if ans:
            time.sleep(0.3)
            self.logic_controller.time_tracker.reset()
            self.logic_controller.app_tracker.reset()
            self.controller.reset_frames()
            self.controller.show_frame("MainWindow")
