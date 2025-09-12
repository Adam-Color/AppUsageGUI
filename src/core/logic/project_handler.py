"""Handler for project management operations. Manages project creation, deletion,
and session organization within projects."""

import os
import json
from datetime import datetime

from core.utils.file_utils import get_projects_directory


class ProjectHandler:
    def __init__(self, parent, logic_controller):
        self.parent = parent
        self.controller = logic_controller
        self.current_project = None
        self.projects_directory = get_projects_directory()
        self.projects_metadata_file = os.path.join(self.projects_directory, "projects_metadata.json")
        
        # Ensure projects directory exists
        if not os.path.exists(self.projects_directory):
            os.makedirs(self.projects_directory, exist_ok=True)
        
        # Initialize projects metadata if it doesn't exist
        self._initialize_metadata()

    def _initialize_metadata(self):
        """Initialize projects metadata file if it doesn't exist"""
        if not os.path.exists(self.projects_metadata_file):
            metadata = {
                "projects": {}
            }
            self._save_metadata(metadata)

    def _load_metadata(self):
        """Load projects metadata from file"""
        try:
            with open(self.projects_metadata_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"projects": {}}

    def _save_metadata(self, metadata):
        """Save projects metadata to file"""
        with open(self.projects_metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def create_project(self, project_name):
        """Create a new project directory and metadata"""
        if not project_name or not project_name.strip():
            return False, "Project name cannot be empty"
        
        project_name = project_name.strip()
        
        # Check if project already exists
        if self.project_exists(project_name):
            return False, f"Project '{project_name}' already exists"
        
        # Create project directory
        project_dir = os.path.join(self.projects_directory, project_name)
        try:
            os.makedirs(project_dir, exist_ok=True)
        except OSError as e:
            return False, f"Failed to create project directory: {str(e)}"
        
        # Update metadata
        metadata = self._load_metadata()
        metadata["projects"][project_name] = {
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "session_count": 0
        }
        self._save_metadata(metadata)
        
        return True, f"Project '{project_name}' created successfully"

    def delete_project(self, project_name):
        """Delete a project and all its sessions"""
        if not self.project_exists(project_name):
            return False, f"Project '{project_name}' does not exist"
        
        
        # Remove project directory and all contents
        project_dir = os.path.join(self.projects_directory, project_name)
        try:
            import shutil
            shutil.rmtree(project_dir)
        except OSError as e:
            return False, f"Failed to delete project directory: {str(e)}"
        
        # Update metadata
        metadata = self._load_metadata()
        if project_name in metadata["projects"]:
            del metadata["projects"][project_name]
        self._save_metadata(metadata)
        
        return True, f"Project '{project_name}' deleted successfully"

    def get_projects(self):
        """Get list of all available projects"""
        metadata = self._load_metadata()
        return list(metadata["projects"].keys())

    def project_exists(self, project_name):
        """Check if a project exists"""
        project_dir = os.path.join(self.projects_directory, project_name)
        return os.path.exists(project_dir)

    def set_current_project(self, project_name):
        """Set the current active project"""
        if self.project_exists(project_name):
            self.current_project = project_name
            return True
        return False

    def get_current_project(self):
        """Get the current active project"""
        return self.current_project

    def get_project_directory(self, project_name):
        """Get the directory path for a project"""
        return os.path.join(self.projects_directory, project_name)

    def get_project_sessions(self, project_name):
        """Get list of session files for a project"""
        project_dir = self.get_project_directory(project_name)
        if not os.path.exists(project_dir):
            return []
        
        sessions = []
        for file in os.listdir(project_dir):
            if file.endswith('.dat'):
                sessions.append(file)
        return sessions

    def get_project_session_count(self, project_name):
        """Get the number of sessions in a project"""
        return len(self.get_project_sessions(project_name))

    def update_project_metadata(self, project_name, session_count=None):
        """Update project metadata"""
        metadata = self._load_metadata()
        if project_name in metadata["projects"]:
            metadata["projects"][project_name]["last_modified"] = datetime.now().isoformat()
            if session_count is not None:
                metadata["projects"][project_name]["session_count"] = session_count
            self._save_metadata(metadata)

    def get_project_info(self, project_name):
        """Get detailed information about a project"""
        metadata = self._load_metadata()
        if project_name in metadata["projects"]:
            project_info = metadata["projects"][project_name].copy()
            project_info["session_count"] = self.get_project_session_count(project_name)
            return project_info
        return None

    def get_project_total_time(self, project_name):
        """Get the total time from all sessions in a project"""
        if not self.project_exists(project_name):
            return 0.0
        
        total_time = 0.0
        project_dir = self.get_project_directory(project_name)
        
        # Get all session files in the project directory
        for file in os.listdir(project_dir):
            if file.endswith('.dat'):
                session_file = file[:-4]  # Remove .dat extension
                try:
                    # Load session data to get time_spent
                    self.controller.file_handler.load_session_data(session_file, project_name)
                    session_data = self.controller.file_handler.get_data()
                    
                    if isinstance(session_data, dict) and 'time_spent' in session_data:
                        total_time += session_data['time_spent']
                except Exception as e:
                    # Skip corrupted or invalid session files
                    print(f"Warning: Could not load session {session_file}: {e}")
                    continue
        
        return total_time
