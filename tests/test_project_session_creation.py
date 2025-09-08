import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from core.screens.create_session_window import CreateSessionWindow
from core.screens.project_sessions_window import ProjectSessionsWindow


@pytest.fixture
def mock_controller():
    """Mock the GUI controller."""
    controller = MagicMock()
    controller.get_selected_project.return_value = "Test Project"
    controller.set_selected_project = MagicMock()
    controller.show_frame = MagicMock()
    return controller


@pytest.fixture
def mock_logic_controller():
    """Mock the logic controller."""
    logic = MagicMock()
    logic.project_handler = MagicMock()
    logic.project_handler.get_projects.return_value = ["Test Project", "Another Project"]
    logic.file_handler = MagicMock()
    logic.time_tracker = MagicMock()
    logic.app_tracker = MagicMock()
    return logic


@pytest.fixture
def root_window():
    """Create a root Tkinter window for testing."""
    root = tk.Tk()
    root.withdraw()  # Hide the window during tests
    yield root
    root.destroy()


def test_create_session_window_pre_selects_project(root_window, mock_controller, mock_logic_controller):
    """Test that CreateSessionWindow pre-selects the project from controller."""
    # Create the CreateSessionWindow
    window = CreateSessionWindow(root_window, mock_controller, mock_logic_controller)
    
    # Call the check_pre_selected_project method
    window.check_pre_selected_project()
    
    # Verify the project was set correctly
    assert window.project_var.get() == "Test Project"
    assert window.no_project_var.get() == False


def test_create_session_window_no_project_default(root_window, mock_controller, mock_logic_controller):
    """Test that CreateSessionWindow sets 'No Project' checkbox as default when no project is pre-selected."""
    # Set up controller to return None for selected project
    mock_controller.get_selected_project.return_value = None
    
    # Create the CreateSessionWindow
    window = CreateSessionWindow(root_window, mock_controller, mock_logic_controller)
    
    # Call the check_pre_selected_project method
    window.check_pre_selected_project()
    
    # Verify the "No Project" checkbox is checked by default
    assert window.no_project_var.get() == True


def test_project_sessions_window_create_new_session(root_window, mock_controller, mock_logic_controller):
    """Test that ProjectSessionsWindow creates new session with correct project context."""
    # Create the ProjectSessionsWindow
    window = ProjectSessionsWindow(root_window, mock_controller, mock_logic_controller)
    
    # Call the create_new_session method
    window.create_new_session()
    
    # Verify the controller methods were called correctly
    mock_controller.get_selected_project.assert_called_once()
    mock_controller.set_selected_project.assert_called_once_with("Test Project")
    mock_controller.show_frame.assert_called_once_with("CreateSessionWindow")


def test_project_sessions_window_create_new_session_no_project(root_window, mock_controller, mock_logic_controller):
    """Test that ProjectSessionsWindow handles case when no project is selected."""
    # Set up controller to return None for selected project
    mock_controller.get_selected_project.return_value = None
    
    # Create the ProjectSessionsWindow
    window = ProjectSessionsWindow(root_window, mock_controller, mock_logic_controller)
    
    # Mock the messagebox to avoid showing actual dialog
    with patch('core.screens.project_sessions_window.messagebox') as mock_messagebox:
        # Call the create_new_session method
        window.create_new_session()
        
        # Verify error message was shown
        mock_messagebox.showerror.assert_called_once_with("Error", "No project selected")
        
        # Verify no navigation occurred
        mock_controller.show_frame.assert_not_called()
