import logging


class ColorFormatter(logging.Formatter):
    """
    Logging colored formatter, adapted from
     - https://alexandra-zaharia.github.io/posts/make-your-own-custom-color-formatter-with-python-logging/
     - https://stackoverflow.com/a/56944256/3638629
    """

    orange = "\x1b[38;5;208m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt: str) -> None:
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.fmt,
            logging.INFO: self.fmt,
            logging.WARNING: self.orange + "WARNING: " + self.fmt + self.reset,
            logging.ERROR: self.red + "ERROR: " + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + "CRITICAL: " + self.fmt + self.reset
        }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
