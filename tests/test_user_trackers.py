import unittest
from unittest.mock import patch, MagicMock
import threading
import pyautogui

# Add the project root directory to the Python path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.core.logic.user_trackers import MouseTracker

class TestMouseTracker(unittest.TestCase):
    def setUp(self):
        self.parent_mock = MagicMock()
        self.logic_controller_mock = MagicMock()
        self.input_tracker = MouseTracker(self.parent_mock, self.logic_controller_mock)

    def test_input_tracker_initialization(self):
        self.assertIsInstance(self.input_tracker, MouseTracker)
        self.assertEqual(self.input_tracker.parent, self.parent_mock)
        self.assertEqual(self.input_tracker.logic_controller, self.logic_controller_mock)
        self.assertEqual(self.input_tracker.idle_time_limit, 30)

    @patch('threading.Event')
    @patch('pyautogui.position')
    @patch('pyautogui.position')

    def test_track_input_movement(self, mock_event, mock_position, mock_thread):
        # Set up mock return values for input position
        mock_position.side_effect = [(0, 0), (10, 10), (20, 20)]

        # Mock the Event.wait method
        mock_wait = MagicMock()
        mock_event.return_value.wait = mock_wait
        mock_wait.side_effect = [False, False, True]  # Return False twice, then True to stop the loop

        # Mock the Thread.start method
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        # Set the idle time limit
        self.input_tracker.set_idle_time_limit(5)

        # Start tracking
        self.input_tracker.start_tracking()

        for _ in range(3):
            print(self.input_tracker.get_last_input_position())
            print(self.input_tracker.get_input_position())

        # Check if wait was called with the expected duration
        expected_wait_duration = 30  # The default idle_time_limit
        mock_wait.assert_has_calls([
            unittest.mock.call(timeout=expected_wait_duration),
            unittest.mock.call(timeout=expected_wait_duration),
            unittest.mock.call(timeout=expected_wait_duration)
        ])

        # Verify that the position was checked the expected number of times
        self.assertEqual(mock_position.call_count, 3)

        # Check if the input positions were updated correctly
        self.assertEqual(self.input_tracker.get_input_position(), (20, 20))
        self.assertEqual(self.input_tracker.get_last_input_position(), (10, 10))

    def test_set_idle_time_limit(self):
        new_limit = 60
        self.input_tracker.set_idle_time_limit(new_limit)
        self.assertEqual(self.input_tracker.idle_time_limit, new_limit)

if __name__ == '__main__':
    unittest.main()
