import threading

import logging
logger = logging.getLogger(__name__)

# https://gist.github.com/awesomebytes/0483e65e0884f05fb95e314c4f2b3db8
def threaded(fn):
    logger.info(f"Running {fn}")
    def wrapper(*args, **kwargs):
        result = []
        def run_and_capture():
            result.append(fn(*args, **kwargs))
        thread = threading.Thread(target=run_and_capture, name=fn.__name__)
        thread.start()
        return thread, result
    return wrapper
