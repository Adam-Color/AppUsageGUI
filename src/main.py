import sys
import psutil
from PyQt6.QtWidgets import QApplication

from core.gui import MainWindow

def is_app_running():
    """Check if the application is already running."""
    current_process = psutil.Process()
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == current_process.name() and process.info['pid'] != current_process.pid:
            return True
    return False

def main():
    # check if app is already running
    if is_app_running():
        sys.exit(0)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
