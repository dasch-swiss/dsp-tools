from unittest.mock import patch

import pytest

from dsp_tools.error.exceptions import DaschEmployeeAccountUsedForUploadError
from dsp_tools.utils.dsp_user_account_check import check_for_dsp_employee_account_email_for_data_upload
from dsp_tools.utils.dsp_user_account_check import dsp_admin_account_email
from dsp_tools.utils.dsp_user_account_check import is_dsp_employee_account_email

PROD_SERVER = "https://api.dasch.swiss"
LOCAL_SERVER = "http://0.0.0.0:3333"
EMPLOYEE_EMAIL = "jane.doe@dasch.swiss"
PROMPT_TARGET = "dsp_tools.utils.dsp_user_account_check.prompt_until_valid_answer"


def test_dsp_admin_account_email() -> None:
    assert dsp_admin_account_email("my-proj") == "my-proj@admin.dasch.swiss"


@pytest.mark.parametrize(
    ("email", "expected"),
    [
        (EMPLOYEE_EMAIL, True),
        ("my-proj@admin.dasch.swiss", False),
        ("someone@example.com", False),
    ],
)
def test_is_dsp_employee_account_email(email: str, expected: bool) -> None:
    assert is_dsp_employee_account_email(email) == expected


@pytest.mark.parametrize("server", [PROD_SERVER, LOCAL_SERVER])
@pytest.mark.parametrize("email", ["my-proj@admin.dasch.swiss", "someone@example.com"])
def test_check_for_data_upload_non_employee_account(email: str, server: str) -> None:
    with patch(PROMPT_TARGET, side_effect=AssertionError("must not prompt")):
        check_for_dsp_employee_account_email_for_data_upload(email, server)


def test_check_for_data_upload_employee_account_local() -> None:
    with patch(PROMPT_TARGET, side_effect=AssertionError("must not prompt")):
        check_for_dsp_employee_account_email_for_data_upload(EMPLOYEE_EMAIL, LOCAL_SERVER)


def test_check_for_data_upload_employee_account_prod_confirmed() -> None:
    with patch(PROMPT_TARGET, return_value="yes"):
        check_for_dsp_employee_account_email_for_data_upload(EMPLOYEE_EMAIL, PROD_SERVER)


def test_check_for_data_upload_employee_account_prod_declined() -> None:
    with patch(PROMPT_TARGET, return_value="no"):
        with pytest.raises(DaschEmployeeAccountUsedForUploadError, match="DaSCH employee account"):
            check_for_dsp_employee_account_email_for_data_upload(EMPLOYEE_EMAIL, PROD_SERVER)


def test_check_for_data_upload_employee_account_prod_non_interactive(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("dsp_tools.utils.interactive.stdin_is_interactive", return_value=False):
        with pytest.raises(DaschEmployeeAccountUsedForUploadError, match="DaSCH employee account"):
            check_for_dsp_employee_account_email_for_data_upload(EMPLOYEE_EMAIL, PROD_SERVER)
    assert "aborting upload" in capsys.readouterr().out
