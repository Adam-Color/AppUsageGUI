import tkinter as tk
import queue
import threading
import traceback

from core.utils.time_utils import format_time, unix_to_datetime
from core.utils.file_utils import calc_runtime


class SessionTotalWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        super().__init__(parent)
        self.controller = controller
        self.logic = logic_controller

        self.update_queue = queue.Queue()
        self.stop_event = threading.Event()

        # Defaults
        self.name_readout = "Error"
        self.project_readout = "Error"
        self.app_readout = "Error"
        self.time_readout = "Error"
        self.ptime_readout = "Error"
        self.start_readout = "Error"
        self.stop_readout = "Error"
        self.last_run_readout = "Error"
        self.num_starts_readout = "Error"

        # ===== Title Section =====
        title_frame = tk.Frame(self, pady=10)
        title_frame.pack(fill="x")

        title_label = tk.Label(
            title_frame,
            text="Session Data",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(5, 0))

        subtitle_label = tk.Label(
            title_frame,
            text="Details for the currently selected session.",
            font=("Arial", 11)
        )
        subtitle_label.pack(pady=(0, 15))

        # ===== Data Card =====
        card = tk.Frame(
            self,
            bd=2, relief="groove",
            padx=15, pady=15
        )
        card.pack(fill="both", expand=True, padx=20, pady=15)

        # Each line: label with dynamic text
        self.name_label = tk.Label(card, text="Session Name: " + self.name_readout, anchor="w", font=("Arial", 11))
        self.name_label.pack(fill="x", pady=4)

        self.project_label = tk.Label(card, text="Project Name: " + self.project_readout, anchor="w", font=("Arial", 11))
        self.project_label.pack(fill="x", pady=4)

        self.app_label = tk.Label(card, text="Tracked App Name: " + self.app_readout, anchor="w", font=("Arial", 11))
        self.app_label.pack(fill="x", pady=4)

        self.total_time_label = tk.Label(card, text="Total Session Runtime: " + self.time_readout, anchor="w", font=("Arial", 11))
        self.total_time_label.pack(fill="x", pady=4)

        self.ptime_label = tk.Label(card, text="Total Project Runtime: " + self.ptime_readout, anchor="w", font=("Arial", 11))
        self.ptime_label.pack(fill="x", pady=4)

        self.start_time_label = tk.Label(card, text="Session Started: " + self.start_readout, anchor="w", font=("Arial", 11))
        self.start_time_label.pack(fill="x", pady=4)

        self.stop_time_label = tk.Label(card, text="Last Ended: " + self.stop_readout, anchor="w", font=("Arial", 11))
        self.stop_time_label.pack(fill="x", pady=4)

        self.last_run_label = tk.Label(card, text="Last Run Length: " + self.last_run_readout, anchor="w", font=("Arial", 11))
        self.last_run_label.pack(fill="x", pady=4)

        self.num_starts_label = tk.Label(card, text="Number of Runs: " + self.num_starts_readout, anchor="w", font=("Arial", 11))
        self.num_starts_label.pack(fill="x", pady=4)

        # ===== Back Button =====
        back_button = tk.Button(
            self,
            text="Main Menu",
            command=lambda: (self.controller.reset_frames(), self.controller.show_frame("MainWindow")),
            width=15, height=2
        )
        back_button.pack(pady=15, side="bottom")

        # Start background thread
        self.total_session_time_thread = threading.Thread(
            target=self.total_time_thread,
            daemon=True,
            name="total_session_time"
        )

    def update_total_time(self):
        try:
            item = self.update_queue.get_nowait()

            self.name_label.config(text="Session Name: " + item['session_name'])

            if item['project_name'] != "Error":
                self.project_label.config(text="Project Name: " + item['project_name'])
            else:
                self.project_label.config(text="Project Name: N/A")

            self.app_label.config(text="Tracked App Name: " + item['tracked_app'])

            if item['project_name'] != "Error":
                self.ptime_label.config(text=f"Total Project Runtime: {format_time(int(item['project_time']))}")
            else:
                self.ptime_label.config(text="Total Project Runtime: N/A")

            self.total_time_label.config(text=f"Total Session Runtime: {format_time(int(item['total_time']))}")

            start_text = unix_to_datetime(item['first_run']).strftime("%Y-%m-%d %H:%M:%S") if item['first_run'] != "N/A" else "N/A"
            self.start_time_label.config(text="Session Started: " + start_text)

            stop_text = unix_to_datetime(item['last_run']).strftime("%Y-%m-%d %H:%M:%S") if item['last_run'] != "N/A" else "N/A"
            self.stop_time_label.config(text="Last Ended: " + stop_text)

            last_run_text = format_time(int(item['last_run_length'])) if item['last_run_length'] != "N/A" else "N/A"
            self.last_run_label.config(text="Last Run Length: " + last_run_text)

            self.num_starts_label.config(text="Number of Runs: " + (item['num_starts'] if item['num_starts'] != "N/A" else "N/A"))
        except queue.Empty:
            pass

    def total_time_thread(self):
        while not self.stop_event.is_set() and (self.time_readout == "Error" or self.time_readout == "N/A"):
            data = {
                'session_name': "Error",
                'project_name': "Error",
                'tracked_app': "Error",
                'total_time': "Error",
                'project_time': "Error",
                'first_run': "N/A",
                'last_run': "N/A",
                'last_run_length': "N/A",
                'num_starts': "N/A"
            }
            try:
                data.update({
                    'session_name': self.logic.file_handler.get_file_name(),
                    'tracked_app': self.logic.file_handler.get_data()['app_name'],
                    'total_time': self.logic.file_handler.get_data()['time_spent'],
                })
                if 'project_name' in self.logic.file_handler.get_data() and self.logic.file_handler.get_data()['project_name']:
                    data.update({
                        'project_name': self.logic.file_handler.get_data()['project_name'],
                        'project_time': self.logic.project_handler.get_project_total_time(
                            self.logic.file_handler.get_data()['project_name'])
                    })
                if 'session_version' in self.logic.file_handler.get_data() and self.logic.file_handler.get_data()['session_version'] != "1.0":
                    time_captures = self.logic.file_handler.get_data()['time_captures']
                    data.update({
                        'first_run': time_captures['starts'][0] if time_captures['starts'] else "N/A",
                        'last_run': time_captures['stops'][-1] if time_captures['stops'] else "N/A",
                        'last_run_length': calc_runtime(self.logic.file_handler.get_data(), -1),
                        'num_starts': str(len(time_captures['starts']))
                    })
                elif 'session_version' in self.logic.file_handler.get_data():
                    time_captures = self.logic.file_handler.get_data()['time_captures']
                    data.update({
                        'last_run': time_captures['stops'][-1] if time_captures['stops'] else "N/A",
                        'last_run_length': calc_runtime(self.logic.file_handler.get_data(), -1)
                    })
            except (TypeError, KeyError):
                print("Error loading session data:\n")
                print("raw data:", self.logic.file_handler.get_data())
                print(traceback.format_exc())

            self.update_queue.put(data)
            self.update_total_time_id = self.update_total_time()

            self.stop_event.wait(timeout=1)

    def stop_threads(self, wait=True):
        if wait:
            self.stop_event.wait(timeout=1)
        self.stop_event.set()

        try:
            self.after_cancel(self.update_total_time_id)
        except (AttributeError, ValueError):
            pass
