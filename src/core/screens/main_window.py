import tkinter as tk

from core.utils.file_utils import sessions_exist, get_projects

class MainWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller # GUI controller
        self.logic = logic_controller
        self.logic = logic_controller

        # Check if we have projects or sessions
        projects = get_projects()
        has_sessions = sessions_exist()
        

        label_text = "Track app usage in a project or standalone session."

        label = tk.Label(self, text=label_text)
        label.pack(side="top", fill="x", pady=10)

        # Start new session button
        button1 = tk.Button(self, text="Start new session",
                            command=lambda: self.controller.show_frame("CreateSessionWindow"), width=25)
        button1.pack(pady=3)

        # Project management button
        button_projects = tk.Button(self, text="Projects",
                                   command=lambda: self.controller.show_frame("ProjectsWindow"), width=25)
        button_projects.pack(pady=3)

        # Sessions button (always show)
        button2 = tk.Button(self, text="Sessions",
                            command=lambda: [self.controller.show_frame("SessionsWindow"), self.logic.app_tracker.start_filter_reset(refresh=True)], width=25)
        button2.pack(pady=3)

        # Configure custom rules button
        button3 = tk.Button(self, text="Configure custom rules",
                            command=lambda: self.controller.show_frame("TrackerSettingsWindow"),
                            width=25)
        button3.pack(pady=3)

        exit_button = tk.Button(self, text=" Exit ", command=lambda: self.controller.on_close())
        exit_button.pack(pady=10, side='bottom')
