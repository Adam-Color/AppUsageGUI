"""Contains utility functions for time related operations"""
import datetime

def format_time(secs):
    """Formats time in seconds to hours, minutes, seconds"""
    hours, remainder = divmod(int(secs), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"

def unix_to_datetime(unix_time):
    """Converts unix time to datetime object"""
    return datetime.datetime.fromtimestamp(unix_time)
