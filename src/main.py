import sys
from PyQt6.QtWidgets import QApplication
from core.gui import GUIRoot 

def main():
    app = QApplication(sys.argv)
    window = GUIRoot()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
