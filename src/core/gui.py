import sys
import os
import webbrowser
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QMessageBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from _version import __version__
from core.utils.file_utils import sessions_exist, user_dir_exists
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
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("AppUsageGUI")
        msg_box.setText("A new update is available. Would you like to download it from the GitHub page?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        response = msg_box.exec_()
        if response == QMessageBox.Yes:
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

class GUIRoot(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

        # Initialize LogicRoot
        self.logic_controller = LogicRoot(self)

    def init_ui(self):
        splash_screen()
        layout = QVBoxLayout()
        label = QLabel("Welcome to AppUsageGUI")
        layout.addWidget(label)
        self.setLayout(layout)
        # self.setWindowFlags()
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle(f"AppUsageGUI - v{__version__}")
        icon_name = "core/resources/icon.ico" if os.name == 'nt' else "core/resources/icon.icns"
        icon_path = resource_path(icon_name)
        self.setWindowIcon(QIcon(icon_path))

        if is_dark_mode():
            self.setStyleSheet("background-color: #2E2E2E; color: white;")

        sessions_exist()
        user_dir_exists()

    def closeEvent(self, event):
        print("Closing the application...")
        self.logic_controller.close()
        QApplication.instance().quit()
        event.accept()
