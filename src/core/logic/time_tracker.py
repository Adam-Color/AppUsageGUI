import time

from core.utils.logic_utils import threaded

import logging
logger = logging.getLogger(__name__)

class TimeTracker:
    """A clock that runs in a separate thread to track elapsed time, 
    with pause and resume functionality."""
    def __init__(self, parent, logic_controller):
        self.parent = parent

        # note: logic controller is defined as the only controller
        self.controller = logic_controller

        self.track = False
        self.start_time = None
        self.elapsed_time = 0.0
        self.total_time = 0.0
        self.paused_time = 0.0
        self.resumed_time = 0.0
        self.offset_time = 0.0
        self.is_paused = False

        # time captures for data analysis are saved in the following format:
        # {'starts': [], 'stops': [], 'pauses': [{start: 0, how_long: 0}, ...]}
        self.captures = {'starts': [], 'stops': [], 'pauses': []}

    @threaded
    def clock(self):
        """This method runs in a separate 
        thread and updates the elapsed time."""
        self.start_time = time.time()
        while self.track:
            # time does not elapse when paused
            if not self.is_paused:
                self.elapsed_time = time.time() - self.start_time - self.offset_time
            # sleep needs to be kept low here for accuracy
            time.sleep(0.1)

    def start(self):
        self.track = True
        self.captures['starts'].append(time.time())
        logger.info("Starting time tracker")

    def stop(self):
        if self.track:
            self.captures['stops'].append(time.time())
            logger.info("Stopping time tracker")
            self.track = False

    def pause(self):
        if self.track and not self.is_paused:
            self.is_paused = True
            self.paused_time = time.time()
            logger.info("Pausing time tracker")

    def resume(self):
        """Resumes the tracker, subtracts the time paused."""
        if self.track and self.is_paused:
            self.is_paused = False
            self.resumed_time = time.time()
            self.offset_time += self.resumed_time - self.paused_time
            self.captures['pauses'].append({'start': self.paused_time,
                                            'how_long': self.resumed_time - self.paused_time})
            logger.info("Resuming time tracker")
    
    def reset(self, add_time=0.0):
        self.elapsed_time = 0.0
        self.offset_time = 0.0
        self.paused_time = 0.0
        self.resumed_time = 0.0
        self.total_time = add_time
        self.track = False
        self.start_time = None
        self.captures = {'starts': [], 'stops': [], 'pauses': []}
        logger.info(self.controller.file_handler.get_continuing_session())
        if self.controller.file_handler.get_continuing_session() == True:
            self.update_captures()  # update captures from session file if applicable
        logging.info("Time tracker reset.")
    
    def update_captures(self):
        """populates the captures dictionary with data from the session file"""
        try:
            self.captures = self.controller.file_handler.get_data()['time_captures']
        except KeyError as e:
            from traceback import print_exc
            # handle v1 session files
            if str(e) != '\'time_captures\'':
                logger.error("Error loading time captures from session file:\n")
                print_exc()

    def get_is_paused(self):
        return self.is_paused

    def get_time(self, saved=False):
        if not self.track and saved is False:
            return None
        return self.elapsed_time

    def get_total_time(self):
        return self.total_time + self.elapsed_time
    
    def get_paused_time(self):
        return self.paused_time
    
    def get_elapsed_time(self):
        return self.elapsed_time
    
    def get_time_captures(self):
        return self.captures

    def is_running(self):
        return self.track
