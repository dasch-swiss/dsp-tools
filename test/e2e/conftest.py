import shutil
from typing import Iterator

import pytest

from test.e2e.setup_testcontainers import SIPI_PATH_IMAGES
from test.e2e.setup_testcontainers import SIPI_PATH_TMP_INGEST
from test.e2e.setup_testcontainers import SIPI_PATH_TMP_SIPI


@pytest.fixture(scope="package", autouse=True)
def _tidy_up_sipi_path() -> Iterator[None]:
    """
    Tidy up the SIPI path after each test.
    """
    yield
    shutil.rmtree(SIPI_PATH_IMAGES, ignore_errors=True)
    shutil.rmtree(SIPI_PATH_TMP_INGEST, ignore_errors=True)
    shutil.rmtree(SIPI_PATH_TMP_SIPI, ignore_errors=True)
