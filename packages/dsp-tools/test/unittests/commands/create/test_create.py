from pathlib import Path
from unittest.mock import Mock

import pytest

import dsp_tools.commands.create.create as create_module
from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.create.exceptions import DspAdminAccountNotInProjectFileError
from dsp_tools.commands.create.models.parsed_project import ParsedProject

PROD_SERVER = "https://api.dasch.swiss"


def test_create_checks_admin_account_before_creating_anything(monkeypatch: pytest.MonkeyPatch) -> None:
    parsed_project = Mock(spec=ParsedProject)
    parsed_project.project_metadata = Mock(shortname="my-proj")
    parsed_project.users = []
    parsed_project.user_memberships = []
    monkeypatch.setattr(create_module, "parse_and_validate_project", Mock(return_value=(parsed_project, [])))
    execute_create = Mock()
    monkeypatch.setattr(create_module, "_execute_create", execute_create)
    creds = ServerCredentials(user="user@example.com", password="pw", server=PROD_SERVER)
    with pytest.raises(DspAdminAccountNotInProjectFileError):
        create_module.create(Path("project.json"), creds, exit_if_exists=False)
    execute_create.assert_not_called()
