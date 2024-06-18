import tkinter as tk
from gui.utils.file_utils import sessions_exist

class MainWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="What would you like to do?")
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Start a new session",
                            command=lambda: controller.show_frame("SelectAppWindow"))
        button1.pack()

        if sessions_exist():
            button2 = tk.Button(self, text="Continue from a previous session",
                                command=lambda: controller.show_frame("SessionsWindow"))
        else:
            button2 = tk.Button(self, text="blank for now")
        
        button2.pack()