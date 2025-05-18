"""Handler for all file io operations"""

import os
import time
import pickle
import _pickle

from core.utils.file_utils import compute_hash, read_file, write_file, get_sessions_directory

class FileHandler:
    def __init__(self, parent, logic_controller):
        self.parent = parent
        self.controller = logic_controller
        time1 = str(int(time.time()))
        self.fileName = f"{time1}.dat"
        self.hashFileName = f"{time1}.hash"
        self.directory = get_sessions_directory()
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        self.data = None
        self.continuing_session = False
        self.continuing_tracker = False
        self.corrupt_sessions = []

    def save_session_data(self, data):
        """Special function to save and hash session data"""
        self.data = pickle.dumps(data)
        file_path = os.path.join(self.directory, self.fileName + '.dat')
        hash_path = os.path.join(self.directory, self.fileName + '.hash')

        # Save data to file
        write_file(file_path, self.data)

        # Compute and save hash
        data_hash = compute_hash(self.data)
        write_file(hash_path, data_hash.encode('utf-8'))

    def load_session_data(self, filename):
        """Loads session data from file and checks hash"""
        file_path = os.path.join(self.directory, filename + '.dat')
        hash_path = os.path.join(self.directory, filename + '.hash')

        if os.path.exists(file_path) and os.path.exists(hash_path):
            try:
                # Read data and hash
                data = read_file(file_path)
                stored_hash = read_file(hash_path).decode('utf-8')

                # Compute hash of the loaded data
                computed_hash = compute_hash(data)

                if computed_hash == stored_hash:
                    self.data = pickle.loads(data)
                else:
                    self.corrupt_sessions.append((filename, "Hash mismatch"))
                    self.data = None
            except _pickle.UnpicklingError as e:
                self.corrupt_sessions.append((filename, "Data is corrupt"))
                self.data = None
        else:
            self.corrupt_sessions.append((filename, "No hash file found"))
            self.data = None

    def delete_session(self, filename):
        """Delete data and hash files of a session"""
        file_path = os.path.join(self.directory, filename + '.dat')
        hash_path = os.path.join(self.directory, filename + '.hash')

        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(hash_path):
            os.remove(hash_path)

    def get_data(self):
        return self.data

    def set_file_name(self, file_name):
        if file_name is not None:
            self.fileName = file_name

    def set_continuing_session(self, continuation=bool):
        self.continuing_session = continuation
        if continuation:
            self.set_continuing_tracker(True)

    def set_continuing_tracker(self, value=bool):
        self.continuing_tracker = value

    def get_continuing_tracker(self):
        return self.continuing_tracker

    def get_continuing_session(self):
        return self.continuing_session

    def get_corrupt_sessions(self):
        return self.corrupt_sessions
