"""Handler for all file io operations. Only handles one session at a time, which should
be set by other classes.
The file handler is responsible for saving and loading session data"""

import os
import pickle
import _pickle
from datetime import datetime

from core.utils.file_utils import (
    compute_hash,
    read_file,
    write_file,
    get_sessions_directory,
    get_projects_directory,
)


class FileHandler:
    def __init__(self, parent, logic_controller):
        self.parent = parent
        self.controller = logic_controller
        self.file_name = ""
        self.current_project = None
        self.directory = get_sessions_directory()  # Keep for backward compatibility
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        self.data = None
        self.continuing_session = False
        self.continuing_tracker = False
        self.corrupt_sessions = []

    def save_session_data(self, data):
        """Special function to save and hash session data"""
        # Add project and timestamp information to data
        if self.current_project:
            data['project_name'] = self.current_project
        data['created_date'] = datetime.now().isoformat()
        data['last_modified'] = datetime.now().isoformat()
        
        self.data = pickle.dumps(data)
        
        # Determine save directory based on project
        if self.current_project:
            save_directory = os.path.join(get_projects_directory(), self.current_project)
            if not os.path.exists(save_directory):
                os.makedirs(save_directory, exist_ok=True)
        else:
            save_directory = self.directory
        
        file_path = os.path.join(save_directory, self.file_name + ".dat")
        hash_path = os.path.join(save_directory, self.file_name + ".hash")

        # Save data to file
        write_file(file_path, self.data)

        # Compute and save hash
        data_hash = compute_hash(self.data)
        write_file(hash_path, data_hash.encode("utf-8"))
        
        # Update project metadata if using projects
        if self.current_project and hasattr(self.controller, 'project_handler'):
            session_count = len(self.controller.project_handler.get_project_sessions(self.current_project))
            self.controller.project_handler.update_project_metadata(self.current_project, session_count)

    def load_session_data(self, filename, project_name=None):
        """Loads session data from file and checks hash"""
        self.file_name = filename
        
        # Determine load directory based on project
        if project_name:
            load_directory = os.path.join(get_projects_directory(), project_name)
            self.current_project = project_name
        else:
            load_directory = self.directory
        
        file_path = os.path.join(load_directory, filename + ".dat")
        hash_path = os.path.join(load_directory, filename + ".hash")

        if os.path.exists(file_path) and os.path.exists(hash_path):
            try:
                # Read data and hash
                data = read_file(file_path)
                stored_hash = read_file(hash_path).decode("utf-8")

                # Compute hash of the loaded data
                computed_hash = compute_hash(data)

                if computed_hash == stored_hash:
                    self.data = pickle.loads(data)
                    # Set current project from loaded data if not specified
                    if not project_name and isinstance(self.data, dict) and 'project_name' in self.data:
                        self.current_project = self.data['project_name']
                else:
                    self.corrupt_sessions.append((filename, "Hash mismatch"))
                    self.data = None
            except _pickle.UnpicklingError:
                self.corrupt_sessions.append((filename, "Data is corrupt"))
                self.data = None
        else:
            self.corrupt_sessions.append((filename, "No hash file found"))
            self.data = None

    def delete_session(self, filename, project_name=None):
        """Delete data and hash files of a session"""
        # Determine delete directory based on project
        if project_name:
            delete_directory = os.path.join(get_projects_directory(), project_name)
        else:
            delete_directory = self.directory
        
        file_path = os.path.join(delete_directory, filename + ".dat")
        hash_path = os.path.join(delete_directory, filename + ".hash")

        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(hash_path):
            os.remove(hash_path)
        
        # Update project metadata if using projects
        if project_name and hasattr(self.controller, 'project_handler'):
            session_count = len(self.controller.project_handler.get_project_sessions(project_name))
            self.controller.project_handler.update_project_metadata(project_name, session_count)

    def get_data(self):
        """Gets session data, and ensures the returned data is always a dictionary."""
        if isinstance(self.data, bytes):  # If data is bytes, unpickle it
            return pickle.loads(self.data)
        return self.data if isinstance(self.data, dict) else {}

    def set_file_name(self, file_name):
        if file_name is not None:
            self.file_name = file_name

    def get_file_name(self):
        return self.file_name

    def set_continuing_session(self, continuation=bool):
        self.continuing_session = continuation
        if continuation:
            self.set_continuing_tracker(True)
            self.controller.time_tracker.update_captures()

    def set_continuing_tracker(self, value):
        self.continuing_tracker = value

    def get_continuing_tracker(self):
        return self.continuing_tracker

    def get_continuing_session(self):
        return self.continuing_session

    def get_corrupt_sessions(self):
        return self.corrupt_sessions

    def set_current_project(self, project_name):
        """Set the current project for session operations"""
        self.current_project = project_name

    def get_current_project(self):
        """Get the current project"""
        return self.current_project

    def move_session_to_project(self, session_name, current_project, target_project):
        """Move a session from one project to another (or to/from No Project)"""
        try:
            # Load the session data first
            self.load_session_data(session_name, current_project)
            session_data = self.get_data()
            
            if session_data is None:
                return False
            
            # Determine source and target directories
            if current_project:
                source_dir = os.path.join(get_projects_directory(), current_project)
            else:
                source_dir = get_sessions_directory()
            
            if target_project:
                target_dir = os.path.join(get_projects_directory(), target_project)
                # Ensure target directory exists
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
            else:
                target_dir = get_sessions_directory()
                # Ensure target directory exists
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
            
            # Define file paths
            source_data_file = os.path.join(source_dir, session_name + ".dat")
            source_hash_file = os.path.join(source_dir, session_name + ".hash")
            target_data_file = os.path.join(target_dir, session_name + ".dat")
            target_hash_file = os.path.join(target_dir, session_name + ".hash")
            
            # Check if source files exist
            if not os.path.exists(source_data_file) or not os.path.exists(source_hash_file):
                return False
            
            # Check if target files already exist (shouldn't happen, but safety check)
            if os.path.exists(target_data_file) or os.path.exists(target_hash_file):
                return False
            
            # Update session data with new project information
            session_data['project_name'] = target_project
            session_data['last_modified'] = datetime.now().isoformat()
            
            # Save the updated session data to the new location
            self.current_project = target_project
            self.file_name = session_name
            self.save_session_data(session_data)
            
            # Remove the old files
            if os.path.exists(source_data_file):
                os.remove(source_data_file)
            if os.path.exists(source_hash_file):
                os.remove(source_hash_file)
            
            # Update project metadata for both projects
            if hasattr(self.controller, 'project_handler'):
                # Update source project metadata
                if current_project:
                    session_count = len(self.controller.project_handler.get_project_sessions(current_project))
                    self.controller.project_handler.update_project_metadata(current_project, session_count)
                
                # Update target project metadata
                if target_project:
                    session_count = len(self.controller.project_handler.get_project_sessions(target_project))
                    self.controller.project_handler.update_project_metadata(target_project, session_count)
            
            return True
            
        except Exception as e:
            print(f"Error moving session {session_name}: {e}")
            return False