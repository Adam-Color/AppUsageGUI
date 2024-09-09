import tkinter as tk

from core.gui_root import GUIRoot
from core.utils.file_utils import sessions_exist


def main():
    sessions_exist()
    root = tk.Tk()
    root.title("App Usage GUI")

    win = GUIRoot(root)
    win.pack(side="top", fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()
