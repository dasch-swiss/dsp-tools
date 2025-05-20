import logging
from collections.abc import Iterator

import pytest
from _pytest.logging import caplog as _caplog  # noqa: F401 (imported but unused)
from loguru import logger

from dsp_tools.config.logger_config import logger_config


@pytest.fixture
def caplog(_caplog: pytest.LogCaptureFixture) -> Iterator[pytest.LogCaptureFixture]:  # noqa: F811 (redefinition)
    """
    The caplog fixture that comes shipped with pytest does not support loguru.
    This modified version can be used exactly like the builtin caplog fixture,
    which is documented at https://docs.pytest.org/en/latest/how-to/logging.html#caplog-fixture.
    Credits: https://www.youtube.com/watch?v=eFdVlyAGeZU

    Yields:
        pytest.LogCaptureFixture: The modified caplog fixture.
    """

    class PropagateHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(sink=PropagateHandler(), format="{message}", level="DEBUG")
    yield _caplog
    logger.remove(handler_id)


def pytest_sessionstart() -> None:
    """
    Called after the Session object has been created
    and before performing collection and entering the run test loop.
    See https://docs.pytest.org/en/latest/reference/reference.html#pytest.hookspec.pytest_sessionstart.
    """
    logger_config()
