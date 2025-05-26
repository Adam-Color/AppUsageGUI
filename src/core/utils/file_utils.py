import os
import sys
import hashlib
import pickle

def get_sessions_directory():
    """Define the sessions directory, which stores application usage data"""
    if os.name == 'nt':  # Windows
        appdata_dir = os.getenv('APPDATA')
        sessions_dir = os.path.join(appdata_dir, 'AppUsageGUI', 'Sessions')
    else:  # macOS and Linux
        home_dir = os.path.expanduser('~')
        sessions_dir = os.path.join(home_dir, '.local/share/AppUsageGUI/Sessions')
    return sessions_dir

def get_user_directory():
    """Define the user directory, which stores presets and settings"""
    if os.name == 'nt':  # Windows
        appdata_dir = os.getenv('APPDATA')
        user_dir = os.path.join(appdata_dir, 'AppUsageGUI', 'User')
    else:  # macOS and Linux
        home_dir = os.path.expanduser('~')
        user_dir = os.path.join(home_dir, '.local/share/AppUsageGUI/User')
    return user_dir

def config_file():
    """Returns the path to the config file"""
    return os.path.join(get_user_directory(), 'config.dat')

def apps_file():
    """Returns the path to the apps file"""
    return os.path.join(get_user_directory(), 'apps.dat')

def sessions_exist(p=False):
    """Check if sessions exist, and if not, create the directory.
    Set p=True to print directory path"""
    file_extension = ".dat"
    sessions_dir = get_sessions_directory()
    if p:
        print("sessions_dir: %s" % sessions_dir)
    # Ensure the directory exists
    if not os.path.exists(sessions_dir):
        os.makedirs(sessions_dir, exist_ok=True)
        return False
    for file in os.listdir(sessions_dir):
        if file.endswith(file_extension):
            return True
    return False

def user_dir_exists(p=False):
    """Check if user directory exists, and if not, create the directory.
    Set p=True to print directory path"""
    user_dir = get_user_directory()
    if p:
        print("user_dir: %s" % user_dir)
    # Ensure the directory exists
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True)
        return False
    return True

def get_sessions():
    """Returns session objects as a list"""
    sessions_list = []
    file_extension = ".dat"
    sessions_dir = get_sessions_directory()
    for file in os.listdir(sessions_dir):
        if file.endswith(file_extension):
            sessions_list.append(file)
    return sessions_list


def name_from_exe(exename):
    """Parses exe filename to give just the name"""
    if os.name == 'nt' or exename.endswith('.app'):
        # Split on the last period to avoid issues with multiple periods in the name
        split_exe_name, exe = exename.rsplit('.', 1)
        return split_exe_name
    # On Unix-like systems, return the name as is, unless it is .app
    return exename

def compute_hash(data):
    """Compute the SHA256 hash of the input data"""
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()

def read_file(file_path):
    """Read and deserialize data from a .dat file"""
    with open(file_path, 'rb') as f:
        return pickle.load(f)

def write_file(file_path, data):
    """Serialize and write data to a .dat file"""
    with open(file_path, 'wb') as f:
        f.truncate(0)
        pickle.dump(data, f)

def calc_runtime(data, start_pos):
    """Calculate the runtime of a single run in seconds from time captures.
    Returns -1 if the data is invalid or start_pos is out of bounds."""
    try:
        if not data or start_pos > len(data):
            return -1
    
        captures = data['time_captures']
    
        start_time = captures['starts'][start_pos]
        stop_time = captures['stops'][start_pos]

        # Find the next stop position
    except KeyError:
        return -1