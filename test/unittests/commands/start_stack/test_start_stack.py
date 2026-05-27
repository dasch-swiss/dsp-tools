from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
import yaml
from requests import RequestException

from dsp_tools.commands.start_stack.exceptions import StartStackInputError
from dsp_tools.commands.start_stack.start_stack import StackConfiguration
from dsp_tools.commands.start_stack.start_stack import StackHandler
from dsp_tools.commands.start_stack.start_stack import _read_env_var
from dsp_tools.error.exceptions import PermanentConnectionError


@pytest.fixture
def latest_handler(tmp_path: Path) -> StackHandler:
    """
    StackHandler configured for latest_dev_version=True, with side effects bypassed.
    The real __init__ calls _get_url_prefix() (a network call) and creates directories
    under ~/.dsp-tools/. This fixture bypasses __init__ and injects the private attributes
    directly, substituting tmp_path for the docker path to keep tests isolated.
    """
    config = StackConfiguration(latest_dev_version=True)
    with patch.object(StackHandler, "__init__", lambda _self, _cfg: None):
        handler = StackHandler.__new__(StackHandler)
        handler._StackHandler__stack_configuration = config  # type: ignore[attr-defined]
        handler._StackHandler__url_prefix = "https://raw.githubusercontent.com/dasch-swiss/dsp-api/main/"  # type: ignore[attr-defined]
        handler._StackHandler__docker_path_of_user = tmp_path  # type: ignore[attr-defined]
        handler._StackHandler__localhost_url = "http://0.0.0.0"  # type: ignore[attr-defined]
    return handler


class TestGetFusekiImageForLatest:
    def test_happy_path(self, latest_handler: StackHandler) -> None:
        good_compose = yaml.dump(
            {
                "services": {
                    "db": {"image": "daschswiss/apache-jena-fuseki:5.5.0-3"},
                    "api": {"image": "daschswiss/knora-api:latest"},
                }
            }
        )
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = good_compose
        with patch("requests.get", return_value=mock_response):
            result = latest_handler._get_fuseki_image_for_latest()
        assert result == "daschswiss/apache-jena-fuseki:5.5.0-3"

    def test_missing_db_key(self, latest_handler: StackHandler) -> None:
        compose_without_db = yaml.dump({"services": {"api": {"image": "daschswiss/knora-api:latest"}}})
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.text = compose_without_db
        with patch("requests.get", return_value=mock_response):
            with pytest.raises(StartStackInputError):
                latest_handler._get_fuseki_image_for_latest()

    def test_non_ok_response(self, latest_handler: StackHandler) -> None:
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        with patch("requests.get", return_value=mock_response):
            with pytest.raises(PermanentConnectionError):
                latest_handler._get_fuseki_image_for_latest()

    def test_request_exception(self, latest_handler: StackHandler) -> None:
        with patch("requests.get", side_effect=RequestException("connection failed")):
            with pytest.raises(PermanentConnectionError):
                latest_handler._get_fuseki_image_for_latest()


class TestWriteOverrideFile:
    def _write_initial_override(self, tmp_path: Path) -> None:
        override = {
            "services": {
                "api": {"image": "daschswiss/knora-api:latest"},
                "sipi": {"image": "daschswiss/knora-sipi:latest"},
                "db": {"image": "daschswiss/apache-jena-fuseki:latest"},
                "ingest": {"image": "daschswiss/dsp-ingest:latest"},
            }
        }
        (tmp_path / "docker-compose.override.yml").write_text(
            yaml.dump(override, default_flow_style=False, sort_keys=False), encoding="utf-8"
        )

    def test_only_db_is_changed(self, latest_handler: StackHandler, tmp_path: Path) -> None:
        self._write_initial_override(tmp_path)
        latest_handler._patch_fuseki_version_in_override_file("daschswiss/apache-jena-fuseki:5.5.0-3")
        result = yaml.safe_load((tmp_path / "docker-compose.override.yml").read_text(encoding="utf-8"))
        assert result["services"]["db"]["image"] == "daschswiss/apache-jena-fuseki:5.5.0-3"
        assert result["services"]["api"]["image"] == "daschswiss/knora-api:latest"
        assert result["services"]["sipi"]["image"] == "daschswiss/knora-sipi:latest"
        assert result["services"]["ingest"]["image"] == "daschswiss/dsp-ingest:latest"

    def test_file_location(self, latest_handler: StackHandler, tmp_path: Path) -> None:
        self._write_initial_override(tmp_path)
        latest_handler._patch_fuseki_version_in_override_file("daschswiss/apache-jena-fuseki:5.5.0-3")
        assert (tmp_path / "docker-compose.override.yml").exists()


class TestReadEnvVar:
    def test_returns_value_for_existing_key(self) -> None:
        content = "RELEASE=2026.05.01\nAPI=v35.8.1\nAPP=v13.3.0\nDB=5.5.0-3\n"
        assert _read_env_var(content, "API") == "v35.8.1"

    def test_skips_comment_and_blank_lines(self) -> None:
        content = "# Auto-managed header\n\n  \nAPI=v35.8.1\n"
        assert _read_env_var(content, "API") == "v35.8.1"

    def test_strips_surrounding_whitespace(self) -> None:
        content = "  API = v35.8.1  \n"
        assert _read_env_var(content, "API") == "v35.8.1"

    def test_raises_when_key_missing(self) -> None:
        with pytest.raises(StartStackInputError):
            _read_env_var("RELEASE=2026.05.01\nAPP=v13.3.0\n", "API")

    def test_raises_when_content_empty(self) -> None:
        with pytest.raises(StartStackInputError):
            _read_env_var("", "API")
