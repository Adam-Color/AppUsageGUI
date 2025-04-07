"""popout window to analyze session data"""
import tkinter as tk
from tkinter import ttk

class AnalyzeDataWindow(tk.Toplevel):
    def __init__(self, parent, controller, logic_controller):
        super().__init__(parent)  # Toplevel window with `parent` as master
        self.controller = controller
        self.logic_controller = logic_controller

        self.title("Popout Window")
        self.geometry("1600x1200")

        ttk.Label(self, text="This is a popout!").pack(pady=10)
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=10)

