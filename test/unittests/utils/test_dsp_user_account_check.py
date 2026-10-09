import pytest

from dsp_tools.error.custom_warnings import DspToolsMissingAdminAccountWarning
from dsp_tools.error.exceptions import DspAdminAccountError
from dsp_tools.utils.dsp_user_account_check import check_for_dsp_admin_account_email_for_data_upload
from dsp_tools.utils.dsp_user_account_check import enforce_dsp_admin_account
from dsp_tools.utils.dsp_user_account_check import is_correct_dsp_admin_account_email

PROD_SERVER = "https://api.dasch.swiss"
LOCAL_SERVER = "http://0.0.0.0:3333"


def test_is_correct_dsp_admin_account_email_correct() -> None:
    assert is_correct_dsp_admin_account_email("my-proj", "my-proj@admin.dasch.swiss")


def test_is_correct_dsp_admin_account_email_wrong() -> None:
    assert not is_correct_dsp_admin_account_email("my-proj", "someone@example.com")


@pytest.mark.parametrize("server", [PROD_SERVER, LOCAL_SERVER])
def test_check_for_data_upload_correct_account(server: str) -> None:
    check_for_dsp_admin_account_email_for_data_upload("my-proj", "my-proj@admin.dasch.swiss", server)


def test_check_for_data_upload_wrong_account_prod() -> None:
    with pytest.raises(DspAdminAccountError):
        check_for_dsp_admin_account_email_for_data_upload("my-proj", "someone@example.com", PROD_SERVER)


def test_check_for_data_upload_wrong_account_local() -> None:
    with pytest.warns(DspToolsMissingAdminAccountWarning):
        check_for_dsp_admin_account_email_for_data_upload("my-proj", "someone@example.com", LOCAL_SERVER)


@pytest.mark.parametrize("server", [PROD_SERVER, LOCAL_SERVER])
def test_enforce_dsp_admin_account_present(server: str) -> None:
    enforce_dsp_admin_account(has_dsp_admin_account=True, server=server, activity="doing something")


def test_enforce_dsp_admin_account_missing_prod() -> None:
    with pytest.raises(DspAdminAccountError, match="You are doing something on a prod-like server"):
        enforce_dsp_admin_account(has_dsp_admin_account=False, server=PROD_SERVER, activity="doing something")


def test_enforce_dsp_admin_account_missing_local() -> None:
    with pytest.warns(DspToolsMissingAdminAccountWarning, match="You are doing something on a test environment"):
        enforce_dsp_admin_account(has_dsp_admin_account=False, server=LOCAL_SERVER, activity="doing something")
