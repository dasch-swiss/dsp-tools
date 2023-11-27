# pylint: disable=missing-class-docstring
# ruff: noqa: D102 (undocumented-public-method)

from dsp_tools.commands.xmlupload.upload_config import UploadConfig, _transform_server_url_to_foldername


class TestTransformServerUrlToFoldername:
    def test_prod_env(self) -> None:
        servername = "https://api.dasch.swiss/"
        expected = "dasch.swiss"
        result = _transform_server_url_to_foldername(servername)
        assert result == expected

    def test_test_env(self) -> None:
        servername = "https://api.test.dasch.swiss/"
        expected = "test.dasch.swiss"
        result = _transform_server_url_to_foldername(servername)
        assert result == expected

    def test_project_server(self) -> None:
        servername = "http://api.082e-test-server.dasch.swiss/"
        expected = "082e-test-server.dasch.swiss"
        result = _transform_server_url_to_foldername(servername)
        assert result == expected

    def test_local_http(self) -> None:
        servername = "http://0.0.0.0:12345"
        expected = "localhost"
        result = _transform_server_url_to_foldername(servername)
        assert result == expected

    def test_local_https(self) -> None:
        servername = "https://0.0.0.0:80/"
        expected = "localhost"
        result = _transform_server_url_to_foldername(servername)
        assert result == expected


def test_save_location() -> None:
    server = "dasch.swiss"
    shortcode = "9999"
    onto_name = "testonto"
    expected_path = f"/.dsp-tools/xmluploads/{server}/{shortcode}/{onto_name}"
    config = UploadConfig()
    config_with_save_location = config.with_server_info(
        server=server,
        shortcode=shortcode,
        onto_name=onto_name,
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
