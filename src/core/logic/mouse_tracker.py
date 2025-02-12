import threading

class MouseTracker:
    def __init__(self, parent, logic_controller):
        self.parent = parent
        self.logic_controller = logic_controller
        self.mouse_position = None
        self.last_mouse_position = None

        self.update_thread = threading.Thread(target=self._update_mouse_position)