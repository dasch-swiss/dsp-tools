import shutil
from typing import Iterator

import pytest

from test.e2e.tools_testcontainers import SIPI_PATH_IMAGES


@pytest.fixture(scope="package", autouse=True)
def _tidy_up_sipi_path() -> Iterator[None]:
    """
    Tidy up the SIPI path after each test.
    """
    yield
    shutil.rmtree(SIPI_PATH_IMAGES, ignore_errors=True)
