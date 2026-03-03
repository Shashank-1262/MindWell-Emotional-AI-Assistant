from datetime import datetime

def get_current_timestamp():
    """Returns current timestamp in a human-readable format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_filename_timestamp():
    """Returns current timestamp formatted for filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")
