import logging
from typing import Iterator

import pytest
from _pytest.logging import caplog as _caplog  # noqa: F401 (imported but unused)
from loguru import logger

from dsp_tools.utils.logger_config import logger_config


@pytest.fixture()
def caplog(_caplog: pytest.LogCaptureFixture) -> Iterator[pytest.LogCaptureFixture]:  # noqa: F811 (redefinition)
    class PropagateHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropagateHandler(), format="{message}")
    yield _caplog
    logger.remove(handler_id)


def pytest_sessionstart() -> None:
    """
    Called after the Session object has been created
    and before performing collection and entering the run test loop.
    See https://docs.pytest.org/en/latest/reference/reference.html#pytest.hookspec.pytest_sessionstart.
    """
    logger_config()
