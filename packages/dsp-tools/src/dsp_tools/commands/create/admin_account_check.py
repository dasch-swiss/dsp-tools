import warnings

from dsp_tools.commands.create.exceptions import DspAdminAccountNotInProjectFileError
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.models.parsed_project import ParsedUser
from dsp_tools.commands.create.models.parsed_project import ParsedUserMemberShipInfo
from dsp_tools.error.custom_warnings import DspAdminAccountNotInProjectFileWarning
from dsp_tools.utils.data_formats.uri_util import is_prod_like_server
from dsp_tools.utils.dsp_user_account_check import dsp_admin_account_email


def check_dsp_admin_account_exists(project: ParsedProject, server: str) -> None:
    """
    Check that the project file defines the project admin account with admin rights.
    On a server that is not prod-like, emit a warning instead of raising.

    Args:
        project: the parsed project file
        server: the URL of the DSP server

    Raises:
        DspAdminAccountNotInProjectFileError: if the account is missing or has no admin rights on a prod-like server
    """
    admin_email = dsp_admin_account_email(project.project_metadata.shortname)
    problem = _find_problem(admin_email, project.users, project.user_memberships)
    if problem is None:
        return
    rule = (
        "It is mandatory that each project has an admin account for DaSCH internal usage. "
        f"On prod-like servers, the 'users' section of the project file must therefore contain the user {admin_email} "
        'with "projects": [":admin", ":member"].'
    )
    if is_prod_like_server(server):
        msg = f"{problem}\n{rule} Please correct the 'users' section and run the command again."
        raise DspAdminAccountNotInProjectFileError(msg)
    msg = f"{problem}\n{rule} On other servers, this is only a warning."
    warnings.warn(DspAdminAccountNotInProjectFileWarning(msg))


def _find_problem(admin_email: str, users: list[ParsedUser], memberships: list[ParsedUserMemberShipInfo]) -> str | None:
    admin_usernames = {usr.username for usr in users if usr.email == admin_email}
    if not admin_usernames:
        return f"The 'users' section of the project file has no user with the email {admin_email}."
    if not any(memb.is_admin for memb in memberships if memb.username in admin_usernames):
        return f"The user with the email {admin_email} is not a project admin: ':admin' is missing in its 'projects'."
    return None
