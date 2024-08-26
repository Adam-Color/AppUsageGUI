import tkinter as tk

# TODO: controller.session_files.set_continuing_session(True) when session is loaded

class SessionsWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, controller)