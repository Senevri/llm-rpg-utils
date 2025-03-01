"""Some basic logging for the project"""

import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path

# from lib.__initpkg__ import CONFIG


class CONFIG:
    FILE_LOG_ENABLED = True
    ADD_DATE_TO_LOG_FILE = False
    CONSOLE_LOGGING = True
    LOG_PATH = Path("logs")


def get_custom_logger(
    file,
    name,
    save_to_file=CONFIG.FILE_LOG_ENABLED,
    add_date=CONFIG.ADD_DATE_TO_LOG_FILE,
    console=CONFIG.CONSOLE_LOGGING,
    fmt=None,
    fltr=None,
    level=logging.DEBUG,
) -> logging.Logger:
    """
    Returns a logger with the specified configuration.

    Args:
        file (str): The name of the log file.
        name (str): The name of the logger.
        save_to_file (bool, optional): Whether to save logs to a file. Defaults to True.
        add_date (bool, optional): Whether to add a date to the log file name. Defaults to False.
        console (bool, optional): Whether to log to the console. Defaults to True.
        fmt (str, optional): The log message format. Defaults to None.
        fltr (logging.Filter, optional): The log filter. Defaults to None.

    Returns:
        logging.Logger: The configured logger.

    Example:
        ```python
        logger = get_custom_logger("app", "my_logger", add_date=True, console=False)
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        ```
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.warn = logger.warning
    fmt = logging.Formatter(
        fmt=fmt or "%(name)-8s :: %(asctime)s :: %(levelname)-8s :: %(message)s"
    )

    if save_to_file:
        if not CONFIG.LOG_PATH.exists():
            CONFIG.LOG_PATH.mkdir(parents=True, exist_ok=True)
        file += datetime.now().strftime("_%Y-%m-%d_%H-%M-%S") if add_date else ""
        file = Path(file).name
        fh = RotatingFileHandler(
            CONFIG.LOG_PATH / f"{file}.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=10,
            encoding="utf-8",
        )
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    if console:
        sh = logging.StreamHandler()
        sh.setFormatter(fmt)
        if fltr:
            sh.addFilter(fltr)
        logger.addHandler(sh)

    return logger


def get_except_details():
    """
    Fetches and formats exception details into a string that can be attached to logging.
    Needs to be called from inside an exception handler.
    """
    # pylint: disable=E0633
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)).replace(
        "\t", "\n"
    )
