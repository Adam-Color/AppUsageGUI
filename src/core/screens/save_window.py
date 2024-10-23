import tkinter as tk

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
            self.controller.show_frame("SessionTotalWindow")
        else:
            self.controller.show_frame("CreateSessionWindow")
    
    def dont_save(self):
        # confirm data deletion
        ans = tk.messagebox.askyesno("Delete Confirmation", "Are you sure you don't want to save?")
        if ans:
            print("!!! TODO: data is to be deleted - code needs to be written !!!")
            self.logic_controller.time_tracker.reset()
            self.controller.show_frame("MainWindow")
