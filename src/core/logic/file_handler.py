import os
import time
import pickle

from core.utils.file_utils import compute_hash, read_file, write_file, get_sessions_directory

class FileHandler:
    def __init__(self):
        time1 = str(time.localtime().tm_year) + '-' + str(time.localtime().tm_mon) + '-' + str(time.localtime().tm_mday) + '-' + str(time.localtime().tm_hour) + '-' + str(time.localtime().tm_min)
        self.fileName = f"{time1}.dat"
        self.hashFileName = f"{time1}.hash"
        self.directory = get_sessions_directory()
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        self.data = None
        self.continuingSession = False

    def save_data(self, data):
        self.data = data
        file_path = os.path.join(self.directory, self.fileName + '.dat')
        hash_path = os.path.join(self.directory, self.fileName + '.hash')

        # Save data to file
        write_file(file_path, data)

        # Compute and save hash
        data_hash = compute_hash(data)
        write_file(hash_path, data_hash.encode('utf-8'))

    def load_data(self, filename):
        file_path = os.path.join(self.directory, filename + '.dat')
        hash_path = os.path.join(self.directory, filename + '.hash')

        if os.path.exists(file_path) and os.path.exists(hash_path):
            # Read data and hash
            data = read_file(file_path)
            stored_hash = read_file(hash_path).decode('utf-8')

            # Compute hash of the loaded data
            computed_hash = compute_hash(data)

            if computed_hash == stored_hash:
                self.data = pickle.loads(data)
                print(f"{filename}: Data loaded and verified successfully.")
            else:
                print(f"{filename}: Data verification failed. Hash mismatch.")
                self.data = None
        else:
            print(f"{filename}: No data or hash file found.")

    def get_data(self):
        return self.data

    def set_file_name(self, file_name):
        if file_name is not None:
            self.fileName = file_name

    def set_continuing_session(self, continuation=bool):
        self.continuingSession = continuation

    def get_continuing_session(self):
        return self.continuingSession
