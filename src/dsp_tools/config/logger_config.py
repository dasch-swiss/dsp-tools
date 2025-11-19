import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def _make_and_get_logs_directory() -> Path:
    """Get the base .dsp-tools directory, creating it if it doesn't exist."""
    base_dir = Path.home() / ".dsp-tools" / "logs"
    base_dir.mkdir(exist_ok=True, parents=True)
    return base_dir


timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]

LOGGER_SAVEPATH = (_make_and_get_logs_directory() / f"{timestamp}_logging.log").absolute()
WARNINGS_SAVEPATH = Path("warnings.log")


def logger_config() -> None:
    """
    This function configures the log files.
    Currently, there are three sinks:
    - timestamp_logging.log in ~/.dsp-tools/logs/ contains the entire stack-trace
    - warnings.log in the cwd only with level warning and higher for the user (no stack-trace)
      OR a complete logging.log file with the stack-trace if configured in the .env
    - print output on the terminal, formatted the same as the warnings.log
    """
    # If this is not removed, the default formatting is also printed out on the terminal
    logger.remove()

    text_format = "<level>{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}</level>"
    rotation_size = "100 MB"

    logger.add(
        sink=LOGGER_SAVEPATH,
        format=text_format,
        backtrace=True,
        diagnose=True,
        delay=True,
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
            delay=True,
        )
    else:
        logger.add(
            sink=WARNINGS_SAVEPATH,
            level="WARNING",
            format=text_format,
            backtrace=False,
            diagnose=False,
            rotation=rotation_size,
            retention=2,
            delay=True,
        )
