import shutil
from typing import Iterator

import pytest

from test.e2e.tools_testcontainers import SIPI_PATH_IMAGES


@pytest.fixture(scope="package")
def _tidy_up_sipi_path() -> Iterator[None]:
    """
    Tidy up the SIPi path after each test.
    """
    SIPI_PATH_IMAGES.mkdir()
    yield
    shutil.rmtree(SIPI_PATH_IMAGES)
