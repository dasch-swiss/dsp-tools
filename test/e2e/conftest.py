import pytest

from dsp_tools.utils.logger_config import logger_config

# @pytest.fixture(scope="session", autouse=True)
# def _initialize_logging() -> None:
#     logger_config()


def pytest_sessionstart(session: pytest.Session) -> None:  # noqa: ARG001 (unused function argument)
    """
    Called after the Session object has been created
    and before performing collection and entering the run test loop.
    See https://docs.pytest.org/en/latest/reference/reference.html#pytest.hookspec.pytest_sessionstart.
    """
    logger_config()
