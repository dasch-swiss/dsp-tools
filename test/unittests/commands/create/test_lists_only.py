import logging
from unittest.mock import patch

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.exceptions import ProjectNotFoundError
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.create.lists_only import _execute_list_creation
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata

CREDS = ServerCredentials(user="user", password="password", server="http://0.0.0.0:3333")
METADATA = ParsedProjectMetadata(
    shortcode="0001",
    shortname="test",
    longname="test project",
    descriptions={"en": "test"},
    keywords=[],
    enabled_licenses=[],
    data_license=None,
    data_copyright_holder=None,
    default_data_authorship=[],
)


class TestExecuteListCreation:
    def test_project_not_found_logs_and_raises(self, caplog: pytest.LogCaptureFixture) -> None:
        with patch.object(ProjectClientLive, "get_project_iri", side_effect=ProjectNotFoundError("not found")):
            with caplog.at_level(logging.ERROR):
                with pytest.raises(ProjectNotFoundError):
                    _execute_list_creation(METADATA, [], CREDS)
        assert len(caplog.records) == 1
