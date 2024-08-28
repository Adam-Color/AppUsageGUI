import tkinter as tk

from core.gui_root import GUIRoot

from core.logic.app_tracker import AppTracker
from core.logic.time_tracker import TimeTracker
from core.logic.file_handler import FileHandler

def main():
    root = tk.Tk()
    root.title("App Usage GUI")

    tracker = AppTracker()
    time_tracker = TimeTracker()
    session_files = FileHandler()

    win = GUIRoot(root)
    win.pack(side="top", fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()
