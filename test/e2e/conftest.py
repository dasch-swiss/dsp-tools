import shutil
from typing import Iterator

import pytest

from test.e2e.setup_testcontainers import INGEST_DB
from test.e2e.setup_testcontainers import SIPI_IMAGES
from test.e2e.setup_testcontainers import TMP_INGEST
from test.e2e.setup_testcontainers import TMP_SIPI


@pytest.fixture(scope="package", autouse=True)
def _tidy_up_artifacts() -> Iterator[None]:
    """Tidy up artifacts after each test, to prevent cluttering the local clone of the repo."""
    yield
    shutil.rmtree(SIPI_IMAGES, ignore_errors=True)
    shutil.rmtree(TMP_INGEST, ignore_errors=True)
    shutil.rmtree(TMP_SIPI, ignore_errors=True)
    shutil.rmtree(INGEST_DB, ignore_errors=True)
