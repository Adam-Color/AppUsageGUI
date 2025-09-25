import tkinter as tk
from core.utils.tk_utils import messagebox
from core.utils.file_utils import get_sessions, get_sessions_directory, get_session_project, get_projects
from core.utils.time_utils import format_time


class SessionsWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic = logic_controller

        # Title label
        title_label = tk.Label(self, text="Session Management", font=("Arial", 14, "bold"))
        title_label.pack(side="top", fill="x", pady=10)

        # Project filter frame
        filter_frame = tk.Frame(self)
        filter_frame.pack(side="top", fill="x", padx=20, pady=5)

        filter_label = tk.Label(filter_frame, text="Filter by Project:")
        filter_label.pack(side="left", padx=(0, 5))

        self.project_filter_var = tk.StringVar()
        self.project_filter_dropdown = tk.OptionMenu(filter_frame, self.project_filter_var, "")
        self.project_filter_dropdown.pack(side="left")

        # Load project filter options
        self.load_project_filter_options()

        # Create the frame for the listbox and scrollbar
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create the listbox
        self.session_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.session_listbox.pack(side="left", fill="both", expand=True)

        # Create the scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.session_listbox.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the listbox to use the scrollbar
        self.session_listbox.config(yscrollcommand=scrollbar.set)

        # Load sessions
        self.load_sessions()

        # Button frame
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=20, pady=10)

        # Continue button
        select_button = tk.Button(button_frame, text="Continue Session",
                                  command=self.select_session, width=20)
        select_button.pack(side="left", padx=5)

        # Analyze button
        analyze_button = tk.Button(button_frame, text="Analyze Session",
                                   command=self.analyze_session, width=20)
        analyze_button.pack(side="left", padx=5)

        # Delete button
        delete_button = tk.Button(button_frame, text="Delete Session",
                                  command=self.delete_session, width=20)
        delete_button.pack(side="left", padx=5)

        # Move button
        move_button = tk.Button(button_frame, text="Change Session's Project",
                                command=self.move_session_to_project, width=20)
        move_button.pack(side="left", padx=5)

        # Back button
        back_button = tk.Button(self, text="Main Menu",
                                command=lambda: (self.controller.reset_frames(),
                                                 self.controller.show_frame("MainWindow")))
        back_button.pack(pady=10, side="bottom")

    def load_project_filter_options(self):
        """Load available project filter options into the dropdown"""
        # Clear existing menu
        menu = self.project_filter_dropdown['menu']
        menu.delete(0, 'end')
        
        # Add "All" option first
        menu.add_command(label="All", command=lambda: self.on_filter_change("All"))
        
        # Add "No Project" option
        menu.add_command(label="No Project", command=lambda: self.on_filter_change("No Project"))
        
        # Add all available projects
        projects = get_projects()
        for project in projects:
            menu.add_command(label=project, command=lambda p=project: self.on_filter_change(p))
        
        # Set default selection to "All"
        self.project_filter_var.set("All")
        
        # Bind the dropdown change event
        self.project_filter_var.trace_add('write', lambda: self.on_filter_change(self.project_filter_var.get()))

    def on_filter_change(self, selected_filter):
        """Handle project filter dropdown change"""
        self.project_filter_var.set(selected_filter)
        self.load_sessions()

    def load_sessions(self):
        """Load session data into the listbox and 
        handle broken sessions"""

        # Clear the listbox first
        self.session_listbox.delete(0, tk.END)
        
        # Get the selected filter
        selected_filter = self.project_filter_var.get()
        
        sessions = get_sessions()
        for session in sessions:
            session_name = session.split(".")[0]
            # Determine which project this session belongs to
            project_name = get_session_project(session)
            
            # Apply filter
            if selected_filter == "All":
                # Show all sessions
                pass
            elif selected_filter == "No Project":
                # Only show sessions without projects
                if project_name is not None:
                    continue
            else:
                # Only show sessions from the selected project
                if project_name != selected_filter:
                    continue
            
            # Load data for the current session
            self.logic.file_handler.load_session_data(session_name, project_name)
            session_data = self.logic.file_handler.get_data()
            if session_data is not None:
                app_name = session_data['app_name']
                time_spent = session_data['time_spent']
                # Format the time spent
                formatted_time = format_time(int(time_spent))
                
                # Create display text with project info
                if project_name:
                    display_text = f"{session_name} [{project_name}]: {app_name}, {formatted_time} on record"
                else:
                    display_text = f"{session_name} [No Project]: {app_name}, {formatted_time} on record"
                
                # Insert into the Listbox
                self.session_listbox.insert(tk.END, display_text)
        
        # Show message if no sessions match the filter
        if self.session_listbox.size() == 0:
            if selected_filter == "All":
                self.session_listbox.insert(tk.END, "No sessions found.")
            elif selected_filter == "No Project":
                self.session_listbox.insert(tk.END, "No standalone sessions found.")
            else:
                self.session_listbox.insert(tk.END, f"No sessions found in project '{selected_filter}'.")
        
        corrupt_sessions = self.logic.file_handler.get_corrupt_sessions()
        if len(corrupt_sessions) > 0:
            error_string = "The following session(s) failed to load:\n\n"
            for session in corrupt_sessions:
                name, error = session
                error_string += "\n" + name + ": " + error
            messagebox.showerror("Session Error", error_string + f"\n\nTo fix or delete session files, go to the {get_sessions_directory()} directory\n")

    def get_session_text(self):
        selected_index = self.session_listbox.curselection()
        if selected_index:
            return self.session_listbox.get(selected_index)

    def select_session(self):
        if not self.get_session_text():
            messagebox.showerror("Error", "No session selected")
            return 0
        self.controller.frames["TrackerWindow"].start_update_thread()
        
        # Parse the display text to extract session name and app name
        display_text = self.get_session_text()
        # Format: "session_name [project]: app_name, time on record"
        parts = display_text.split(": ")
        session_part = parts[0]  # "session_name [project]"
        app_part = parts[1].split(", ")[0]  # "app_name"
        
        # Extract session name (remove project part)
        if " [" in session_part:
            selected_session_name = session_part.split(" [")[0]
        else:
            selected_session_name = session_part
        
        # Determine project for this session
        project_name = get_session_project(selected_session_name + ".dat")

        # update the logic session name var
        self.logic.file_handler.set_file_name(selected_session_name)

        # tell the controller we are continuing from a session
        self.logic.file_handler.set_continuing_session(True)

        # load selected session data into the file handler,
        # so it's ready to be pulled
        self.logic.file_handler.load_session_data(selected_session_name, project_name)

        # start/reset tracking threads
        self.logic.app_tracker.reset()
        self.logic.app_tracker.set_selected_app(app_part)
        self.logic.time_tracker.reset(add_time=self.logic.file_handler.get_data()['time_spent'])
        self.logic.time_tracker.start()
        self.logic.time_tracker.clock()

        # show the TrackerWindow
        self.controller.show_frame('TrackerWindow')

    def analyze_session(self):
        if not self.get_session_text():
            messagebox.showerror("Error", "No session selected")
            return 0
        
        # Parse the display text to extract session name
        display_text = self.get_session_text()
        parts = display_text.split(": ")
        session_part = parts[0]  # "session_name [project]"
        
        # Extract session name (remove project part)
        if " [" in session_part:
            selected_session_name = session_part.split(" [")[0]
        else:
            selected_session_name = session_part
        
        # Determine project for this session
        project_name = get_session_project(selected_session_name + ".dat")
        
        # load the session data
        self.logic.file_handler.load_session_data(selected_session_name, project_name)
        self.controller.frames['SessionTotalWindow'].total_session_time_thread.start()
        self.controller.frames['SessionTotalWindow'].update_total_time()
        # show the SessionTotalWindow
        self.controller.show_frame('SessionTotalWindow')

    def delete_session(self):
        if not self.get_session_text():
            messagebox.showerror("Error", "No session selected")
            return 0
        else:
            # Parse the display text to extract session name
            display_text = self.get_session_text()
            parts = display_text.split(": ")
            session_part = parts[0]  # "session_name [project]"
            
            # Extract session name (remove project part)
            if " [" in session_part:
                selected_session_name = session_part.split(" [")[0]
            else:
                selected_session_name = session_part
            
            # Determine project for this session
            project_name = get_session_project(selected_session_name + ".dat")
            
            # ask for confirmation
            confirm = messagebox.askyesno("Confirm Deletion",
                                             f"Are you sure you want to delete the session '{selected_session_name}'? \nThis action cannot be undone.")
            if confirm:
                self.logic.file_handler.delete_session(selected_session_name, project_name)
                # Reload sessions to refresh the filtered list
                self.load_sessions()

    def move_session_to_project(self):
        """Move the selected session to a different project"""
        if not self.get_session_text():
            messagebox.showerror("Error", "No session selected")
            return
        
        # Parse the display text to extract session name
        display_text = self.get_session_text()
        parts = display_text.split(": ")
        session_part = parts[0]  # "session_name [project]"
        
        # Extract session name (remove project part)
        if " [" in session_part:
            selected_session_name = session_part.split(" [")[0]
        else:
            selected_session_name = session_part
        
        # Determine current project for this session
        current_project = get_session_project(selected_session_name + ".dat")
        
        # Get all available projects
        available_projects = get_projects()
        
        # Create a dialog to select target project
        self.show_move_session_dialog(selected_session_name, current_project, available_projects)

    def show_move_session_dialog(self, session_name, current_project, available_projects):
        """Show dialog to select target project for moving session"""
        # Create a new window for project selection
        dialog = tk.Toplevel(self)
        dialog.title("Move Session to Project")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self)
        dialog.grab_set()
        
        # Main frame
        main_frame = tk.Frame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text=f"Move session '{session_name}' to:")
        title_label.pack(pady=(0, 10))
        
        # Current project info
        if current_project:
            current_info = tk.Label(main_frame, text=f"Current project: {current_project}")
        else:
            current_info = tk.Label(main_frame, text="Current project: No Project")
        current_info.pack(pady=(0, 10))
        
        # Project selection frame
        selection_frame = tk.Frame(main_frame)
        selection_frame.pack(fill="both", expand=True, pady=10)
        
        # Label for dropdown
        select_label = tk.Label(selection_frame, text="Select target project:")
        select_label.pack(anchor="w", pady=(0, 5))
        
        # Project selection dropdown
        self.target_project_var = tk.StringVar()
        project_dropdown = tk.OptionMenu(selection_frame, self.target_project_var, "")
        project_dropdown.pack(fill="x", pady=(0, 10))
        
        # Populate dropdown with available projects
        menu = project_dropdown['menu']
        menu.delete(0, 'end')
        
        # Add "No Project" option
        menu.add_command(label="No Project", command=lambda: self.target_project_var.set("No Project"))
        
        # Add all available projects
        for project in available_projects:
            if project != current_project:  # Don't show current project as option
                menu.add_command(label=project, command=lambda p=project: self.target_project_var.set(p))
        
        # Set default selection
        if available_projects and available_projects[0] != current_project:
            self.target_project_var.set(available_projects[0])
        else:
            self.target_project_var.set("No Project")
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Move button
        move_button = tk.Button(button_frame, text="Move Session", 
                              command=lambda: self.execute_move_session(session_name, current_project, dialog),
                              bg="lightblue", width=15)
        move_button.pack(side="left", padx=(0, 10))
        
        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel", 
                                command=dialog.destroy, width=15)
        cancel_button.pack(side="left")
        
        # Store reference to dialog for the execute function
        self.move_dialog = dialog

    def execute_move_session(self, session_name, current_project, dialog):
        """Execute the session move operation"""
        target_project = self.target_project_var.get()
        
        # Check if target is different from current
        if target_project == "No Project" and current_project is None:
            messagebox.showwarning("Warning", "Session is already in 'No Project'")
            dialog.destroy()
            return
        elif target_project == current_project:
            messagebox.showwarning("Warning", f"Session is already in project '{current_project}'")
            dialog.destroy()
            return
        
        # Confirm the move operation
        if target_project == "No Project":
            confirm_message = f"Move session '{session_name}' from project '{current_project}' to 'No Project'?"
        elif current_project is None:
            confirm_message = f"Move session '{session_name}' from 'No Project' to project '{target_project}'?"
        else:
            confirm_message = f"Move session '{session_name}' from project '{current_project}' to project '{target_project}'?"
        
        if messagebox.askyesno("Confirm Move", confirm_message):
            # Execute the move
            success = self.logic.file_handler.move_session_to_project(
                session_name, current_project, target_project
            )
            
            if success:
                messagebox.showinfo("Success", f"Session '{session_name}' moved successfully!")
                # Refresh the sessions list
                self.load_sessions()
            else:
                messagebox.showerror("Error", "Failed to move session. Please try again.")
        
        dialog.destroy()
