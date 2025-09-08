import tkinter as tk
from core.utils.tk_utils import messagebox

from core.utils.file_utils import get_project_sessions
from core.utils.file_utils import get_projects_directory
from core.utils.time_utils import format_time


class ProjectSessionsWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic = logic_controller

        # Title label with current project
        self.title_label = tk.Label(self, text="Sessions", font=("Arial", 14, "bold"))
        self.title_label.pack(side="top", fill="x", pady=5)

        # Current project display
        self.current_project_label = tk.Label(self, text="", font=("Arial", 10), fg="blue")
        self.current_project_label.pack(side="top", fill="x", pady=5)

        # Create the frame for the listbox and scrollbar
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True)

        # Create the listbox
        self.session_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.session_listbox.pack(side="left", fill="both", expand=True)

        # Create the scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.session_listbox.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the listbox to use the scrollbar
        self.session_listbox.config(yscrollcommand=scrollbar.set)

        # Don't load sessions here - they'll be loaded when the window is shown

        # Button frame
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=20, pady=10)

        # New session button
        new_session_button = tk.Button(button_frame, text="New Session", 
                                     command=self.create_new_session, width=20)
        new_session_button.pack(side="left", padx=5)

        # Continue session button
        continue_button = tk.Button(button_frame, text="Continue Session", 
                                  command=self.continue_session, width=20)
        continue_button.pack(side="left", padx=5)

        # Analyze session button
        analyze_button = tk.Button(button_frame, text="Analyze Session", 
                                 command=self.analyze_session, width=20)
        analyze_button.pack(side="left", padx=5)

        # Delete session button
        delete_button = tk.Button(button_frame, text="Delete Session", 
                                command=self.delete_session, width=20)
        delete_button.pack(side="left", padx=5)

        # Back to projects button
        back_button = tk.Button(self, text="Back to Projects", 
                              command=lambda: self.controller.show_frame("ProjectsWindow"))
        back_button.pack(pady=5, side='bottom')

    def load_sessions(self):
        """Load session data into the listbox and handle broken sessions"""
        # Clear the listbox
        self.session_listbox.delete(0, tk.END)
        
        # Get selected project from controller
        selected_project = self.controller.get_selected_project()
        
        if selected_project:
            self.title_label.config(text=f'"{selected_project}" sessions')
            self.current_project_label.config(text=f"Project: {selected_project}")
        else:
            self.title_label.config(text="Sessions")
            self.current_project_label.config(text="No project selected")
            self.session_listbox.insert(tk.END, "No project selected. Please select a project first.")
            return

        # Get sessions for selected project
        sessions = get_project_sessions(selected_project)
        
        if not sessions:
            self.session_listbox.insert(tk.END, f"No sessions found in project '{selected_project}'.")
            return

        for session in sessions:
            session_name = session.split(".")[0]
            # Load data for the current session
            self.logic.file_handler.load_session_data(session_name, selected_project)
            session_data = self.logic.file_handler.get_data()
            
            if session_data is not None:
                app_name = session_data.get('app_name', 'Unknown')
                time_spent = session_data.get('time_spent', 0)
                created_date = session_data.get('created_date', 'Unknown')
                
                # Format the time spent
                formatted_time = format_time(int(time_spent))
                
                # Format created date
                if created_date != 'Unknown':
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(created_date)
                        formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        formatted_date = created_date
                else:
                    formatted_date = "Unknown date"
                
                # Insert into the Listbox
                display_text = f"{session_name}: {app_name}, {formatted_time} ({formatted_date})"
                self.session_listbox.insert(tk.END, display_text)
        
        # Check for corrupt sessions
        corrupt_sessions = self.logic.file_handler.get_corrupt_sessions()
        if len(corrupt_sessions) > 0:
            error_string = "The following session(s) failed to load:\n\n"
            for session in corrupt_sessions:
                name, error = session
                error_string += f"{name}: {error}\n"
            error_string += f"\nTo fix or delete session files, go to the {get_projects_directory()} directory"
            messagebox.showerror("Session Error", error_string)

    def get_session_text(self):
        """Get the selected session text from the listbox"""
        selected_index = self.session_listbox.curselection()
        if selected_index:
            return self.session_listbox.get(selected_index)
        return None

    def create_new_session(self):
        """Create a new session for the current project"""
        selected_project = self.controller.get_selected_project()
        
        if not selected_project:
            messagebox.showerror("Error", "No project selected")
            return
        
        # Set the project context for the CreateSessionWindow
        self.controller.set_selected_project(selected_project)
        
        # Navigate to CreateSessionWindow with project pre-selected
        self.controller.show_frame("CreateSessionWindow")

    def continue_session(self):
        """Continue from the selected session"""
        if not self.get_session_text():
            messagebox.showerror("Error", "No session selected")
            return
        
        # Parse session information
        session_text = self.get_session_text()
        selected_app_name = session_text.split(": ")[1].split(", ")[0]
        selected_session_name = session_text.split(": ")[0]

        # Update the logic session name var
        self.logic.file_handler.set_file_name(selected_session_name)

        # Tell the controller we are continuing from a session
        self.logic.file_handler.set_continuing_session(True)

        # Load selected session data into the file handler
        selected_project = self.controller.get_selected_project()
        self.logic.file_handler.load_session_data(selected_session_name, selected_project)

        # Start/reset tracking threads
        self.logic.app_tracker.reset()
        self.logic.app_tracker.set_selected_app(selected_app_name)
        self.logic.time_tracker.reset(add_time=self.logic.file_handler.get_data()['time_spent'])
        self.logic.time_tracker.start()
        self.logic.time_tracker.clock()

        # Start the update thread for the tracker window
        self.controller.frames["TrackerWindow"].start_update_thread()

        # Show the TrackerWindow
        self.controller.show_frame('TrackerWindow')

    def analyze_session(self):
        """Analyze the selected session"""
        if not self.get_session_text():
            messagebox.showerror("Error", "No session selected")
            return
        
        # Parse session information
        session_text = self.get_session_text()
        selected_session_name = session_text.split(": ")[0]
        
        # Load the session data
        selected_project = self.controller.get_selected_project()
        self.logic.file_handler.load_session_data(selected_session_name, selected_project)
        
        # Start session total window
        self.controller.frames['SessionTotalWindow'].total_session_time_thread.start()
        self.controller.frames['SessionTotalWindow'].update_total_time()
        
        # Show the SessionTotalWindow
        self.controller.show_frame('SessionTotalWindow')

    def delete_session(self):
        """Delete the selected session"""
        if not self.get_session_text():
            messagebox.showerror("Error", "No session selected")
            return
        
        # Parse session information
        session_text = self.get_session_text()
        selected_session_name = session_text.split(": ")[0]
        
        # Ask for confirmation
        confirm = messagebox.askyesno("Confirm Deletion",
                                     f"Are you sure you want to delete the session '{selected_session_name}'?\n"
                                     f"This action cannot be undone.")
        if confirm:
            selected_project = self.controller.get_selected_project()
            self.logic.file_handler.delete_session(selected_session_name, selected_project)
            
            # Remove from listbox
            selected_index = self.session_listbox.curselection()
            if selected_index:
                self.session_listbox.delete(selected_index)
            
            # Refresh the list
            self.load_sessions()
