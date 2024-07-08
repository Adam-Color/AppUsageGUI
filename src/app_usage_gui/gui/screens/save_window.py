import tkinter as tk

class SaveWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        print("SaveWindow initialized")