"""The entire GUI is created here, in one file."""

import sys
import os
import webbrowser
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QMessageBox,
    QListWidget, QHBoxLayout, QPushButton, QMenu
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal, pyqtSlot

from _version import __version__
from core.utils.file_utils import sessions_exist, user_dir_exists
from core.utils.time_utils import format_time, unix_to_datetime
from .logic_root import LogicRoot

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def is_dark_mode():
    if os.name == 'nt':  # Windows
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize") as key:
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                return value == 0
        except Exception:
            return False
    elif sys.platform == 'darwin':  # macOS
        try:
            from AppKit import NSUserDefaults
            defaults = NSUserDefaults.standardUserDefaults()
            return defaults.boolForKey_("AppleInterfaceStyle") == "Dark"
        except ImportError:
            return False
    elif sys.platform.startswith('linux'):  # Linux
        try:
            with open(os.path.expanduser("~/.config/gtk-3.0/settings.ini"), 'r') as f:
                for line in f:
                    if "gtk-theme-name" in line:
                        return "dark" in line.lower()
        except FileNotFoundError:
            return False

def new_updates():
    try:
        response = requests.get("https://api.github.com/repos/adam-color/AppUsageGUI/releases/latest", timeout=10)
        response.raise_for_status()
        data = response.json()
        latest_version = data["tag_name"].lstrip('v').split('.')
        current_version = __version__.split('.')
        for latest, current in zip(latest_version, current_version):
            if int(latest) > int(current):
                return True
            elif int(latest) < int(current):
                return False
        return False
    except requests.RequestException as e:
        print(f"Error checking for updates: Network error - {str(e)}")
    except (KeyError, ValueError, IndexError) as e:
        print(f"Error checking for updates: Parsing error - {str(e)}")
    except Exception as e:
        print(f"Error checking for updates: Unexpected error - {str(e)}")
    return False

def splash_screen():
    if new_updates():
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("AppUsageGUI")
        msg_box.setText("A new update is available. Would you like to download it from the GitHub page?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        response = msg_box.exec()
        if response == 16385: # if the user clicked "Yes"
            webbrowser.open_new_tab("https://github.com/adam-color/AppUsageGUI/releases/latest")

    splash = QWidget()
    splash.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.CustomizeWindowHint)
    splash.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    splash.setGeometry(600, 300, 250, 80)
    splash.setWindowTitle("AppUsageGUI - Loading...")
    layout = QVBoxLayout()
    label = QLabel("\nLoading...")
    layout.addWidget(label)
    splash.setLayout(layout)
    splash.show()
    QApplication.processEvents()
    splash.close()

class SessionsList(QListWidget):
    def onItemClicked(self, item):
        QMessageBox.information(self, "QListWidget Interaction", "You selected: " + item.text())

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # Initialize LogicRoot
        self.logic = LogicRoot(self)

        # calls to create the app directories
        sessions_exist()
        user_dir_exists()

    def init_ui(self):
        splash_screen()

        # define the main layout type --
        layout = QVBoxLayout()

        # define nested layouts --
        controls_layout = QHBoxLayout()

        # app setup --
        self.setLayout(layout)
        # self.setWindowFlags()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle(f"AppUsageGUI - v{__version__}")
        icon_name = "core/resources/icon.ico" if os.name == 'nt' else "core/resources/icon.icns"
        icon_path = resource_path(icon_name)
        self.setWindowIcon(QIcon(icon_path))

        if is_dark_mode():
            self.setStyleSheet("background-color: #2E2E2E; color: white;")

        # create widgets --
        tracking_status_label = QLabel("Tracking Status: No Session Loaded")
        tracking_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tracking_status_label.setStyleSheet("font-size: 18px;")

        time_label = QLabel("0h 0m 0s")
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_label.setStyleSheet("font-size: 64px;")

        # create buttons --
        sessions_button = QPushButton("Sessions...")
        sessions_button.clicked.connect(self.closeEvent)

        pause_resume_button = QPushButton("Pause")

        # add widgets and nested layouts to the main layout --
        layout.addWidget(tracking_status_label)
        layout.addWidget(time_label)
        layout.addLayout(controls_layout)
        controls_layout.addWidget(sessions_button)
        controls_layout.addWidget(pause_resume_button)

    def closeEvent(self, event):
        print("Closing the application...")
        if self.logic.app_tracker:
            self.logic.app_tracker.reset()
        if self.logic.time_tracker:
            self.logic.time_tracker.reset()
        if self.logic.mouse_tracker:
            self.logic.mouse_tracker.stop()
        self.close()
        sessions_exist()
        user_dir_exists()
        self.logic.close()
        QApplication.instance().quit()
        event.accept()
