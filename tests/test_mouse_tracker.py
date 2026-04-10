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
def test_mouse_idle_triggers_pause(mock_controller, tracker):
    """Simulate mouse inactivity and check pause is triggered."""
    # The controller will report the same position as the tracker's current position,
    # so _check_mouse_position sees no movement and should trigger a pause.
    mock_controller.return_value.position = (100, 100)
    tracker.mouse_position = (100, 100)  # Becomes last_mouse_position inside the method
    tracker.logic.time_tracker.get_is_paused.return_value = False

    tracker._check_mouse_position()

    tracker.logic.time_tracker.pause.assert_called_once()
    assert tracker.is_pausing() is True


@patch("core.logic.user_trackers.pynput.mouse.Controller")
def test_mouse_movement_triggers_resume(mock_controller, tracker):
    """Simulate mouse movement and check resume is triggered."""
    # The controller reports a new position different from the tracker's stored one,
    # so _check_mouse_position sees movement and should trigger a resume.
    mock_controller.return_value.position = (200, 200)
    tracker.mouse_position = (100, 100)  # Becomes last_mouse_position inside the method
    tracker.pausing = True  # Simulate the tracker having already triggered a pause
    tracker.logic.time_tracker.get_is_paused.return_value = True

    tracker._check_mouse_position()

    tracker.logic.time_tracker.resume.assert_called_once()
    assert tracker.is_pausing() is False