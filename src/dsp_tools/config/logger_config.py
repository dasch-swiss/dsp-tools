import os
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from pathlib import Path
from typing import Self

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


@dataclass
class LoggerService:
    """Service for managing logger configuration and providing access to log file paths."""

    _current_log_file: Path | None = field(default=None, init=False)
    _warnings_savepath: Path = field(default=Path("warnings.log"), init=False)

    # Class variable for singleton pattern
    _instance: Self | None = None

    @classmethod
    def get_instance(cls) -> Self:
        """Get the singleton instance of LoggerService."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def configure(self) -> None:
        """Configure the logger and set the current log file path."""
        # If this is not removed, the default formatting is also printed out on the terminal
        logger.remove()

        text_format = "<level>{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}</level>"
        rotation_size = "100 MB"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        logger_savepath = (_make_and_get_logs_directory() / f"{timestamp}_logging.log").absolute()

        # Store the log file path for later retrieval
        self._current_log_file = logger_savepath

        logger.add(
            sink=logger_savepath,
            format=text_format,
            backtrace=True,
            diagnose=True,
        )

        additional_log = str(os.getenv("DSP_TOOLS_SAVE_ADDITIONAL_LOG_FILE_IN_CWD"))
        if additional_log.lower() == "true":
            logger.add(
                sink=Path("logging.log"),
                format=text_format,
                backtrace=True,
                diagnose=True,
                rotation=rotation_size,
                retention=2,
            )
        else:
            logger.add(
                sink=self._warnings_savepath,
                level="WARNING",
                format=text_format,
                backtrace=False,
                diagnose=False,
                rotation=rotation_size,
                retention=2,
            )

    def get_current_log_file(self) -> Path:
        """Get the path to the current log file."""
        if self._current_log_file is None:
            return _make_and_get_logs_directory()
        return self._current_log_file

    def get_warnings_file(self) -> Path:
        """Get the path to the warnings log file."""
        return self._warnings_savepath


def _make_and_get_logs_directory() -> Path:
    """Get the base .dsp-tools directory, creating it if it doesn't exist."""
    base_dir = Path.home() / ".dsp-tools" / "logs"
    base_dir.mkdir(exist_ok=True, parents=True)
    return base_dir




def get_current_log_file() -> Path:
    """Get the path to the current log file."""
    logger_service = LoggerService.get_instance()
    return logger_service.get_current_log_file()


def get_warnings_file() -> Path:
    """Get the path to the warnings log file."""
    logger_service = LoggerService.get_instance()
    return logger_service.get_warnings_file()


def logger_config() -> None:
    """
    This function configures the log files.
    Currently, there are three sinks:
    - timestamp_logging.log in ~/.dsp-tools/logs/ contains the entire stack-trace
    - warnings.log in the cwd only with level warning and higher for the user (no stack-trace)
      OR a complete logging.log file with the stack-trace if configured in the .env
    - print output on the terminal, formatted the same as the warnings.log
    """
    logger_service = LoggerService.get_instance()
    logger_service.configure()
