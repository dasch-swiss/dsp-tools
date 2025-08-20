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

    _log_file: Path | None = field(default=None, init=False)
    _warnings_file: Path = field(default=Path("warnings.log"), init=False)
    _instance: Self | None = None  # class variable for singleton pattern

    @classmethod
    def get_instance(cls) -> Self:
        """Get the singleton instance of LoggerService."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def configure(self) -> None:
        """
        Configure the log files. Currently, there are three sinks:
          - timestamp_logging.log in ~/.dsp-tools/logs/ contains the entire stack-trace
          - warnings.log in the cwd only with level warning and higher for the user (no stack-trace)
            OR a complete logging.log file with the stack-trace if configured in the .env
          - print output on the terminal, formatted the same as the warnings.log
        """
        logger.remove()  # If this is not removed, the default formatting is also printed out on the terminal

        text_format = "<level>{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}</level>"
        rotation_size = "100 MB"
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        self._log_file = (self._make_and_get_logs_directory() / f"{timestamp}_logging.log").absolute()

        logger.add(
            sink=self._log_file,
            format=text_format,
            backtrace=True,
            diagnose=True,
        )

        save_additional_log = str(os.getenv("DSP_TOOLS_SAVE_ADDITIONAL_LOG_FILE_IN_CWD", "false")).lower() == "true"
        if save_additional_log:
            logger.add(
                sink=Path("logging.log"),
                format=text_format,
                backtrace=True,
                diagnose=True,
                rotation=rotation_size,
                retention=2,  # when starting a new one, the old one shouldn't be deleted immediately
            )
        else:
            logger.add(
                sink=self._warnings_file,
                level="WARNING",
                format=text_format,
                backtrace=False,
                diagnose=False,
                rotation=rotation_size,
                retention=2,  # when starting a new one, the old one shouldn't be deleted immediately
            )

    def get_log_file(self) -> Path:
        """Get the path to the log file. As a fallback, return the parent directory."""
        if self._log_file is None:
            return self._make_and_get_logs_directory()
        return self._log_file

    def get_warnings_file(self) -> Path:
        """Get the path to the warnings file."""
        return self._warnings_file

    def _make_and_get_logs_directory(self) -> Path:
        """Get the base .dsp-tools directory, creating it if it doesn't exist."""
        base_dir = Path.home() / ".dsp-tools" / "logs"
        base_dir.mkdir(exist_ok=True, parents=True)
        return base_dir


def get_log_file() -> Path:
    """Convenience function to get the path to the current log file."""
    logger_service = LoggerService.get_instance()
    return logger_service.get_log_file()


def get_warnings_file() -> Path:
    """Convenience function to get the path to the warnings log file."""
    logger_service = LoggerService.get_instance()
    return logger_service.get_warnings_file()


def trigger_initial_logging_setup() -> None:
    """
    Initial configuration of the logger service. Has to be called before any logging is done.
    """
    logger_service = LoggerService.get_instance()
    logger_service.configure()
