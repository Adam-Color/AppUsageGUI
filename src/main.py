import tkinter as tk

from core.gui_root import GUIRoot
from core.utils.file_utils import sessions_exist, user_dir_exists


def main():
    # calls to create the app directories
    sessions_exist()
    user_dir_exists()

    root = tk.Tk()
    root.title("App Usage GUI")

    win = GUIRoot(root)
    win.pack(side="top", fill="both", expand=True)

    root.mainloop()

if __name__ == "__main__":
    main()
