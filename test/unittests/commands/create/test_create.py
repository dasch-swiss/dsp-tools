import pytest

from dsp_tools.commands.create.create import _check_that_dsp_admin_account_exists
from dsp_tools.commands.create.models.parsed_project import ParsedUser
from dsp_tools.error.custom_warnings import DspToolsMissingAdminAccountWarning
from dsp_tools.error.exceptions import DspAdminAccountError

PROD_SERVER = "https://api.dasch.swiss"
LOCAL_SERVER = "http://0.0.0.0:3333"


def _user(email: str) -> ParsedUser:
    return ParsedUser("usr", email, "Given", "Family", "pw", "en")


def test_check_admin_account_exists() -> None:
    users = [_user("other@example.com"), _user("my-proj@admin.dasch.swiss")]
    _check_that_dsp_admin_account_exists("my-proj", users, PROD_SERVER)


def test_check_admin_account_missing_prod() -> None:
    with pytest.raises(DspAdminAccountError):
        _check_that_dsp_admin_account_exists("my-proj", [_user("other@example.com")], PROD_SERVER)


def test_check_admin_account_missing_local() -> None:
    with pytest.warns(DspToolsMissingAdminAccountWarning):
        _check_that_dsp_admin_account_exists("my-proj", [_user("other@example.com")], LOCAL_SERVER)
