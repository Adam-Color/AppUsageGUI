import tkinter as tk
import queue
import threading
import traceback

from core.utils.time_utils import format_time, unix_to_datetime
from core.utils.file_utils import calc_runtime

class SessionTotalWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic = logic_controller

        self.update_queue = queue.Queue()

        self.stop_event = threading.Event()

        self.name_readout = "Error"
        self.project_readout = "Error"
        self.app_readout = "Error"
        self.time_readout = "Error"
        self.ptime_readout = "Error" # total project time
        self.start_readout = "Error"
        self.stop_readout = "Error"
        self.last_run_readout = "Error"
        self.num_starts_readout = "Error"

        # Display the page label
        self.page_label = tk.Label(self, text="Session Data:")
        self.page_label.pack(pady=10)

        # Display the labels
        self.name_label = tk.Label(self, text="Session Name: " + self.name_readout)
        self.name_label.pack(pady=5)

        self.project_label = tk.Label(self, text="Project Name: " + self.project_readout)
        self.project_label.pack(pady=5)

        self.app_label = tk.Label(self, text="Tracked App Name: " + self.app_readout)
        self.app_label.pack(pady=5)

        self.total_time_label = tk.Label(self, text="Total Session Runtime: " + self.time_readout)
        self.total_time_label.pack(pady=5)

        self.ptime_label = tk.Label(self, text="Total Project Runtime: " + self.ptime_readout)
        self.ptime_label.pack(pady=5)

        self.start_time_label = tk.Label(self, text="Session Started: " + self.start_readout)
        self.start_time_label.pack(pady=5)

        self.stop_time_label = tk.Label(self, text="Last Ended: " + self.stop_readout)
        self.stop_time_label.pack(pady=5)

        self.last_run_label = tk.Label(self, text="Last Run Length: " + self.last_run_readout)
        self.last_run_label.pack(pady=5)

        self.num_starts_label = tk.Label(self, text="Number of Runs: " + self.num_starts_readout)
        self.num_starts_label.pack(pady=5)

        # back to main window button
        back_button = tk.Button(self, text="Main Menu", command=lambda: (self.controller.reset_frames(), self.controller.show_frame("MainWindow")))
        back_button.pack(pady=5, side='bottom')

        # Start the total time thread
        self.total_session_time_thread = threading.Thread(target=self.total_time_thread, daemon=True, name="total_session_time")

    def update_total_time(self):
        try:
            # Fetch the data from the queue if available
            item = self.update_queue.get_nowait()

            self.name_readout = "Session Name: " + item['session_name']
            self.name_label.config(text=self.name_readout)

            if item['project_name'] != "Error":
                self.project_readout = "Project Name: " + item['project_name']
                self.project_label.config(text=self.project_readout)
            else:
                self.project_readout = "N/A"
                self.project_label.config(text="Project Name: N/A")

            self.app_readout = "Tracked App Name: " + item['tracked_app']
            self.app_label.config(text=self.app_readout)

            if item['project_name'] != "Error":
                self.ptime_readout = f"Total Project Runtime: {format_time(int(item['project_time']))}"
                self.ptime_label.config(text=self.ptime_readout)
            else:
                self.ptime_readout = "N/A"
                self.ptime_label.config(text="Total Project Runtime: N/A")

            self.time_readout = f"Total Session Runtime: {format_time(int(item['total_time']))}"
            self.total_time_label.config(text=self.time_readout)

            self.start_readout = "Session Started: " + (unix_to_datetime(item['first_run']).strftime("%Y-%m-%d %H:%M:%S") if item['first_run'] != "N/A" else "N/A")
            self.start_time_label.config(text=self.start_readout)

            self.stop_readout = "Last Ended: " + ((unix_to_datetime(item['last_run']).strftime("%Y-%m-%d %H:%M:%S")) if item['last_run'] != "N/A" else "N/A")
            self.stop_time_label.config(text=self.stop_readout)

            self.last_run_readout = "Last Run Length: " + (format_time(int(item['last_run_length'])) if item['last_run_length'] != "N/A" else "N/A")
            self.last_run_label.config(text=self.last_run_readout)

            self.num_starts_readout = "Number of Runs: " + (item['num_starts'] if item['num_starts'] != "N/A" else "N/A")
            self.num_starts_label.config(text=self.num_starts_readout)
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
                # Get the data
                data.update({
                    'session_name': self.logic.file_handler.get_file_name(),
                    'tracked_app': self.logic.file_handler.get_data()['app_name'],
                    'total_time': self.logic.file_handler.get_data()['time_spent'],
                    })
                if self.logic.file_handler.get_data()['project_name']:
                    data.update({
                        'project_name': self.logic.file_handler.get_data()['project_name'],
                        'project_time': self.logic.project_handler.get_project_total_time(self.logic.file_handler.get_data()['project_name'])})
                if self.logic.file_handler.get_data()['session_version'] != "1.0":
                    time_captures = self.logic.file_handler.get_data()['time_captures']
                    data.update({
                        'first_run': time_captures['starts'][0] if time_captures['starts'] else "N/A",
                        'last_run': time_captures['stops'][-1] if time_captures['stops'] else "N/A",
                        'last_run_length': calc_runtime(self.logic.file_handler.get_data(), -1),
                        'num_starts': str(len(time_captures['starts']))
                        })
                else:
                    time_captures = self.logic.file_handler.get_data()['time_captures']
                    data.update({
                        'last_run': time_captures['stops'][-1] if time_captures['stops'] else "N/A",
                        'last_run_length': calc_runtime(self.logic.file_handler.get_data(), -1)
                        })
            except (TypeError, KeyError):
                print("Error loading session data:\n")
                print(traceback.format_exc())
            
            # Put the data into the queue to update the UI
            self.update_queue.put(data)
            self.update_total_time_id = self.update_total_time()

            # Sleep for 1 second before the next update
            self.stop_event.wait(timeout=1)
    
    def stop_threads(self, wait=True):
        """Stop the threads gracefully."""
        if wait:
            self.stop_event.wait(timeout=1)  # Wait for the threads to finish
        self.stop_event.set()

        # Cancel scheduled update_total_time calls
        try:
            self.after_cancel(self.update_total_time_id)
        except AttributeError:
            pass  # If no updates were scheduled yet, ignore error
        except ValueError:
            pass  # If already cancelled, ignore error
