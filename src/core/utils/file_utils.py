import os
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

def get_projects_directory():
    """Define the projects directory, which stores project-organized session data"""
    if os.name == 'nt':  # Windows
        appdata_dir = os.getenv('APPDATA')
        projects_dir = os.path.join(appdata_dir, 'AppUsageGUI', 'Projects')
    else:  # macOS and Linux
        home_dir = os.path.expanduser('~')
        projects_dir = os.path.join(home_dir, '.local/share/AppUsageGUI/Projects')
    return projects_dir

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
    """Check if sessions exist in either old sessions directory or any project directory.
    Set p=True to print directory paths"""
    file_extension = ".dat"
    sessions_dir = get_sessions_directory()
    projects_dir = get_projects_directory()
    
    if p:
        print("sessions_dir: %s" % sessions_dir)
        print("projects_dir: %s" % projects_dir)
    
    # Check old sessions directory
    if os.path.exists(sessions_dir):
        for file in os.listdir(sessions_dir):
            if file.endswith(file_extension):
                return True
    
    # Check all project directories
    if os.path.exists(projects_dir):
        for project_name in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_name)
            if os.path.isdir(project_path):
                for file in os.listdir(project_path):
                    if file.endswith(file_extension):
                        return True
    
    # Ensure the old sessions directory exists for new standalone sessions
    if not os.path.exists(sessions_dir):
        os.makedirs(sessions_dir, exist_ok=True)
    
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
    """Returns session objects as a list from both old sessions directory and all project directories"""
    sessions_list = []
    file_extension = ".dat"
    
    # Get sessions from old sessions directory
    sessions_dir = get_sessions_directory()
    if os.path.exists(sessions_dir):
        for file in os.listdir(sessions_dir):
            if file.endswith(file_extension):
                sessions_list.append(file)
    
    # Get sessions from all project directories
    projects_dir = get_projects_directory()
    if os.path.exists(projects_dir):
        for project_name in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_name)
            if os.path.isdir(project_path):
                for file in os.listdir(project_path):
                    if file.endswith(file_extension):
                        sessions_list.append(file)
    
    return sessions_list

def get_project_sessions(project_name):
    """Returns session objects for a specific project as a list"""
    sessions_list = []
    file_extension = ".dat"
    projects_dir = get_projects_directory()
    project_dir = os.path.join(projects_dir, project_name)
    
    if os.path.exists(project_dir):
        for file in os.listdir(project_dir):
            if file.endswith(file_extension):
                sessions_list.append(file)
    return sessions_list

def project_exists(project_name):
    """Check if a project exists"""
    projects_dir = get_projects_directory()
    project_dir = os.path.join(projects_dir, project_name)
    return os.path.exists(project_dir)

def get_projects():
    """Returns list of all available projects"""
    projects_list = []
    projects_dir = get_projects_directory()
    
    if os.path.exists(projects_dir):
        for item in os.listdir(projects_dir):
            item_path = os.path.join(projects_dir, item)
            if os.path.isdir(item_path) and item != "__pycache__":
                projects_list.append(item)
    return projects_list

def get_session_project(session_filename):
    """Determine which project a session belongs to, or None if it's a standalone session"""
    projects_dir = get_projects_directory()
    
    if os.path.exists(projects_dir):
        for project_name in os.listdir(projects_dir):
            project_path = os.path.join(projects_dir, project_name)
            if os.path.isdir(project_path):
                session_path = os.path.join(project_path, session_filename)
                if os.path.exists(session_path):
                    return project_name
    
    # If not found in any project, it's a standalone session
    return None


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
    Returns -1 if the data is invalid"""
    try:
        captures = data['time_captures']
    
        # Check if we have enough starts and stops
        if len(captures['starts']) <= abs(start_pos) or len(captures['stops']) <= abs(start_pos):
            return -1
            
        start_time = captures['starts'][start_pos]
        stop_time = captures['stops'][start_pos]

        run_time = stop_time - start_time

        pauses = captures['pauses']
        for pause in pauses:
            if pause['start'] >= start_time and pause['start'] < stop_time:
                run_time -= pause['how_long']
        
        return run_time if run_time >= 0 else -1

        # Find the next stop position
    except (KeyError, IndexError):
        return -1
