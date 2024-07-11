import tkinter as tk

class SaveWindow(tk.Frame):
    def __init__(self, parent, controller):
        print("SaveWindow initialized")
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # display the page label
        self.page_label = tk.Label(self, text="Would you like to save the recorded data?")
        self.page_label.pack(pady=5)

        # display the yes/no buttons
        button_yes = tk.Button(self, text="Yes", command=self.save)
        button_yes.pack(pady=2)
        button_no = tk.Button(self, text="No", command=self.dont_save)
        button_no.pack(pady=5)

    def save(self):
        print("data is to be saved")
    
    def dont_save(self):
        # confirm data deletion
        ans = tk.messagebox.askyesno("Delete Confirmation", "Are you sure you don't want to save?")
        if ans:
            print("data is to be deleted")