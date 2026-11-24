from dsp_tools.error.exceptions import DaschEmployeeAccountUsedForUploadError
from dsp_tools.error.exceptions import OnBehalfOfUserNotProjectAdminAccountError
from dsp_tools.utils.data_formats.uri_util import is_prod_like_server
from dsp_tools.utils.interactive import prompt_until_valid_answer


def dsp_admin_account_email(shortname: str) -> str:
    return f"{shortname}@admin.dasch.swiss"


def is_dsp_employee_account_email(email: str) -> bool:
    return email.endswith("@dasch.swiss")


def check_for_dsp_employee_account_email_for_data_upload(email: str, server: str) -> None:
    if not is_dsp_employee_account_email(email):
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
                "User aborted upload due to using a DaSCH employee account on a prod-like server."
            )
    return


def check_on_behalf_of_user_for_data_import(on_behalf_of_user: str, shortname: str, server: str) -> None:
    expected_account = dsp_admin_account_email(shortname)
    if not is_prod_like_server(server) or on_behalf_of_user == expected_account:
        return
    msg = (
        f"You are importing data on a prod-like server on behalf of '{on_behalf_of_user}'. "
        f"On prod-like servers, data imports must be done on behalf of the account {expected_account}. "
        "Are you sure you want to continue? [yes / no] "
    )
    answer = prompt_until_valid_answer(
        prompt=msg,
        valid_answers=["yes", "no"],
        non_interactive_answer="no",
        non_interactive_notice=(
            f"The flag '--on-behalf-of-user' is not set to {expected_account} "
            "for an import on a prod-like server, aborting import."
        ),
    )
    if answer.lower() == "no":
        raise OnBehalfOfUserNotProjectAdminAccountError(
            f"User aborted the import: on a prod-like server, "
            f"the data must be imported on behalf of {expected_account}."
        )
