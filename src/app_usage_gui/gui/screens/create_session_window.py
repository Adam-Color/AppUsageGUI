import tkinter as tk
from gui.logic.file_handler import FileHandler
from gui.screens.tracker_window import get_rec_time

class CreateSessionWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        name_label = tk.Label(self, text="Name this session:")
        name_label.pack(side="top", fill="x", pady=5)

        # User inputs session name
        session_name_input = tk.Entry(self, text="")
        session_name_input.pack(side="top", fill="x", pady=5)

        # Confirm session name entry
        confirm_button = tk.Button(self, text="Confirm", command=print())
        confirm_button.pack(side="top", fill="x", pady=5)

    def session_save(self, session_name):
        