from time import sleep
import tkinter as tk
from core.utils.tk_utils import messagebox
from core.utils.logic_utils import threaded

import logging
logger = logging.getLogger(__name__)


class SelectAppWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        super().__init__(parent)
        self.controller = controller
        self.logic = logic_controller

        # Title Section
        title_frame = tk.Frame(self, pady=10)
        title_frame.pack(fill="x")

        label = tk.Label(
            title_frame,
            text="Select an Application to Track",
            font=("Arial", 16, "bold")
        )
        label.pack(pady=(5, 0))

        subtitle = tk.Label(
            title_frame,
            text="Ensure the application is running. Use 'Refresh List' if it does not appear.",
            font=("Arial", 11)
        )
        subtitle.pack(pady=(0, 15))

        # Search Section
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", padx=20, pady=5)

        search_label = tk.Label(search_frame, text="Search:", font=("Arial", 10))
        search_label.pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.update_search())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=8)

        refresh_button = tk.Button(
            search_frame,
            text="Refresh List",
            command=lambda: self.refresh_apps(True),
            width=12
        )
        refresh_button.pack(side="right")

        # App List Section
        card = tk.Frame(
            self,
            bd=2, relief="groove",
            padx=15, pady=15
        )
        card.pack(fill="both", expand=True, padx=20, pady=15)

        list_frame = tk.Frame(card)
        list_frame.pack(fill="both", expand=True)

        self.app_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, font=("Arial", 11))
        self.app_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.app_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.app_listbox.config(yscrollcommand=scrollbar.set)

        # Bottom Buttons
        bottom_frame = tk.Frame(self, pady=15)
        bottom_frame.pack(fill="x")

        select_button = tk.Button(
            bottom_frame,
            text="Select",
            command=self.select_app,
            width=15, height=2,
            font=("Arial", 10, "bold")
        )
        select_button.pack(side="left", padx=20)

        back_button = tk.Button(
            bottom_frame,
            text="Main Menu",
            command=lambda: (self.controller.reset_frames(),
                             self.controller.show_frame("MainWindow")),
            width=15, height=2
        )
        back_button.pack(side="right", padx=20)

        self.app_tracker = self.logic.app_tracker
        self.all_apps = []
        self.refresh_apps()  # Populate list initially

    def select_app(self):
        selected_index = self.app_listbox.curselection()
        if selected_index:
            self.controller.frames["TrackerWindow"].start_update_thread()
            selected_app = self.app_listbox.get(selected_index)
            self.app_tracker.set_selected_app(selected_app)
            self.controller.show_frame("TrackerWindow")
        else:
            messagebox.showerror("Error", "No application selected")

    @threaded
    def refresh_apps(self, filter_reset=False):
        """Fetch all app names and display them in the listbox."""
        try:
            self.app_listbox.delete(0, tk.END)
            self.all_apps = self.app_tracker.get_app_names()

            if not self.all_apps:
                logger.warning("No applications found in refresh_apps()")
            else:
                for app in self.all_apps:
                    self.app_listbox.insert(tk.END, app)
        except RuntimeError as e:
            if str(e) == "main thread is not in main loop":
                self.refresh_apps(filter_reset)
            else:
                from traceback import format_exc
                error = f"refresh_apps() runtime error:\n\n{str(e)} - {str(format_exc())}"
                messagebox.showerror("Error", error)
                logger.error(error)

    @threaded
    def update_search(self, *args):
        """Filter apps in the listbox based on search input."""
        search_text = self.search_var.get().lower()
        filtered_apps = [app for app in self.all_apps if search_text in app.lower()]

        self.app_listbox.delete(0, tk.END)
        for app in filtered_apps:
            self.app_listbox.insert(tk.END, app)
