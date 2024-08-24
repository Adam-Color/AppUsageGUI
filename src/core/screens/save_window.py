import tkinter as tk

class SaveWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        # display the page label
        self.page_label = tk.Label(self, text="Would you like to save the recorded data?")
        self.page_label.pack(pady=5)

        # display the yes/no buttons
        button_yes = tk.Button(self, text="Yes", command=lambda: controller.show_frame("CreateSessionWindow"))
        button_yes.pack(pady=2)
        button_no = tk.Button(self, text="No", command=self.dont_save)
        button_no.pack(pady=5)
    
    def dont_save(self):
        # confirm data deletion
        ans = tk.messagebox.askyesno("Delete Confirmation", "Are you sure you don't want to save?")
        if ans:
            print("TODO: data is to be deleted")
