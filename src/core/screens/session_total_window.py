import tkinter as tk
import queue
import time
import threading

from core.utils.time_utils import format_time

class SessionTotalWindow(tk.Frame):
    def __init__(self, parent, controller, logic_controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.logic_controller = logic_controller

        self.update_queue = queue.Queue()

        self.stop_event = threading.Event()

        self.time_readout = "loading..."

        # Display the page label
        self.page_label = tk.Label(self, text="Total time for this session:")
        self.page_label.pack(pady=5)

        # Display the total time label
        self.total_time_label = tk.Label(self, text=self.time_readout)
        self.total_time_label.pack(pady=10)

        # back to main window button
        back_button = tk.Button(self, text="Main Menu", command=lambda: (self.controller.reset_frames(), self.controller.show_frame("MainWindow")))
        back_button.pack(pady=5, side='bottom')

        # Start the total time thread
        threading.Thread(target=self.total_time_thread, daemon=True, name="total_session_time").start()

        # Start the update queue
        self.update_total_time()

    def update_total_time(self):
        try:
            # Fetch the total time from the queue if available
            item = self.update_queue.get_nowait()
            self.time_readout = f"{format_time(int(item))}"  # Update the time readout string
            self.total_time_label.config(text=self.time_readout)  # Update the label
        except queue.Empty:
            pass
        
        # Call this method again after 1000 ms (1 second) to keep updating the label
        self.update_total_time_id = self.after(1000, self.update_total_time)

    def total_time_thread(self):
        while not self.stop_event.is_set():
            try:
                if self.logic_controller.time_tracker.get_time() > 0 and self.logic_controller.time_tracker.is_running():
                    # Get the total session time from the logic controller
                    total_time = self.logic_controller.time_tracker.get_total_time()

                    # Put the total time into the queue to update the UI
                    self.update_queue.put(total_time)
            except TypeError:
                pass

            # Sleep for 1 second before the next update
            self.stop_event.wait(timeout=1)
    
    def stop_threads(self):
        """Stop the threads gracefully."""
        self.stop_event.wait(timeout=1)  # Wait for the threads to finish
        self.stop_event.set()

        # Cancel scheduled update_total_time calls
        try:
            self.after_cancel(self.update_total_time_id)
        except AttributeError:
            pass  # If no updates were scheduled yet, ignore error
        except ValueError:
            pass  # If already cancelled, ignore error
