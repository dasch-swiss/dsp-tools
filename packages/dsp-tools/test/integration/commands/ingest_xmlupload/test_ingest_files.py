from collections.abc import Iterator
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from dsp_tools.clients.bulk_ingest_client import BulkIngestClient
from dsp_tools.commands.ingest_xmlupload.ingest_files.ingest_files import _retrieve_mapping
from dsp_tools.error.exceptions import UnreachableCodeError

MAPPING_CSV = "original,derivative\nfoo.jpg,0001.jp2\n"

SLEEP_TARGET = "dsp_tools.commands.ingest_xmlupload.ingest_files.ingest_files.sleep"
SPINNER_TARGET = "dsp_tools.commands.ingest_xmlupload.ingest_files.ingest_files.get_green_bouncy_ball_spinner"


@pytest.fixture
def sleep_mock() -> Iterator[MagicMock]:
    with patch(SLEEP_TARGET) as mock_sleep, patch(SPINNER_TARGET):
        yield mock_sleep


def _client_yielding(*results: object) -> MagicMock:
    client = MagicMock(spec=BulkIngestClient)
    client.retrieve_mapping_generator.return_value = iter(results)
    return client


def test_retrieve_mapping_completes_after_polling(sleep_mock: MagicMock) -> None:
    client = _client_yielding(True, True, False, MAPPING_CSV)
    result = _retrieve_mapping(client)
    assert result == MAPPING_CSV
    assert sleep_mock.call_count == 3


def test_retrieve_mapping_immediate_completion(sleep_mock: MagicMock) -> None:
    client = _client_yielding(MAPPING_CSV)
    result = _retrieve_mapping(client)
    assert result == MAPPING_CSV
    assert sleep_mock.call_count == 0


@pytest.mark.usefixtures("sleep_mock")
def test_retrieve_mapping_unexpected_value_raises() -> None:
    client = _client_yielding(None)
    with pytest.raises(UnreachableCodeError):
        _retrieve_mapping(client)


if __name__ == "__main__":
    pytest.main([__file__])
