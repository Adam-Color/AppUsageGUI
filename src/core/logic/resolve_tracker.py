import os
import subprocess
import sys
import threading
import logging

from core.utils.file_utils import read_file, write_file

logger = logging.getLogger(__name__)

class ResolveTracker:
    # Class-level variables to mimic the original global state
    project_data = {"name": "None"}
    script_dir = "Error"

    def __init__(self, parent, logic_controller):
        self.controller = logic_controller
        self._initialize_script_dir()
        self.stop_event = threading.Event()
        self.update_thread = None


    def _initialize_script_dir(self):
        """Determines the script directory based on the OS."""
        if os.name == 'nt':
            pass
        elif 'Darwin' in os.uname().sysname:
            self.script_dir = os.path.join(
                os.path.expanduser("~/Library/Application Support"),
                "Blackmagic Design",
                "DaVinci Resolve",
                "Fusion",
                "Scripts",
                "Utility"
            )
        else:
            pass

    def start(self):
        """Starts the background update thread."""
        self.update_thread = threading.Thread(
            target=self._update,
            name="resolve_connector"
        )
        self.update_thread.start()

    def stop(self):
        """Stops the background update thread."""
        self.stop_event.set()
        if self.update_thread is not None:
            self.update_thread.join()

    def _run_command(self, command):
        """Run a shell command and handle errors."""
        result = subprocess.run(command, shell=True)
        if result.returncode != 0:
            logger.error(f"Command '{command}' failed.")
            sys.exit(1)

    def inject_script(self):
        """Injects the project tracking script into DaVinci Resolve's Fusion script directory."""
        project_file = os.path.join(self.script_dir, "project.dat")
        write_file(project_file, self.project_data)

    def _update(self):
        """Runs the project tracking script and updates project data."""
        if os.name == 'nt':
            pass
        elif 'Darwin' in os.uname().sysname:
            self._run_command(f"python3 {self.script_dir}/project_tracker.py")
        else:
            pass

        # Update the class variable
        self.project_data = read_file(os.path.join(self.script_dir, "project.dat"))

    def get_project_data(self):
        """Returns the current project data."""
        return self.project_data
