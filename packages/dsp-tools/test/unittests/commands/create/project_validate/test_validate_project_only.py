from pathlib import Path
from unittest.mock import Mock

import pytest

import dsp_tools.commands.create.project_validate as project_validate_module
from dsp_tools.commands.create.exceptions import DspAdminAccountNotInProjectFileError
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.models.parsed_project import ParsedUser
from dsp_tools.commands.create.models.parsed_project import ParsedUserMemberShipInfo
from dsp_tools.commands.create.project_validate import validate_project_only
from dsp_tools.error.custom_warnings import DspAdminAccountNotInProjectFileWarning

PROD_SERVER = "https://api.dasch.swiss"
LOCAL_SERVER = "http://0.0.0.0:3333"
SHORTNAME = "my-proj"
PASSED_VALIDATION = "passed validation"


def _patch_parsing(
    monkeypatch: pytest.MonkeyPatch, users: list[ParsedUser], memberships: list[ParsedUserMemberShipInfo]
) -> None:
    parsed_project = Mock(spec=ParsedProject)
    parsed_project.project_metadata = Mock(shortname=SHORTNAME)
    parsed_project.users = users
    parsed_project.user_memberships = memberships
    monkeypatch.setattr(project_validate_module, "parse_and_validate_project", Mock(return_value=(parsed_project, [])))


def test_validate_project_only_stops_before_reporting_success(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _patch_parsing(monkeypatch, [], [])
    with pytest.raises(DspAdminAccountNotInProjectFileError):
        validate_project_only(Path("project.json"), PROD_SERVER)
    assert PASSED_VALIDATION not in capsys.readouterr().out


def test_validate_project_only_warns_on_a_server_that_is_not_prod_like(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _patch_parsing(monkeypatch, [], [])
    with pytest.warns(DspAdminAccountNotInProjectFileWarning):
        assert validate_project_only(Path("project.json"), LOCAL_SERVER)
    assert PASSED_VALIDATION in capsys.readouterr().out


def test_validate_project_only_with_admin_account(monkeypatch: pytest.MonkeyPatch) -> None:
    users = [ParsedUser("admin", f"{SHORTNAME}@admin.dasch.swiss", "Given", "Family", "pw", "en")]
    _patch_parsing(monkeypatch, users, [ParsedUserMemberShipInfo("admin", True, [])])
    assert validate_project_only(Path("project.json"), PROD_SERVER)
