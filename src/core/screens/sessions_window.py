import tkinter as tk

# TODO: controller.session_files.set_continuing_session(True) when session is loaded

class SessionsWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        # label for SessionsWindow
        label = tk.Label(self, text="Select a Session to continue from:")
        label.pack(side="top", fill="x", pady=5)

        # create the frame for the listbox and scrollbar
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True)

        # create the listbox
        self.session_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.session_listbox.pack(side="left", fill="both", expand=True)

        # create the scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.session_listbox.yview)
        scrollbar.pack(side="right", fill="y")

        # configure the listbox to use the scrollbar
        self.session_listbox.config(yscrollcommand=scrollbar.set)

        # button to make the selection
        select_button = tk.Button(self, text="Select", command=self.select_session)
        select_button.pack(pady=10)

    def select_session(self):
        return 0
