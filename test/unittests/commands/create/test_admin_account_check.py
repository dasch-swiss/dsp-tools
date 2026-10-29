import re
import warnings
from unittest.mock import Mock

import pytest

from dsp_tools.commands.create.admin_account_check import check_dsp_admin_account_exists
from dsp_tools.commands.create.exceptions import DspAdminAccountNotInProjectFileError
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.models.parsed_project import ParsedUser
from dsp_tools.commands.create.models.parsed_project import ParsedUserMemberShipInfo
from dsp_tools.error.custom_warnings import DspAdminAccountNotInProjectFileWarning

PROD_SERVER = "https://api.dasch.swiss"
LOCAL_SERVER = "http://0.0.0.0:3333"
SHORTNAME = "my-proj"
ADMIN_EMAIL = "my-proj@admin.dasch.swiss"

NO_USER_WITH_ADMIN_EMAIL = "has no user with the email"
USER_NOT_ADMIN = "is not a project admin"


def _user(username: str, email: str) -> ParsedUser:
    return ParsedUser(username, email, "Given", "Family", "pw", "en")


def _membership(username: str, is_admin: bool) -> ParsedUserMemberShipInfo:
    return ParsedUserMemberShipInfo(username, is_admin, [])


def _project(users: list[ParsedUser], memberships: list[ParsedUserMemberShipInfo]) -> ParsedProject:
    project = Mock(spec=ParsedProject)
    project.project_metadata = Mock(shortname=SHORTNAME)
    project.users = users
    project.user_memberships = memberships
    return project


PROBLEMS = [
    pytest.param([], [], NO_USER_WITH_ADMIN_EMAIL, id="no users"),
    pytest.param(
        [_user("other", "other@example.com")],
        [_membership("other", True)],
        NO_USER_WITH_ADMIN_EMAIL,
        id="no user with the admin email",
    ),
    pytest.param(
        [_user("other", "other@example.com"), _user("admin", ADMIN_EMAIL)],
        [_membership("other", True), _membership("admin", False)],
        USER_NOT_ADMIN,
        id="admin email without admin rights, other user is admin",
    ),
    pytest.param(
        [_user("admin", ADMIN_EMAIL)],
        [],
        USER_NOT_ADMIN,
        id="admin email without membership",
    ),
]


@pytest.mark.parametrize("server", [PROD_SERVER, LOCAL_SERVER])
def test_check_admin_account_with_admin_rights(server: str) -> None:
    users = [_user("other", "other@example.com"), _user("admin", ADMIN_EMAIL)]
    memberships = [_membership("other", False), _membership("admin", True)]
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        check_dsp_admin_account_exists(_project(users, memberships), server)


@pytest.mark.parametrize(("users", "memberships", "problem"), PROBLEMS)
def test_check_admin_account_problem_prod(
    users: list[ParsedUser], memberships: list[ParsedUserMemberShipInfo], problem: str
) -> None:
    with pytest.raises(DspAdminAccountNotInProjectFileError) as exc_info:
        check_dsp_admin_account_exists(_project(users, memberships), PROD_SERVER)
    message = str(exc_info.value)
    assert problem in message
    assert ADMIN_EMAIL in message
    assert "'users' section" in message
    assert "run the command again" in message
    assert "upload" not in message


@pytest.mark.parametrize(("users", "memberships", "problem"), PROBLEMS)
def test_check_admin_account_problem_local(
    users: list[ParsedUser], memberships: list[ParsedUserMemberShipInfo], problem: str
) -> None:
    with pytest.warns(DspAdminAccountNotInProjectFileWarning, match=re.escape(problem)):
        check_dsp_admin_account_exists(_project(users, memberships), LOCAL_SERVER)
