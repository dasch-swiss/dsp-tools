import logging
from collections.abc import Iterator

import pytest


class _ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


@pytest.fixture
def notice_records() -> Iterator[list[logging.LogRecord]]:
    """Collects the records of "dsp_vre" and of "dsp_vre.notices", which does not propagate to the parent."""
    handler = _ListHandler()
    loggers = [logging.getLogger("dsp_vre"), logging.getLogger("dsp_vre.notices")]
    old_level = loggers[0].level
    for lg in loggers:
        lg.addHandler(handler)
    loggers[0].setLevel(logging.DEBUG)
    yield handler.records
    loggers[0].setLevel(old_level)
    for lg in loggers:
        lg.removeHandler(handler)
