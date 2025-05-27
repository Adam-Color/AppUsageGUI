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

        self.time_readout = "Error"
        self.start_readout = "Error"
        self.stop_readout = "Error"
        self.last_run_readout = "Error"

        # Display the page label
        self.page_label = tk.Label(self, text="Session Data:")
        self.page_label.pack(pady=10)

        # Display the labels
        self.total_time_label = tk.Label(self, text="Total Runtime: " + self.time_readout)
        self.total_time_label.pack(pady=5)

        self.start_time_label = tk.Label(self, text="Session Started: " + self.start_readout)
        self.start_time_label.pack(pady=5)

        self.stop_time_label = tk.Label(self, text="Last Ended: " + self.stop_readout)
        self.stop_time_label.pack(pady=5)

        self.last_run_label = tk.Label(self, text="Last Run Length: " + self.last_run_readout)
        self.last_run_label.pack(pady=5)

        # back to main window button
        back_button = tk.Button(self, text="Main Menu", command=lambda: (self.controller.reset_frames(), self.controller.show_frame("MainWindow")))
        back_button.pack(pady=5, side='bottom')

        # Start the total time thread
        self.total_session_time_thread = threading.Thread(target=self.total_time_thread, daemon=True, name="total_session_time")

    def update_total_time(self):
        try:
            # Fetch the data from the queue if available
            item = self.update_queue.get_nowait()
            self.time_readout = f"Total Runtime: {format_time(int(item['total_time']))}"
            self.total_time_label.config(text=self.time_readout)

            self.start_readout = "Session Started: " + (unix_to_datetime(item['first_run']).strftime("%Y-%m-%d %H:%M:%S") if item['first_run'] != "N/A" else "N/A")
            self.start_time_label.config(text=self.start_readout)

            self.stop_readout = "Last Ended: " + ((unix_to_datetime(item['last_run']).strftime("%Y-%m-%d %H:%M:%S")) if item['last_run'] != "N/A" else "N/A")
            self.stop_time_label.config(text=self.stop_readout)

            self.last_run_readout = "Last Run Length: " + (format_time(int(item['last_run_length'])) if item['last_run_length'] != "N/A" else "N/A")
            self.last_run_label.config(text=self.last_run_readout)
        except queue.Empty:
            pass

    def total_time_thread(self):
        while not self.stop_event.is_set() and (self.time_readout == "Error" or self.time_readout == "N/A"):
            data = {
            'total_time': "N/A",
            'first_run': "N/A",
            'last_run': "N/A",
            'last_run_length': "N/A"
            }
            try:
                # Get the total session time from the logic controller
                data.update({'total_time': self.logic.file_handler.get_data()['time_spent']})
                if self.logic.file_handler.get_data()['session_version'] != "1.0":
                    data.update({
                        'first_run': self.logic.file_handler.get_data()['time_captures']['starts'][0],
                        'last_run': self.logic.file_handler.get_data()['time_captures']['stops'][-1],
                        'last_run_length': calc_runtime(self.logic.file_handler.get_data(), -1)
                        })
                else:
                    data.update({
                        'last_run': self.logic.file_handler.get_data()['time_captures']['stops'][-1],
                        'last_run_length': calc_runtime(self.logic.file_handler.get_data(), -1)
                        })
            except (TypeError, KeyError):
                print(str(traceback.format_exc()))
                pass
            
            # Put the data into the queue to update the UI
            self.update_queue.put(data)
            self.update_total_time()

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
