import tkinter as tk
from tkinter import messagebox


class SelectAppWindow(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, controller)
        self.controller = controller

        label = tk.Label(self, text="Ensure the desired application is running.\n\nSelect which application you would like to track:")
        label.pack(side="top", fill="x", pady=5)
        
        # button to refresh the list
        refresh_button = tk.Button(self, text="Refresh List", command=self.refresh_apps)
        refresh_button.pack(pady=10)


        # create the frame for the listbox and scrollbar
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True)

        # create the listbox
        self.app_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.app_listbox.pack(side="left", fill="both", expand=True)

        # create the scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.app_listbox.yview)
        scrollbar.pack(side="right", fill="y")

        # configure the listbox to use the scrollbar
        self.app_listbox.config(yscrollcommand=scrollbar.set)

        #TODO: add a search function
        # populate the listbox with test application names
        apps = ["Test 1", "Test 2", "Test 3", "Test 4", "Test 5"]

        self.tracker = self.controller.tracker
        thread, _ = self.tracker.update_app_names()
        thread.join()
        apps = self.tracker.get_app_names()
        for app in apps:
            self.app_listbox.insert(tk.END, app)
        
        # button to make the selection
        select_button = tk.Button(self, text="Select", command=self.select_app)
        select_button.pack(pady=10)
    
    def select_app(self):
        selected_index = self.app_listbox.curselection()
        if selected_index:
            selected_app = self.app_listbox.get(selected_index)

            # handle the selected application
            self.controller.show_frame("TrackerWindow")
            self.tracker.set_selected_app(selected_app)
        else:
            messagebox.showerror("Error","No application selected")

    def refresh_apps(self):
        self.app_listbox.delete(0, tk.END)
        thread, _ = self.tracker.update_app_names()
        thread.join()  # Wait for the thread to complete
        result = self.tracker.get_app_names()
        app_names = result if result else []
        
        if not app_names:
            messagebox.showerror("Error", "No applications found.")
        else:
            for app in app_names:
                self.app_listbox.insert(tk.END, app)
