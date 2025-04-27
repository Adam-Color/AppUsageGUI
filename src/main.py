import sys
import socket
from PyQt6.QtWidgets import QApplication

from core.gui import MainWindow


def main():
    # check if app is already running
    try:
        # create a socket to check if the app is already running
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("localhost", 0))  # bind to an available port
        sock.listen(1)  # listen for incoming connections
    except socket.error:
        # if there is an error, it means the app is already running
        print("App is already running")
        sys.exit()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
