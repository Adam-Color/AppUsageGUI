import tkinter as tk
from core.utils.tk_utils import messagebox
from re import search as re

from core.utils.time_utils import format_time
from core.utils.file_utils import config_file, read_file

from _version import __version__

def validate_name(value):
    """Check if name is valid for saving as a file"""
    if value == "":  # Allow empty string (for backspace)
        return True

    # Check for illegal characters
    illegal_chars = r'[<>:"/\\|?*\x00-\x1F.]'
    if re(illegal_chars, value):
        return False

    return True

class CreateSessionWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic = logic_controller

        # Title label
        title_label = tk.Label(self, text="Create New Session", font=("Arial", 14, "bold"))
        title_label.pack(side="top", fill="x", pady=10)

        # No Project checkbox
        self.no_project_var = tk.BooleanVar()
        self.no_project_checkbox = tk.Checkbutton(self, text="No Project (standalone session)", 
                                                 variable=self.no_project_var,
                                                 command=self.on_no_project_toggle)
        self.no_project_checkbox.pack(side="top", fill="x", pady=5, padx=20)

        # Project selection frame
        project_frame = tk.Frame(self)
        project_frame.pack(side="top", fill="x", pady=5, padx=20)
        
        # Project label
        self.project_label = tk.Label(project_frame, text="Project:")
        self.project_label.pack(side="left")
        
        # Project dropdown
        self.project_var = tk.StringVar()
        self.project_dropdown = tk.OptionMenu(project_frame, self.project_var, "")
        self.project_dropdown.pack(side="left", fill="x", expand=True, padx=(10, 5))
        
        # Create new project button
        self.create_project_button = tk.Button(project_frame, text="Create New Project", 
                                             command=self.create_new_project, width=15, height=1)
        self.create_project_button.pack(side="right", padx=(5, 0))
        
        # Load projects into dropdown
        self.load_projects()
        
        # Check if there's a pre-selected project from the controller
        self.check_pre_selected_project()

        # Session name input
        name_label = tk.Label(self, text="Session Name:")
        name_label.pack(side="top", fill="x", pady=5, padx=20)

        vcmd = (self.register(validate_name), '%P')
        self.session_name = tk.StringVar()
        self.session_name.set("")

        # User inputs session name
        self.session_name_input = tk.Entry(self, textvariable=self.session_name,
                                            validate="key", validatecommand=vcmd)
        self.session_name_input.pack(side="top", fill="x", pady=5, padx=20)

        # Button frame
        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=20, pady=20)

        # Confirm session name entry
        confirm_button = tk.Button(button_frame, text="Create Session", command=self.on_confirm, width=15, height=1)
        confirm_button.pack(side="left", padx=5)

        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel", command=self.cancel, width=15, height=1)
        cancel_button.pack(side="left", padx=5)

        back_button = tk.Button(self, text="Main Menu", command=lambda: (self.controller.reset_frames(), self.controller.show_frame("MainWindow")), height=1)
        back_button.pack(pady=5, side='bottom')

        # Bind Enter key to confirm
        self.session_name_input.bind('<Return>', lambda event: self.on_confirm())

    def load_projects(self):
        """Load available projects into the dropdown"""
        projects = self.logic.project_handler.get_projects()
        
        # Clear existing menu
        menu = self.project_dropdown['menu']
        menu.delete(0, 'end')
        
        
        # Add projects to menu
        for project in projects:
            menu.add_command(label=project, command=lambda p=project: self.project_var.set(p))
        
        # Set default selection
        if projects:
            self.project_var.set(projects[0])

    def check_pre_selected_project(self):
        """Check if there's a pre-selected project from the controller and set it"""
        selected_project = self.controller.get_selected_project()
        if selected_project:
            # Set the project in the dropdown
            self.project_var.set(selected_project)
            # Disable the "No Project" checkbox since we have a specific project
            self.no_project_var.set(False)
            self.on_no_project_toggle()  # This will enable the project dropdown
        else:
            # No pre-selected project - set "No Project" checkbox as checked by default
            self.no_project_var.set(True)
            self.on_no_project_toggle()  # This will disable the project dropdown

    def on_no_project_toggle(self):
        """Handle No Project checkbox toggle"""
        if self.no_project_var.get():
            # Disable project selection
            self.project_dropdown.config(state="disabled")
            self.project_label.config(fg="gray")
            self.create_project_button.config(state="disabled")
            self.project_var.set("")
        else:
            # Enable project selection
            self.project_dropdown.config(state="normal")
            self.project_label.config(fg="black")
            self.create_project_button.config(state="normal")
            # Reload projects and set default
            self.load_projects()

    def create_new_project(self):
        """Open a dialog to create a new project and associate it with the session"""
        # Create a simple dialog for project creation
        dialog = tk.Toplevel(self)
        dialog.title("Create New Project")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        title_label = tk.Label(dialog, text="Create New Project", font=("Arial", 12, "bold"))
        title_label.pack(pady=10)
        
        # Project name input
        name_label = tk.Label(dialog, text="Project Name:")
        name_label.pack(pady=5)
        
        # Validation command
        vcmd = (dialog.register(validate_name), '%P')
        project_name_var = tk.StringVar()
        project_name_entry = tk.Entry(dialog, textvariable=project_name_var, 
                                    validate="key", validatecommand=vcmd, width=30)
        project_name_entry.pack(pady=5)
        
        # Help text
        help_text = tk.Label(dialog, text="Project names can contain letters, numbers, spaces, hyphens, and underscores.\nSpecial characters like < > : \" / \\ | ? * are not allowed.",
                           font=("Arial", 8), fg="gray")
        help_text.pack(pady=5)
        
        # Button frame
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20, padx=20)
        
        def create_and_select():
            """Create the project and select it in the dropdown"""
            project_name = project_name_var.get().strip()
            
            if not project_name:
                messagebox.showerror("Error", "Please enter a project name.", parent=dialog)
                return
            
            if len(project_name) > 50:
                messagebox.showerror("Error", "Project name must be 50 characters or less.", parent=dialog)
                return
            
            # Create the project
            success, message = self.logic.project_handler.create_project(project_name)
            
            if success:
                messagebox.showinfo("Success", message, parent=dialog)
                # Reload projects and select the new one
                self.load_projects()
                self.project_var.set(project_name)
                dialog.destroy()
            else:
                messagebox.showerror("Error", message, parent=dialog)
        
        # Create button
        create_button = tk.Button(button_frame, text="Create Project", 
                                command=create_and_select, width=15, height=1)
        create_button.pack(side="left", padx=(0, 10))
        
        # Cancel button
        cancel_button = tk.Button(button_frame, text="Cancel", 
                                command=dialog.destroy, width=15, height=1)
        cancel_button.pack(side="left", padx=(0, 0))
        
        # Bind Enter key to create project
        project_name_entry.bind('<Return>', lambda event: create_and_select())
        
        # Focus on the entry field
        project_name_entry.focus_set()

    def on_confirm(self):
        """Sets up session and proceeds to app selection"""
        session_name = self.session_name.get().strip()
        project_name = self.project_var.get()
        
        if not session_name:
            messagebox.showerror("Error", "Please enter a session name.")
            return
        
        # Check if No Project is selected or if project is required
        if not self.no_project_var.get() and not project_name:
            messagebox.showerror("Error", "Please select a project or check 'No Project'.")
            return
        
        # Set the session name and project for this session
        if self.no_project_var.get():
            # No project - set to None for standalone session
            self.logic.file_handler.set_current_project(None)
        else:
            # Use selected project
            self.logic.file_handler.set_current_project(project_name)
        
        self.logic.file_handler.set_file_name(session_name)
        
        # Reset trackers for new session
        self.logic.time_tracker.reset()
        self.logic.app_tracker.reset()
        
        # Proceed to app selection
        self.controller.show_frame("SelectAppWindow")

    def cancel(self):
        """Cancel session creation"""
        self.controller.show_frame("MainWindow")

