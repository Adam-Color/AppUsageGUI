import tkinter as tk
from core.utils.file_utils import sessions_exist, get_projects

class MainWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        super().__init__(parent)
        self.controller = controller
        self.logic = logic_controller

        # Check if we have projects or sessions
        _ = get_projects()
        _ = sessions_exist()

        # Title Label
        label_text = "Track app usage in a project or standalone session."
        label = tk.Label(self, text=label_text, font=("Arial", 14, "bold"))
        label.pack(side="top", pady=(15, 20))

        # Button Container
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        # Row 1: Sessions + Projects
        btn_session = tk.Button(
            button_frame, text="Start New Session",
            command=lambda: self.controller.show_frame("CreateSessionWindow"),
            width=20, height=2
        )
        btn_session.grid(row=0, column=0, padx=10, pady=10)

        btn_projects = tk.Button(
            button_frame, text="Projects",
            command=lambda: self.controller.show_frame("ProjectsWindow"),
            width=20, height=2
        )
        btn_projects.grid(row=0, column=1, padx=10, pady=10)

        # Row 2: Sessions list + Rules
        btn_sessions = tk.Button(
            button_frame, text="View Sessions",
            command=lambda: [
                self.controller.show_frame("SessionsWindow"),
                self.logic.app_tracker.start_filter_reset(refresh=True)
            ],
            width=20, height=2
        )
        btn_sessions.grid(row=1, column=0, padx=10, pady=10)

        btn_rules = tk.Button(
            button_frame, text="Custom Rules",
            command=lambda: self.controller.show_frame("TrackerSettingsWindow"),
            width=20, height=2
        )
        btn_rules.grid(row=1, column=1, padx=10, pady=10)

        # Exit Button at Bottom
        exit_button = tk.Button(
            self, text="Exit", command=self.controller.on_close,
            width=10, height=1, bg="#d9534f", fg="white"
        )
        exit_button.pack(side="bottom", pady=15)
