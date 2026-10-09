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
    is_prod_like = is_prod_like_server(server)

    match is_dsp_admin_account, is_prod_like:
        case True, _:
            return
        case False, True:
            msg = "You are uploading data to a prod-like server."
            raise DspAdminAccountError(msg)
        case False, False:
            msg = "You are uploading data on a test environment."
            warnings.warn(DspToolsMissingAdminAccountWarning(msg))
        case _:
            raise UnreachableCodeError()
