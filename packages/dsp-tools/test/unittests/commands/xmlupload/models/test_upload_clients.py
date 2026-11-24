from pathlib import Path
from unittest.mock import Mock

from dsp_tools.commands.xmlupload.models.bitstream_info import BitstreamInfo
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileBitstream
from dsp_tools.commands.xmlupload.models.upload_clients import DspIngestAssetClient
from dsp_vre.clients.exceptions import InvalidIngestFileNameError
from dsp_vre.clients.exceptions import PermanentConnectionError
from dsp_vre.clients.ingest import DspIngestClientLive
from dsp_vre.clients.ingest import IngestResponse

FILE_INFO = ProcessedFileBitstream(value="images/test.jpg", res_id="res_1")


def _make_asset_client(ingest_client: Mock) -> DspIngestAssetClient:
    return DspIngestAssetClient(ingest_client=ingest_client, imgdir="imgdir")


class TestDspIngestAssetClient:
    def test_success_returns_bitstream_info(self) -> None:
        ingest_client = Mock(spec=DspIngestClientLive)
        ingest_client.ingest.return_value = IngestResponse(internal_filename="internal.jp2")
        result = _make_asset_client(ingest_client).get_bitstream_info(FILE_INFO, None)
        assert result == BitstreamInfo("internal.jp2", None)
        ingest_client.ingest.assert_called_once_with(Path("imgdir/images/test.jpg"))

    def test_invalid_filename_returns_none(self) -> None:
        ingest_client = Mock(spec=DspIngestClientLive)
        ingest_client.ingest.side_effect = InvalidIngestFileNameError()
        assert _make_asset_client(ingest_client).get_bitstream_info(FILE_INFO, None) is None

    def test_permanent_connection_error_returns_none(self) -> None:
        ingest_client = Mock(spec=DspIngestClientLive)
        ingest_client.ingest.side_effect = PermanentConnectionError()
        assert _make_asset_client(ingest_client).get_bitstream_info(FILE_INFO, None) is None
