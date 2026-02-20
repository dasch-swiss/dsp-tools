from unittest.mock import Mock
from unittest.mock import patch

import pytest

from dsp_tools.commands.get.get import _read_project
from dsp_tools.error.exceptions import BaseError


@pytest.fixture
def mock_connection() -> Mock:
    return Mock()


class TestReadProject:
    """Tests for the _read_project function's regex-based routing logic."""

    def test_shortcode_route(self, mock_connection: Mock) -> None:
        # Shortcode pattern: exactly 4 hex characters [0-9A-F]
        with patch("dsp_tools.commands.get.get.read_project_by_shortcode") as mock_read:
            mock_read.return_value = Mock()
            _read_project(mock_connection, "0001")
            mock_read.assert_called_once_with(mock_connection, "0001")

    def test_shortcode_uppercase_hex(self, mock_connection: Mock) -> None:
        # Uppercase hex letters should match shortcode pattern
        with patch("dsp_tools.commands.get.get.read_project_by_shortcode") as mock_read:
            mock_read.return_value = Mock()
            _read_project(mock_connection, "ABCD")
            mock_read.assert_called_once_with(mock_connection, "ABCD")

    def test_shortname_route(self, mock_connection: Mock) -> None:
        # Shortname pattern: word characters and hyphens
        with patch("dsp_tools.commands.get.get.read_project_by_shortname") as mock_read:
            mock_read.return_value = Mock()
            _read_project(mock_connection, "myproject")
            mock_read.assert_called_once_with(mock_connection, "myproject")

    def test_shortname_with_hyphen(self, mock_connection: Mock) -> None:
        with patch("dsp_tools.commands.get.get.read_project_by_shortname") as mock_read:
            mock_read.return_value = Mock()
            _read_project(mock_connection, "my-project")
            mock_read.assert_called_once_with(mock_connection, "my-project")

    def test_shortname_converted_to_lowercase(self, mock_connection: Mock) -> None:
        # Shortnames are converted to lowercase before calling the API
        with patch("dsp_tools.commands.get.get.read_project_by_shortname") as mock_read:
            mock_read.return_value = Mock()
            _read_project(mock_connection, "MyProject")
            mock_read.assert_called_once_with(mock_connection, "myproject")

    def test_iri_route_http(self, mock_connection: Mock) -> None:
        # IRI pattern: http(s)://host/path
        with patch("dsp_tools.commands.get.get.read_project_by_iri") as mock_read:
            mock_read.return_value = Mock()
            _read_project(mock_connection, "http://rdfh.ch/projects/0001")
            mock_read.assert_called_once_with(mock_connection, "http://rdfh.ch/projects/0001")

    def test_iri_route_https(self, mock_connection: Mock) -> None:
        with patch("dsp_tools.commands.get.get.read_project_by_iri") as mock_read:
            mock_read.return_value = Mock()
            _read_project(mock_connection, "https://admin.dasch.swiss/projects/0001")
            mock_read.assert_called_once_with(mock_connection, "https://admin.dasch.swiss/projects/0001")

    def test_iri_route_with_port(self, mock_connection: Mock) -> None:
        with patch("dsp_tools.commands.get.get.read_project_by_iri") as mock_read:
            mock_read.return_value = Mock()
            _read_project(mock_connection, "http://0.0.0.0:3333/projects/0001")
            mock_read.assert_called_once_with(mock_connection, "http://0.0.0.0:3333/projects/0001")

    def test_invalid_identifier_raises(self, mock_connection: Mock) -> None:
        # Invalid pattern should raise BaseError
        with pytest.raises(BaseError, match="Invalid project identifier"):
            _read_project(mock_connection, "not a valid identifier!")

    def test_invalid_identifier_with_spaces(self, mock_connection: Mock) -> None:
        with pytest.raises(BaseError, match="Invalid project identifier"):
            _read_project(mock_connection, "my project")
