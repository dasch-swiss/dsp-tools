import warnings

from dsp_tools.error.custom_warnings import DspToolsMissingAdminAccountWarning
from dsp_tools.error.exceptions import DspAdminAccountError
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.utils.data_formats.uri_util import is_prod_like_server


def is_correct_dsp_admin_account_email(shortname: str, email: str) -> bool:
    expected = f"{shortname}@admin.dasch.swiss"
    return email == expected


def check_for_dsp_admin_account_email_for_data_upload(shortname: str, email: str, server: str) -> None:
    is_dsp_admin_account = is_correct_dsp_admin_account_email(shortname, email)
    enforce_dsp_admin_account(is_dsp_admin_account, server, activity="uploading data")


def enforce_dsp_admin_account(has_dsp_admin_account: bool, server: str, activity: str) -> None:
    is_prod_like = is_prod_like_server(server)

    match has_dsp_admin_account, is_prod_like:
        case True, _:
            return
        case False, True:
            msg = f"You are {activity} on a prod-like server."
            raise DspAdminAccountError(msg)
        case False, False:
            msg = f"You are {activity} on a test environment."
            warnings.warn(DspToolsMissingAdminAccountWarning(msg))
        case _:
            raise UnreachableCodeError()
