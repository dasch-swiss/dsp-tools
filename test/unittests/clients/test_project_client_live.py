from unittest.mock import Mock
from unittest.mock import patch

import pytest
import requests

from dsp_tools.clients.project_client_live import ProjectInfoClientLive
from dsp_tools.error.exceptions import DspToolsRequestException
from dsp_tools.error.exceptions import FatalNonOkApiResponseCode


@pytest.fixture
def api_url() -> str:
    return "http://0.0.0.0:3333"


@pytest.fixture
def project_client(api_url: str) -> ProjectInfoClientLive:
    return ProjectInfoClientLive(api_url=api_url)


class TestProjectInfoClientLive:
    def test_get_project_iri_success(self, project_client: ProjectInfoClientLive) -> None:
        mock_response = Mock(status_code=200, ok=True, headers={})
        mock_response.json.return_value = {
            "project": {
                "id": "http://rdfh.ch/projects/0001",
                "shortcode": "0001",
                "shortname": "test-project",
            }
        }
        with patch("dsp_tools.clients.project_client_live.requests.get", return_value=mock_response) as mock_get:
            result = project_client.get_project_iri("0001")
        assert result == "http://rdfh.ch/projects/0001"
        assert mock_get.call_args[0][0] == f"{project_client.api_url}/admin/projects/shortcode/0001"

    def test_get_project_iri_not_found(self, project_client: ProjectInfoClientLive) -> None:
        mock_response = Mock(status_code=404, ok=False, headers={}, text="")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.project_client_live.requests.get", return_value=mock_response):
            result = project_client.get_project_iri("9999")
        assert result is None

    def test_get_project_iri_timeout(self, project_client: ProjectInfoClientLive) -> None:
        with patch("dsp_tools.clients.project_client_live.requests.get", side_effect=requests.ReadTimeout("Timeout")):
            with pytest.raises(DspToolsRequestException):
                project_client.get_project_iri("0001")

    def test_get_project_iri_other_error(self, project_client: ProjectInfoClientLive) -> None:
        mock_response = Mock(status_code=500, ok=False, headers={}, text="Internal Server Error")
        mock_response.json.return_value = {}
        with patch("dsp_tools.clients.project_client_live.requests.get", return_value=mock_response):
            with pytest.raises(FatalNonOkApiResponseCode):
                project_client.get_project_iri("0001")


if __name__ == "__main__":
    pytest.main([__file__])
