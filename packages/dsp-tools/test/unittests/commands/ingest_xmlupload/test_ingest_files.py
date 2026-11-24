from unittest.mock import patch

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.ingest_xmlupload.exceptions import NoFilesUploadedForIngestError
from dsp_tools.commands.ingest_xmlupload.ingest_files.ingest_files import ingest_files
from dsp_vre.clients.exceptions import NoIngestFileFoundError

MODULE = "dsp_tools.commands.ingest_xmlupload.ingest_files.ingest_files"
CREDS = ServerCredentials(server="http://0.0.0.0:3333", user="u", password="p", dsp_ingest_url="http://0.0.0.0:3340")


def test_no_uploaded_files_raises_error_with_upload_files_hint() -> None:
    with patch(f"{MODULE}.AuthenticationClientLive"), patch(f"{MODULE}.BulkIngestClient") as client_cls:
        client_cls.return_value.trigger_ingest_process.side_effect = NoIngestFileFoundError("No files for 0001.")
        with pytest.raises(NoFilesUploadedForIngestError, match=r"No files for 0001\..*'upload-files'"):
            ingest_files(CREDS, "0001")
