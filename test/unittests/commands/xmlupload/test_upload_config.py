import pytest

from dsp_tools.commands.xmlupload.upload_config import _transform_server_url_to_foldername


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


if __name__ == "__main__":
    pytest.main([__file__])
