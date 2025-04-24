#
# Copyright (c) Siemens AG 2025 ALL RIGHTS RESERVED
#
import os
import logging

parent_dir = os.path.dirname(os.getcwd())


class ErrorTrackingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.error_occurred = False

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.error_occurred = True


def setup_logger(logger_name: str, log_file: str = os.path.join(parent_dir, 'licencelynx.log'),
                 log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name, log file, and log level.

    Args:
        logger_name (str): Name of the logger.
        log_file (str): Path to the log file.
        log_level (int, optional): Logging level (default is logging.INFO).

    Returns:
        logging.Logger: Configured logger object.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create a console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Custom error tracking handler
    error_tracking_handler = ErrorTrackingHandler()
    logger.addHandler(error_tracking_handler)

    try:
        # Add a file handler
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception as e:
        # Handle any errors in setting up the file handler
        logger.error("Failed to set up file handler: %s", e)

    return logger
