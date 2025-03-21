import tkinter as tk
from tkinter import messagebox
import time
import threading

def threaded(fn):
    def wrapper(*args, **kwargs):
        result = []
        def run_and_capture():
            result.append(fn(*args, **kwargs))
        thread = threading.Thread(target=run_and_capture)
        thread.start()
        return thread, result
    return wrapper

class SelectAppWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic_controller = logic_controller

        label = tk.Label(self, text="Ensure the desired application is running.\n\nSelect which application you would like to track:")
        label.pack(side="top", fill="x", pady=5)
        
        # Search entry
        search_label = tk.Label(self, text="Search:")
        search_label.pack(pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_search)  # Update list as user types
        search_entry = tk.Entry(self, textvariable=self.search_var)
        search_entry.pack(pady=5)

        # Button to refresh the list
        refresh_button = tk.Button(self, text="Refresh List", command=self.refresh_apps)
        refresh_button.pack(pady=10)

        # Frame for listbox and scrollbar
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True)

        # Create the listbox
        self.app_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.app_listbox.pack(side="left", fill="both", expand=True)

        # Scrollbar for listbox
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.app_listbox.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure listbox to use scrollbar
        self.app_listbox.config(yscrollcommand=scrollbar.set)

        # Track the apps and filtered apps
        self.app_tracker = self.logic_controller.app_tracker
        self.all_apps = []  # Store all apps to filter through
        self.refresh_apps()  # Populate list initially
        
        # Button to make selection
        select_button = tk.Button(self, text="Select", command=self.select_app)
        select_button.pack(pady=10)

        back_button = tk.Button(self, text="Main Menu", command=lambda: (self.controller.reset_frames(), self.controller.show_frame("MainWindow")))
        back_button.pack(pady=5, side='bottom')
    
    def select_app(self):
        selected_index = self.app_listbox.curselection()
        if selected_index:
            selected_app = self.app_listbox.get(selected_index)
            self.controller.show_frame("TrackerWindow")
            self.app_tracker.set_selected_app(selected_app)
        else:
            messagebox.showerror("Error", "No application selected")

    @threaded
    def refresh_apps(self):
        """Fetch all app names and display them in the listbox."""
        self.app_listbox.delete(0, tk.END)
        time.sleep(1)
        self.all_apps = self.app_tracker.get_app_names()

        if not self.all_apps:
            messagebox.showerror("Error", "No applications found.")
        else:
            for app in self.all_apps:
                self.app_listbox.insert(tk.END, app)
        self.update_search()

    @threaded
    def update_search(self, *args):
        """Filter apps in the listbox based on search input."""
        search_text = self.search_var.get().lower()
        filtered_apps = [app for app in self.all_apps if search_text in app.lower()]

        self.app_listbox.delete(0, tk.END)  # Clear the listbox
        for app in filtered_apps:
            self.app_listbox.insert(tk.END, app)
