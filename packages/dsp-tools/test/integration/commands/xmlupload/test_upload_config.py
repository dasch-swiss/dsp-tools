import contextlib
from pathlib import Path

import pytest

from dsp_tools.commands.xmlupload.upload_config import UploadConfig


def test_save_location() -> None:
    server = "dasch.swiss"
    expected_path = Path(Path.home() / f".dsp-tools/xmluploads/{server}/resumable/latest.pkl")
    config_with_save_location = UploadConfig().with_server_info(server=server, shortcode="1234")
    diagnostics = config_with_save_location.diagnostics
    assert expected_path == diagnostics.save_location
    # in case these folders didn't exist before: tidy up
    with contextlib.suppress(OSError):
        diagnostics.save_location.parent.rmdir()  # raises OSError if the folder is not empty
        diagnostics.save_location.parent.parent.rmdir()


if __name__ == "__main__":
    pytest.main([__file__])
