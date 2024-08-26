import tkinter as tk

class CreateSessionWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        name_label = tk.Label(self, text="Name this session:")
        name_label.pack(side="top", fill="x", pady=5)

        # User inputs session name
        self.session_name_input = tk.Entry(self, text="")
        self.session_name_input.pack(side="top", fill="x", pady=5)

        # Confirm session name entry
        confirm_button = tk.Button(self, text="Confirm", command=self.on_confirm)
        confirm_button.pack(side="top", fill="x", pady=5)

    def on_confirm(self):
        session_name = self.session_name_input.get()
        self.session_save(session_name)

    def session_save(self, session_name):
        self.controller.session_files.set_file_name(session_name)
        session_time = self.controller.time_tracker.get_time(saved=True)
        print("Session time: ", session_time) #!
        session_app_name = self.controller.tracker.get_selected_app()
        print("Session_app_name: ", session_app_name) #!
        data = f"{session_app_name}-{session_time}"
        print(data) #!
        # convert to binary
        data = data.encode('ascii')
        self.controller.session_files.save_data(data)
