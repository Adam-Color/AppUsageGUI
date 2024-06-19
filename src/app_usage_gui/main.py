import tkinter as tk
from gui.gui_root import GUIRoot
import threading

def main():
    root = tk.Tk()
    root.title("App Usage GUI")

    win = GUIRoot(root)
    win.pack(side="top", fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()
