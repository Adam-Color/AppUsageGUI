import os
import glob
import hashlib

def sessions_exist(directory):
    return bool(glob.glob(os.path.join(directory, '*.dat')))

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
