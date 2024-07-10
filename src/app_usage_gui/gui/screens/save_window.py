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
        button_yes = tk.Button(self, text="Yes", command=lambda: print("yes"))
        button_yes.pack(pady=2)
        button_no = tk.Button(self, text="No", command=lambda: print("no"))
        button_no.pack(pady=5)