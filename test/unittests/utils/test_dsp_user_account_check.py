import warnings

import pytest

from dsp_tools.error.custom_warnings import DspAdminAccountNotUsedForUploadWarning
from dsp_tools.error.exceptions import DspAdminAccountNotUsedForUploadError
from dsp_tools.utils.dsp_user_account_check import check_for_dsp_admin_account_email_for_data_upload
from dsp_tools.utils.dsp_user_account_check import dsp_admin_account_email
from dsp_tools.utils.dsp_user_account_check import is_correct_dsp_admin_account_email

PROD_SERVER = "https://api.dasch.swiss"
LOCAL_SERVER = "http://0.0.0.0:3333"


def test_dsp_admin_account_email() -> None:
    assert dsp_admin_account_email("my-proj") == "my-proj@admin.dasch.swiss"


def test_is_correct_dsp_admin_account_email_correct() -> None:
    assert is_correct_dsp_admin_account_email("my-proj", "my-proj@admin.dasch.swiss")


def test_is_correct_dsp_admin_account_email_wrong() -> None:
    assert not is_correct_dsp_admin_account_email("my-proj", "someone@example.com")


@pytest.mark.parametrize("server", [PROD_SERVER, LOCAL_SERVER])
def test_check_for_data_upload_correct_account(server: str) -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        check_for_dsp_admin_account_email_for_data_upload("my-proj", "my-proj@admin.dasch.swiss", server)


def test_check_for_data_upload_wrong_account_prod() -> None:
    with pytest.raises(DspAdminAccountNotUsedForUploadError, match="You are uploading data on a prod-like server") as e:
        check_for_dsp_admin_account_email_for_data_upload("my-proj", "someone@example.com", PROD_SERVER)
    assert "[shortname]@admin.dasch.swiss" in str(e.value)
    assert "re-start the upload" in str(e.value)


def test_check_for_data_upload_wrong_account_local() -> None:
    with pytest.warns(DspAdminAccountNotUsedForUploadWarning) as record:
        check_for_dsp_admin_account_email_for_data_upload("my-proj", "someone@example.com", LOCAL_SERVER)
    message = str(record[0].message)
    assert "You are uploading data without the project admin account" in message
    assert "[shortname]@admin.dasch.swiss" in message
    assert "Other accounts are only permitted in test environments" in message
