import tkinter as tk

from core.utils.file_utils import get_sessions
from core.utils.file_utils import get_sessions_directory
from core.utils.time_utils import format_time

class SessionsWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic = logic_controller

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

        self.load_sessions()

        # button to make the selection
        select_button = tk.Button(self, text="Continue from selected session", command=self.select_session, width=25)
        select_button.pack(pady=5)

        # button to analyze the session
        analyze_button = tk.Button(self, text="Analyze selected session", command=self.analyze_session, width=25)
        analyze_button.pack(pady=5)

        # button to delete the session
        delete_button = tk.Button(self, text="Delete selected session", command=self.delete_session, width=25)
        delete_button.pack(pady=5)

        back_button = tk.Button(self, text="Main Menu", command=lambda: (self.controller.reset_frames(), self.controller.show_frame("MainWindow")))
        back_button.pack(pady=5, side='bottom')

    def load_sessions(self):
        """Load session data into the listbox and 
        handle broken sessions"""

        sessions = get_sessions()
        for session in sessions:
            session_name = session.split(".")[0]
            # Load data for the current session
            self.logic.file_handler.load_session_data(session_name)
            session_data = self.logic.file_handler.get_data()
            if session_data is not None:
                app_name = session_data['app_name']
                time_spent = session_data['time_spent']
                # Format the time spent
                formatted_time = format_time(int(time_spent))
                # Insert into the Listbox
                self.session_listbox.insert(tk.END, f"{session_name}: {app_name}, {formatted_time} on record")
        corrupt_sessions = self.logic.file_handler.get_corrupt_sessions()
        if len(corrupt_sessions) > 0:
            error_string = "The following session(s) failed to load:\n\n"
            for session in corrupt_sessions:
                name, error = session
                error_string += "\n" + name + ": " + error
            tk.messagebox.showerror("Session Error", error_string + f"\n\nTo fix or delete session files, go to the {get_sessions_directory()} directory\n")

    def get_session_text(self):
        selected_index = self.session_listbox.curselection()
        if selected_index:
            return self.session_listbox.get(selected_index)

    def select_session(self):
        if not self.get_session_text():
            tk.messagebox.showerror("Error", "No session selected")
            return 0
        self.controller.frames["TrackerWindow"].start_update_thread()
        selected_app_name = self.get_session_text().split(": ")[1].split(", ")[0]
        selected_session_name = self.get_session_text().split(": ")[0]

        # update the logic session name var
        self.logic.file_handler.set_file_name(selected_session_name)

        # tell the controller we are continuing from a session
        self.logic.file_handler.set_continuing_session(True)

        # load selected session data into the file handler,
        # so it's ready to be pulled
        self.logic.file_handler.load_session_data(selected_session_name)

        # start/reset tracking threads
        self.logic.app_tracker.reset()
        self.logic.app_tracker.set_selected_app(selected_app_name)
        self.logic.time_tracker.reset(add_time=self.logic.file_handler.get_data()['time_spent'])
        self.logic.time_tracker.start()
        self.logic.time_tracker.clock()

        # show the TrackerWindow
        self.controller.show_frame('TrackerWindow')

    def analyze_session(self):
        if not self.get_session_text():
            tk.messagebox.showerror("Error", "No session selected")
            return 0
        selected_session_name = self.get_session_text().split(": ")[0]
        # load the session data
        self.logic.file_handler.load_session_data(selected_session_name)
        self.controller.frames['SessionTotalWindow'].total_session_time_thread.start()
        self.controller.frames['SessionTotalWindow'].update_total_time()
        # show the SessionTotalWindow
        self.controller.show_frame('SessionTotalWindow')

    def delete_session(self):
        if not self.get_session_text():
            tk.messagebox.showerror("Error", "No session selected")
            return 0
        else:
            selected_session_name = self.get_session_text().split(": ")[0]
            # ask for confirmation
            confirm = tk.messagebox.askyesno("Confirm Deletion",
                                             f"Are you sure you want to delete the session '{selected_session_name}'? \nThis action cannot be undone.")
            if confirm:
                self.logic.file_handler.delete_session(selected_session_name)
                self.session_listbox.delete(self.session_listbox.curselection())
