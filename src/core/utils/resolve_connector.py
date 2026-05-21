import os
from core.utils.file_utils import read_file, write_file
import subprocess
import sys

import logging
logger = logging.getLogger(__name__)

script_dir = "Error"
if os.name == 'nt':
    pass
elif 'Darwin' in os.uname().sysname:
    script_dir = os.path.join(os.path.expanduser("~/Library/Application Support"), "Blackmagic Design", "DaVinci Resolve", "Fusion", "Scripts", "Utility")
else:
    pass

def run_command(command):
    """Run a shell command and handle errors."""
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        logger.error(f"Command '{command}' failed.")
        sys.exit(1)

def inject_script():
    """Injects the project tracking script into DaVinci Resolve's Fusion script directory."""
    project_file = os.path.join(script_dir, "project.dat")

    project_data = {"name": "None"}

    write_file(project_file, project_data)

    update()

def update():
    """runs the project tracking script"""
    if os.name == 'nt':
        pass
    elif 'Darwin' in os.uname().sysname:
        run_command("")
    else:
        pass
