"""Test cases for moving sessions between projects"""

import os
import tempfile
import shutil
import unittest
from unittest.mock import Mock, patch

# Add the src directory to the path so we can import our modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.logic.file_handler import FileHandler
from core.utils.file_utils import get_sessions_directory, get_projects_directory


class TestMoveSessionToProject(unittest.TestCase):
    """Test cases for the move_session_to_project functionality"""
    
    def setUp(self):
        """Set up test environment"""
        # Create temporary directories for testing
        self.temp_dir = tempfile.mkdtemp()
        self.sessions_dir = os.path.join(self.temp_dir, 'Sessions')
        self.projects_dir = os.path.join(self.temp_dir, 'Projects')
        
        # Create directories
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.projects_dir, exist_ok=True)
        
        # Mock the directory functions
        self.sessions_patcher = patch('core.utils.file_utils.get_sessions_directory')
        self.projects_patcher = patch('core.utils.file_utils.get_projects_directory')
        
        self.mock_sessions_dir = self.sessions_patcher.start()
        self.mock_projects_dir = self.projects_patcher.start()
        
        self.mock_sessions_dir.return_value = self.sessions_dir
        self.mock_projects_dir.return_value = self.projects_dir
        
        # Create mock controller
        self.mock_controller = Mock()
        self.mock_controller.project_handler = Mock()
        self.mock_controller.project_handler.get_project_sessions.return_value = []
        self.mock_controller.project_handler.update_project_metadata = Mock()
        
        # Create file handler
        self.file_handler = FileHandler(None, self.mock_controller)
        
        # Create test session data
        self.test_session_data = {
            'app_name': 'TestApp',
            'time_spent': 3600,  # 1 hour
            'time_captures': {
                'starts': [1000],
                'stops': [4600],
                'pauses': []
            },
            'project_name': None,
            'created_date': '2024-01-01T00:00:00',
            'last_modified': '2024-01-01T00:00:00'
        }
    
    def tearDown(self):
        """Clean up test environment"""
        self.sessions_patcher.stop()
        self.projects_patcher.stop()
        shutil.rmtree(self.temp_dir)
    
    def test_move_session_from_no_project_to_project(self):
        """Test moving a session from No Project to a specific project"""
        # Create a test session in the sessions directory (No Project)
        session_name = "test_session"
        session_file = os.path.join(self.sessions_dir, session_name + ".dat")
        hash_file = os.path.join(self.sessions_dir, session_name + ".hash")
        
        # Save test session data
        import pickle
        with open(session_file, 'wb') as f:
            pickle.dump(self.test_session_data, f)
        
        # Create a simple hash file
        with open(hash_file, 'wb') as f:
            f.write(b"test_hash")
        
        # Create target project directory
        project_name = "TestProject"
        project_dir = os.path.join(self.projects_dir, project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        # Move the session
        result = self.file_handler.move_session_to_project(session_name, None, project_name)
        
        # Verify the move was successful
        self.assertTrue(result)
        
        # Verify the session was moved to the project directory
        new_session_file = os.path.join(project_dir, session_name + ".dat")
        new_hash_file = os.path.join(project_dir, session_name + ".hash")
        
        self.assertTrue(os.path.exists(new_session_file))
        self.assertTrue(os.path.exists(new_hash_file))
        
        # Verify the old files were removed
        self.assertFalse(os.path.exists(session_file))
        self.assertFalse(os.path.exists(hash_file))
        
        # Verify project metadata was updated
        self.mock_controller.project_handler.update_project_metadata.assert_called()
    
    def test_move_session_from_project_to_no_project(self):
        """Test moving a session from a project to No Project"""
        # Create a test project and session
        project_name = "TestProject"
        project_dir = os.path.join(self.projects_dir, project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        session_name = "test_session"
        session_file = os.path.join(project_dir, session_name + ".dat")
        hash_file = os.path.join(project_dir, session_name + ".hash")
        
        # Update session data to include project
        session_data = self.test_session_data.copy()
        session_data['project_name'] = project_name
        
        # Save test session data
        import pickle
        with open(session_file, 'wb') as f:
            pickle.dump(session_data, f)
        
        # Create a simple hash file
        with open(hash_file, 'wb') as f:
            f.write(b"test_hash")
        
        # Move the session to No Project
        result = self.file_handler.move_session_to_project(session_name, project_name, None)
        
        # Verify the move was successful
        self.assertTrue(result)
        
        # Verify the session was moved to the sessions directory
        new_session_file = os.path.join(self.sessions_dir, session_name + ".dat")
        new_hash_file = os.path.join(self.sessions_dir, session_name + ".hash")
        
        self.assertTrue(os.path.exists(new_session_file))
        self.assertTrue(os.path.exists(new_hash_file))
        
        # Verify the old files were removed
        self.assertFalse(os.path.exists(session_file))
        self.assertFalse(os.path.exists(hash_file))
    
    def test_move_session_between_projects(self):
        """Test moving a session from one project to another"""
        # Create source project and session
        source_project = "SourceProject"
        source_dir = os.path.join(self.projects_dir, source_project)
        os.makedirs(source_dir, exist_ok=True)
        
        session_name = "test_session"
        session_file = os.path.join(source_dir, session_name + ".dat")
        hash_file = os.path.join(source_dir, session_name + ".hash")
        
        # Update session data to include project
        session_data = self.test_session_data.copy()
        session_data['project_name'] = source_project
        
        # Save test session data
        import pickle
        with open(session_file, 'wb') as f:
            pickle.dump(session_data, f)
        
        # Create a simple hash file
        with open(hash_file, 'wb') as f:
            f.write(b"test_hash")
        
        # Create target project
        target_project = "TargetProject"
        target_dir = os.path.join(self.projects_dir, target_project)
        os.makedirs(target_dir, exist_ok=True)
        
        # Move the session
        result = self.file_handler.move_session_to_project(session_name, source_project, target_project)
        
        # Verify the move was successful
        self.assertTrue(result)
        
        # Verify the session was moved to the target project directory
        new_session_file = os.path.join(target_dir, session_name + ".dat")
        new_hash_file = os.path.join(target_dir, session_name + ".hash")
        
        self.assertTrue(os.path.exists(new_session_file))
        self.assertTrue(os.path.exists(new_hash_file))
        
        # Verify the old files were removed
        self.assertFalse(os.path.exists(session_file))
        self.assertFalse(os.path.exists(hash_file))
    
    def test_move_nonexistent_session(self):
        """Test moving a session that doesn't exist"""
        result = self.file_handler.move_session_to_project("nonexistent_session", None, "TestProject")
        self.assertFalse(result)
    
    def test_move_session_to_same_project(self):
        """Test moving a session to the same project (should be handled by UI validation)"""
        # This test verifies the backend handles the case gracefully
        project_name = "TestProject"
        project_dir = os.path.join(self.projects_dir, project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        session_name = "test_session"
        session_file = os.path.join(project_dir, session_name + ".dat")
        hash_file = os.path.join(project_dir, session_name + ".hash")
        
        # Update session data to include project
        session_data = self.test_session_data.copy()
        session_data['project_name'] = project_name
        
        # Save test session data
        import pickle
        with open(session_file, 'wb') as f:
            pickle.dump(session_data, f)
        
        # Create a simple hash file
        with open(hash_file, 'wb') as f:
            f.write(b"test_hash")
        
        # Try to move to the same project
        result = self.file_handler.move_session_to_project(session_name, project_name, project_name)
        
        # The backend should handle this gracefully (though UI should prevent it)
        # For now, we expect it to succeed but not actually move anything
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
