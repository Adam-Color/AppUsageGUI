import os
import hashlib
import pickle

# Define the path to the "Sessions/" directory
def get_sessions_directory():
    if os.name == 'nt':  # Windows
        appdata_dir = os.getenv('APPDATA')
        sessions_dir = os.path.join(appdata_dir, 'AppUsageGUI', 'Sessions')
    else:  # macOS and Linux
        home_dir = os.path.expanduser('~')
        sessions_dir = os.path.join(home_dir, '.local/share/AppUsageGUI/Sessions')

    return sessions_dir

def sessions_exist():
    file_extension = ".dat"
    sessions_dir = get_sessions_directory()
    print("sessions_dir: %s" % sessions_dir) #!
    # Ensure the directory exists
    if not os.path.exists(sessions_dir):
        os.makedirs(sessions_dir, exist_ok=True)
        return False
    for file in os.listdir(sessions_dir):
        if file.endswith(file_extension):
            return True
    return False

def get_sessions():
    sessions_list = []
    file_extension = ".dat"
    sessions_dir = get_sessions_directory()
    for file in os.listdir(sessions_dir):
        if file.endswith(file_extension):
            sessions_list.append(file)
    return sessions_list


# Parses exe filename to give just the name
def name_from_exe(exename):
    if os.name == 'nt' or exename.endswith('.app'):
        # Split on the last period to avoid issues with multiple periods in the name
        split_exe_name, exe = exename.rsplit('.', 1)
        return split_exe_name
    # On Unix-like systems, return the name as is, unless it is .app
    return exename

# Compute the SHA256 hash of the given data
def compute_hash(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()

# Read and deserialize data from a .dat file
def read_file(file_path):
    with open(file_path, 'rb') as f:
        return pickle.load(f)

# Serialize and write data to a .dat file
def write_file(file_path, data):
    with open(file_path, 'wb') as f:
        pickle.dump(data, f)
