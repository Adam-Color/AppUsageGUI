import tkinter as tk
import pickle

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
        if self.logic_controller.session_files.get_continuing_session():
            session_time = self.logic_controller.time_tracker.get_total_time()
            #print("Session time: ", session_time) #! debug print
            session_app_name = self.logic_controller.tracker.get_selected_app()
            #print("Session_app_name: ", session_app_name) #! debug print

            data = {'app_name': session_app_name, 'time_spent': session_time}
            print(data)

            serialized_data = pickle.dumps(data)

            self.logic_controller.session_files.save_data(serialized_data)

            # show to session total window
            self.controller.show_frame("SessionTotalWindow")
        else:
            self.controller.show_frame("CreateSessionWindow")
    
    def dont_save(self):
        """confirm data deletion"""
        ans = tk.messagebox.askyesno("Delete Confirmation", "Are you sure you don't want to save?")
        if ans:
            self.logic_controller.time_tracker.reset()
            self.logic_controller.tracker.reset()
            self.controller.show_frame("MainWindow")
