import tkinter as tk
from core.utils.tk_utils import messagebox
import re


def validate_project_name(value):
    """Validate project name - no special characters that could cause file system issues"""
    # Allow alphanumeric, spaces, hyphens, underscores
    illegal_chars = r'[<>:"/\\|?*]'
    
    if re.search(illegal_chars, value):
        return False
    
    return True


class CreateProjectWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic = logic_controller

        # Title label
        title_label = tk.Label(self, text="Create New Project", font=("Arial", 14, "bold"))
        title_label.pack(side="top", fill="x", pady=10)

        # Project name input
        name_label = tk.Label(self, text="Project Name:")
        name_label.pack(side="top", fill="x", pady=5, padx=20)

        # Validation command
        vcmd = (self.register(validate_project_name), '%P')
        self.project_name = tk.StringVar()
        self.project_name.set("")

        # User inputs project name
        self.project_name_input = tk.Entry(self, textvariable=self.project_name,
                                         validate="key", validatecommand=vcmd)
        self.project_name_input.pack(side="top", fill="x", pady=5, padx=20)

        # Help text
        help_text = tk.Label(self, text="Project names can contain letters, numbers, spaces, hyphens, and underscores.\nSpecial characters like < > : \" / \\ | ? * are not allowed.",
                           font=("Arial", 8), fg="gray")
        help_text.pack(side="top", fill="x", pady=5, padx=20)

        # Button frame
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=20, pady=20)

        # Create project button
        create_button = tk.Button(button_frame, text="Create Project", 
                                command=self.create_project, width=15)
        create_button.pack(side="left", padx=5)

        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel", 
                                command=self.cancel, width=15)
        cancel_button.pack(side="left", padx=5)

        # Back button
        back_button = tk.Button(self, text="Back to Projects", 
                              command=lambda: self.controller.show_frame("ProjectsWindow"))
        back_button.pack(pady=10, side='bottom')

        # Bind Enter key to create project
        self.project_name_input.bind('<Return>', lambda event: self.create_project())

    def create_project(self):
        """Create a new project"""
        project_name = self.project_name.get().strip()
        
        if not project_name:
            messagebox.showerror("Error", "Please enter a project name.")
            return
        
        if len(project_name) > 50:
            messagebox.showerror("Error", "Project name must be 50 characters or less.")
            return
        
        if self.logic.project_handler.get_project_sessions(project_name) != []:
            messagebox.showerror("Error", "A project with this name already exists. Please choose a different name.")
            return
        
        if project_name.lower() == "no project":
            messagebox.showerror("Error", "The project name 'No Project' is reserved. Please choose a different name.")
            return
        
        # Create the project
        success, message = self.logic.project_handler.create_project(project_name)
        
        if success:
            messagebox.showinfo("Success", message)
            # Return to projects window
            self.controller.reset_frames()
            self.controller.show_frame("ProjectsWindow")
        else:
            print(f"Error creating project: {message}")
            messagebox.showerror("Error", message)

    def cancel(self):
        """Cancel project creation and return to projects window"""
        self.controller.show_frame("ProjectsWindow")
