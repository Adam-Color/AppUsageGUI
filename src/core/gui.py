import PyQt5 as qt

class MainWindow(qt.QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("My Application")
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget
        self.central_widget = qt.QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create a layout
        self.layout = qt.QtWidgets.QVBoxLayout(self.central_widget)

        # Add widgets to the layout
        self.label = qt.QtWidgets.QLabel("Hello, World!", self.central_widget)
        self.layout.addWidget(self.label)

        self.button = qt.QtWidgets.QPushButton("Click Me", self.central_widget)
        self.layout.addWidget(self.button)