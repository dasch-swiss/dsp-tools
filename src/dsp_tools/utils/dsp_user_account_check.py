from dsp_tools.error import DaschEmployeeAccountUsedForUploadError
from dsp_tools.utils.data_formats.uri_util import is_prod_like_server
from dsp_tools.utils.interactive import prompt_until_valid_answer


def dsp_admin_account_email(shortname: str) -> str:
    return f"{shortname}@admin.dasch.swiss"


def is_correct_dsp_admin_account_email(shortname: str, email: str) -> bool:
    return email == dsp_admin_account_email(shortname)


def is_dsp_employee_acount_email(email: str) -> bool:
    return email.endswith("@dasch.swiss")


def check_for_dsp_employee_account_email_for_data_upload(email: str, server: str) -> None:
    if not is_dsp_employee_acount_email(email):
        return
    rule = (
        "It is mandatory that each project has an admin account for DaSCH internal usage. "
        f"On prod-like servers, data uploads must be done by an account named {dsp_admin_account_email('[shortname]')}."
    )
    if is_prod_like_server(server):
        msg = (
            "You are uploading data on a prod-like server and are using your DaSCH employee account.\n"
            f"{rule} Are you sure you want to continue? [yes / no] "
        )
        answer = prompt_until_valid_answer(
            prompt=msg,
            valid_answers=["yes", "no"],
            non_interactive_answer="no",
            non_interactive_notice="Using a DaSCH employee account for an upload on a prod-like server, "
            "aborting upload.",
        )
        if answer.lower() == "no":
            raise DaschEmployeeAccountUsedForUploadError(
                "User aborted upload due to using a DaSCH employee acount on a prod-like server."
            )
    return
