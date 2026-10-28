import warnings

from dsp_tools.error.custom_warnings import DspAdminAccountNotUsedForUploadWarning
from dsp_tools.error.exceptions import DspAdminAccountNotUsedForUploadError
from dsp_tools.utils.data_formats.uri_util import is_prod_like_server


def dsp_admin_account_email(shortname: str) -> str:
    return f"{shortname}@admin.dasch.swiss"


def is_correct_dsp_admin_account_email(shortname: str, email: str) -> bool:
    return email == dsp_admin_account_email(shortname)


def check_for_dsp_admin_account_email_for_data_upload(shortname: str, email: str, server: str) -> None:
    if is_correct_dsp_admin_account_email(shortname, email):
        return
    rule = (
        "It is mandatory that each project has an admin account for DaSCH internal usage. "
        f"On prod-like servers, data uploads must be done by an account named {dsp_admin_account_email('[shortname]')}."
    )
    if is_prod_like_server(server):
        msg = (
            "You are uploading data on a prod-like server.\n"
            f"{rule} Please create such an account and re-start the upload."
        )
        raise DspAdminAccountNotUsedForUploadError(msg)
    msg = (
        "You are uploading data without the project admin account.\n"
        f"{rule} Other accounts are only permitted in test environments."
    )
    warnings.warn(DspAdminAccountNotUsedForUploadWarning(msg))
