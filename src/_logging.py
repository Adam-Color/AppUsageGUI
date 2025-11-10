import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

from core.utils.file_utils import get_user_directory

def setup_logging():
    """Set up application-wide logging with rotation."""
    # Folder for logs
    logs_dir = os.path.join(get_user_directory(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Log file path
    log_file = os.path.join(logs_dir, f"{datetime.now():%Y-%m-%d_%H-%M-%S}.log")

    # Create rotating file handler
    rotating_handler = RotatingFileHandler(
        log_file,
        maxBytes=2_000_000,   # 2 MB before rotating
        backupCount=20,        # keep 20 old log files
        encoding='utf-8'
    )

    # Console handler
    console_handler = logging.StreamHandler()

    # Shared format
    log_format = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    rotating_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(rotating_handler)
    root_logger.addHandler(console_handler)

    cleanup_old_logs(logs_dir, backup_count=5)

    # quiet some libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    root_logger.info(f"Logging initialized: {log_file}")

def get_current_log_file():
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Iterate through the handlers
    for handler in root_logger.handlers:
        if isinstance(handler, logging.handlers.RotatingFileHandler):
            # Return the log file path
            return handler.baseFilename
    
    # If no RotatingFileHandler is found
    return None

def cleanup_old_logs(logs_dir, backup_count):
    """Delete old log files if they exceed the backup count."""
    try:
        # List all log files in the directory
        log_files = [os.path.join(logs_dir, f) for f in os.listdir(logs_dir) if f.endswith('.log')]

        # Sort log files by creation time (oldest first)
        log_files.sort(key=os.path.getctime)

        # Delete files exceeding the backup count
        for log_file in log_files[:-backup_count]:
            os.remove(log_file)
    except Exception as e:
        logging.error(f"Failed to clean up old log files: {e}")