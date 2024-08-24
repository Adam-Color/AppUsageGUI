import tkinter as tk
from core.utils.file_utils import sessions_exist

class MainWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label_text = "To begin app tracking, start a new session:"

        if sessions_exist():
            label_text = "What would you like to do?"

        label = tk.Label(self, text=label_text)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Start a new session",
                            command=lambda: controller.show_frame("SelectAppWindow"))
        button1.pack()

        if label_text == "What would you like to do?":
            button2 = tk.Button(self, text="Continue a previous session",
                                command=lambda: controller.show_frame("SessionsWindow")) 
            button2.pack()
