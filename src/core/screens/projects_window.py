import tkinter as tk
from core.utils.tk_utils import messagebox

from core.utils.time_utils import format_time


class ProjectsWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic = logic_controller

        # Title label
        title_label = tk.Label(self, text="Project Management", font=("Arial", 14, "bold"))
        title_label.pack(side="top", fill="x", pady=10)


        # Create the frame for the listbox and scrollbar
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Create the listbox
        self.project_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.project_listbox.pack(side="left", fill="both", expand=True)

        # Create the scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.project_listbox.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the listbox to use the scrollbar
        self.project_listbox.config(yscrollcommand=scrollbar.set)

        # Load projects
        self.load_projects()

        # Button frame
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=20, pady=10)

        # Create new project button
        create_button = tk.Button(button_frame, text="Create New Project", 
                                command=self.create_project, width=20)
        create_button.pack(side="left", padx=5)


        # View sessions button
        sessions_button = tk.Button(button_frame, text="View Project Sessions", 
                                  command=self.view_sessions, width=20)
        sessions_button.pack(side="left", padx=5)

        # Delete project button
        delete_button = tk.Button(button_frame, text="Delete Project", 
                                command=self.delete_project, width=20)
        delete_button.pack(side="left", padx=5)

        # Back button
        back_button = tk.Button(self, text="Main Menu", 
                              command=lambda: (self.controller.reset_frames(), 
                                             self.controller.show_frame("MainWindow")))
        back_button.pack(pady=10, side='bottom')

        # keybinds
        self.project_listbox.bind("<Delete>", lambda e: self.delete_project())
        self.project_listbox.bind("<Return>", lambda e: self.view_sessions())


    def load_projects(self):
        """Load projects into the listbox"""
        self.project_listbox.delete(0, tk.END)
        
        # Load all projects
        projects = self.logic.project_handler.get_projects()
        
        if not projects:
            self.project_listbox.insert(tk.END, "No projects found. Create a new project to get started.")
            self.project_listbox.config(state=tk.DISABLED)
        else:
            self.project_listbox.config(state=tk.NORMAL)
            for project in projects:
                # Get project info
                project_info = self.logic.project_handler.get_project_info(project)
                session_count = project_info.get('session_count', 0) if project_info else 0
                
                # Get total time for the project
                total_time = self.logic.project_handler.get_project_total_time(project)
                formatted_time = format_time(total_time)
                
                # Format display text
                display_text = f"{project} ({session_count} sessions, Total session time: {formatted_time})"
                
                self.project_listbox.insert(tk.END, display_text)

    def get_selected_project(self):
        """Get the selected project name from the listbox"""
        selected_index = self.project_listbox.curselection()
        if selected_index:
            selected_text = self.project_listbox.get(selected_index)
            # Extract project name (remove session count and time info)
            project_name = self.extract_project_name(selected_text)
            return project_name
        return None
    
    def extract_project_name(self, listbox_text: str) -> str:
        """Extract project name from listbox entry text"""
        return listbox_text.split(' (')[0]


    def create_project(self):
        """Navigate to create project window"""
        self.controller.show_frame("CreateProjectWindow")


    def view_sessions(self):
        """View sessions for the selected project"""
        # Ensure the listbox has focus and check selection
        self.project_listbox.focus_set()
        selected_index = self.project_listbox.curselection()
        
        # Also try getting the active selection
        active_index = self.project_listbox.index(tk.ACTIVE)
        
        if not selected_index:
            # If no selection, try to use the active item
            if active_index is not None and active_index >= 0:
                selected_index = (active_index,)
            else:
                messagebox.showerror("Error", "No project selected")
                return
        
        # Get the selected text directly from the stored index
        selected_text = self.project_listbox.get(selected_index)
        
        # Extract project name (remove session count and time info)
        project_name = self.extract_project_name(selected_text)
        
        # Set the selected project in the controller and navigate to sessions
        self.logic.project_handler.set_selected_project(project_name)
        self.controller.show_frame("ProjectSessionsWindow")

    def delete_project(self):
        """Delete the selected project"""
        selected_project = self.get_selected_project()
        if not selected_project:
            messagebox.showerror("Error", "No project selected")
            return
        
        if selected_project.startswith("No projects found"):
            messagebox.showerror("Error", "No projects available")
            return

        # Confirm deletion
        session_count = self.logic.project_handler.get_project_session_count(selected_project)
        confirm_message = f"Are you sure you want to delete project '{selected_project}'?"
        if session_count > 0:
            confirm_message += f"\n\nThis will also delete {session_count} session(s) in this project."
        confirm_message += "\n\nThis action cannot be undone."
        
        if messagebox.askyesno("Confirm Deletion", confirm_message):
            success, message = self.logic.project_handler.delete_project(selected_project)
            if success:
                messagebox.showinfo("Success", message)
                self.load_projects()  # Refresh the list
            else:
                messagebox.showerror("Error", message)
