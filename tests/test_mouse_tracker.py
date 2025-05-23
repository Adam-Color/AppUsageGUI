import pytest
from unittest.mock import MagicMock, patch
from core.logic.user_trackers import MouseTracker


@pytest.fixture
def mock_logic_controller():
    """Mock the logic controller with a mock time tracker."""
    mock = MagicMock()
    mock.time_tracker.get_is_paused.return_value = False
    return mock


@pytest.fixture
def tracker(mock_logic_controller):
    """Create a MouseTracker instance with mocked dependencies."""
    tracker = MouseTracker(parent=None, logic_controller=mock_logic_controller)
    tracker.enabled = True
    tracker.idle_time_limit = 1  # Short delay for testing
    return tracker


@patch("core.logic.user_trackers.pynput.mouse.Controller")
@patch("time.sleep", return_value=None)  # Skip actual sleep
def test_mouse_idle_triggers_pause(mock_sleep, mock_controller, tracker):
    """Simulate mouse inactivity and check pause is triggered."""
    # Setup fake mouse positions
    mock_controller.return_value.position = (100, 100)

    # Run one iteration of the loop manually
    tracker.last_mouse_position = (100, 100)
    tracker.mouse_position = (100, 100)
    tracker.logic.time_tracker.get_is_paused.return_value = False

    tracker._update_mouse_position()  # Normally private; tested for now

    # Check pause was called
    tracker.logic.time_tracker.pause.assert_called_once()
    assert tracker.is_pausing() is True


@patch("core.logic.user_trackers.pynput.mouse.Controller")
@patch("time.sleep", return_value=None)
def test_mouse_movement_triggers_resume(mock_sleep, mock_controller, tracker):
    """Simulate mouse movement and check resume is triggered."""
    tracker.last_mouse_position = (100, 100)
    mock_controller.return_value.position = (200, 200)

    tracker.logic.time_tracker.get_is_paused.return_value = True

    tracker._update_mouse_position()

    tracker.logic.time_tracker.resume
