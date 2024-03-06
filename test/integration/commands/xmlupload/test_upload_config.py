import pytest

from dsp_tools.commands.xmlupload.upload_config import UploadConfig


def test_save_location() -> None:
    server = "dasch.swiss"
    shortcode = "9999"
    onto_name = "testonto"
    expected_path = f"/.dsp-tools/xmluploads/{server}/{shortcode}/{onto_name}"
    config = UploadConfig()
    config_with_save_location = config.with_server_info(
        server=server,
        shortcode=shortcode,
    )
    diagnostics = config_with_save_location.diagnostics
    result = str(diagnostics.save_location)
    assert result.endswith(expected_path)
    try:
        diagnostics.save_location.rmdir()
        diagnostics.save_location.parent.rmdir()
        diagnostics.save_location.parent.parent.rmdir()
    except OSError:
        # there was already stuff in the folder before this test: do nothing
        pass


if __name__ == "__main__":
    pytest.main([__file__])
