import os
import glob
import hashlib

# Define the path to the "Sessions/" directory four levels up from the current file
def get_sessions_directory():
    # Get the directory containing the script (e.g., "src/utils")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Move up four levels to the project root's parent directory
    four_levels_up = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
    # Define the "Sessions/" directory four levels up
    sessions_dir = os.path.join(four_levels_up, 'Sessions')
    return sessions_dir

def sessions_exist():
    sessions_dir = get_sessions_directory()
    # Ensure the directory exists
    if not os.path.exists(sessions_dir):
        os.makedirs(sessions_dir)
    return bool(glob.glob(os.path.join(sessions_dir, '*.dat')))

# Parses exe filename to give just the name
def name_from_exe(exename):
    if os.name == 'nt' or exename.endswith('.app'):
        # Split on the last period to avoid issues with multiple periods in the name
        split_exe_name, exe = exename.rsplit('.', 1)
        return split_exe_name
    # On Unix-like systems, return the name as is, unless it is .app
    return exename

def compute_hash(data):
    """Compute the SHA256 hash of the given data."""
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()

def read_file(file_path):
    """Read binary data from a file."""
    with open(file_path, 'rb') as f:
        return f.read()

def write_file(file_path, data):
    """Write binary data to a file."""
    with open(file_path, 'wb') as f:
        f.write(data)
