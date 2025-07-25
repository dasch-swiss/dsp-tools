import csv
import hashlib
import os
import sys
from pathlib import Path

from loguru import logger


def _get_instance_id() -> str:
    """Generate a unique instance ID based on the Python executable path and working directory."""
    # Use both the Python executable path and current working directory
    # This ensures different virtual environments get different log files
    # but the same venv in the same location gets the same log file
    key_string = f"{sys.executable}:{os.getcwd()}"
    return hashlib.md5(key_string.encode(), usedforsecurity=False).hexdigest()[:8]


def _get_base_directory() -> Path:
    """Get the base .dsp-tools directory, creating it if it doesn't exist."""
    base_dir = Path.home() / ".dsp-tools"
    base_dir.mkdir(exist_ok=True)
    return base_dir


def _get_instance_mapping_file() -> Path:
    """Get the path to the instance mapping CSV file."""
    return _get_base_directory() / "instance2directory_mapping.csv"


def _get_instance_directory() -> Path:
    """Get the instance-specific directory, creating it if it doesn't exist."""
    instance_id = _get_instance_id()
    current_dir = os.getcwd()

    # Append current mapping to CSV file
    mapping_file = _get_instance_mapping_file()
    try:
        with open(mapping_file, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([instance_id, current_dir])
    except OSError:
        # If we can't save the mapping, continue without it
        pass

    # Create and return instance directory
    instance_dir = _get_base_directory() / instance_id
    instance_dir.mkdir(exist_ok=True)
    return instance_dir


LOGGER_SAVEPATH = (_get_instance_directory() / "logging.log").absolute()
WARNINGS_SAVEPATH = Path("warnings.log")


def logger_config() -> None:
    """
    This function configures the log files.
    Currently, there are three sinks:
    - instance-specific logger.log in ~/.dsp-tools/ for development purposes
    - warnings.log in the cwd only with level warning and higher for the user (no stack-trace)
    - print output on the terminal, formatted the same as the warnings.log
    """
    # If this is not removed, the default formatting is also printed out on the terminal
    logger.remove()

    text_format = "<level>{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}</level>"
    rotation_size = "100 MB"
    retention_number = 30

    logger.add(
        sink=LOGGER_SAVEPATH,
        format=text_format,
        backtrace=True,
        diagnose=True,
        rotation=rotation_size,
        retention=retention_number,
    )

    logger.add(
        sink=WARNINGS_SAVEPATH,
        level="WARNING",
        format=text_format,
        backtrace=False,
        diagnose=False,
        rotation=rotation_size,
        retention=10,
    )
