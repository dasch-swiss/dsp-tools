import warnings
from pathlib import Path

from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.group_user_clients_live import GroupClientLive
from dsp_tools.clients.permissions_client_live import PermissionsClientLive
from dsp_tools.commands.create.communicate_problems import print_all_problem_collections
from dsp_tools.commands.create.communicate_problems import print_msg_str_for_potential_problematic_circles
from dsp_tools.commands.create.communicate_problems import print_problem_collection
from dsp_tools.commands.create.create_on_server.complete_ontologies import create_ontologies
from dsp_tools.commands.create.create_on_server.default_permissions import create_default_permissions
from dsp_tools.commands.create.create_on_server.group_users import create_groups
from dsp_tools.commands.create.create_on_server.group_users import create_users
from dsp_tools.commands.create.create_on_server.group_users import get_existing_group_to_iri_lookup
from dsp_tools.commands.create.create_on_server.lists import create_lists
from dsp_tools.commands.create.create_on_server.lists import get_existing_lists_on_server
from dsp_tools.commands.create.create_on_server.project import create_project
from dsp_tools.commands.create.exceptions import DspAdminAccountNotInProjectFileError
from dsp_tools.commands.create.models.parsed_project import ParsedProject
from dsp_tools.commands.create.models.parsed_project import ParsedUser
from dsp_tools.commands.create.models.parsed_project import ParsedUserMemberShipInfo
from dsp_tools.commands.create.project_validate import parse_and_validate_project
from dsp_tools.error.custom_warnings import DspAdminAccountNotInProjectFileWarning
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.setup.ansi_colors import BOLD_GREEN
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.setup.dotenv import read_dotenv_if_exists
from dsp_tools.utils.data_formats.uri_util import is_prod_like_server
from dsp_tools.utils.dsp_user_account_check import dsp_admin_account_email

read_dotenv_if_exists()


def create(project_file: Path, creds: ServerCredentials, exit_if_exists: bool) -> bool:
    parsing_result, potential_circles = parse_and_validate_project(project_file, creds.server)
    if potential_circles:
        print_msg_str_for_potential_problematic_circles(potential_circles)

    match parsing_result:
        case ParsedProject():
            _check_that_dsp_admin_account_exists(
                shortname=parsing_result.project_metadata.shortname,
                users=parsing_result.users,
                memberships=parsing_result.user_memberships,
                server=creds.server,
            )
            return _execute_create(parsing_result, creds, exit_if_exists)
        case list():
            print_all_problem_collections(parsing_result)
            return False
        case _:
            raise UnreachableCodeError("Unreachable result of project parsing.")


def _check_that_dsp_admin_account_exists(
    shortname: str, users: list[ParsedUser], memberships: list[ParsedUserMemberShipInfo], server: str
) -> None:
    admin_email = dsp_admin_account_email(shortname)
    if (problem := _find_dsp_admin_account_problem(admin_email, users, memberships)) is None:
        return
    rule = (
        "It is mandatory that each project has an admin account for DaSCH internal usage. "
        f"On prod-like servers, the 'users' section of the project file must therefore contain the user {admin_email} "
        'with "projects": [":admin", ":member"].'
    )
    if is_prod_like_server(server):
        msg = f"{problem}\n{rule} Please correct the 'users' section and run 'create' again."
        raise DspAdminAccountNotInProjectFileError(msg)
    msg = f"{problem}\n{rule} On other servers, this is only a warning."
    warnings.warn(DspAdminAccountNotInProjectFileWarning(msg))


def _find_dsp_admin_account_problem(
    admin_email: str, users: list[ParsedUser], memberships: list[ParsedUserMemberShipInfo]
) -> str | None:
    admin_usernames = {usr.username for usr in users if usr.email == admin_email}
    if not admin_usernames:
        return f"The 'users' section of the project file has no user with the email {admin_email}."
    if not any(memb.is_admin for memb in memberships if memb.username in admin_usernames):
        return f"The user with the email {admin_email} is not a project admin: ':admin' is missing in its 'projects'."
    return None


def _execute_create(parsed_project: ParsedProject, creds: ServerCredentials, exit_if_exists: bool) -> bool:
    msg = "JSON project file is syntactically correct and passed validation."
    print(BOLD_GREEN + "    JSON project file is syntactically correct and passed validation." + RESET_TO_DEFAULT)
    logger.info(msg)
    overall_success = True
    auth = AuthenticationClientLive(creds.server, creds.user, creds.password)

    # create project
    project_iri = create_project(parsed_project.project_metadata, auth, exit_if_exists)

    # create the lists
    if parsed_project.lists:
        list_name_2_iri, list_problems = create_lists(
            parsed_lists=parsed_project.lists,
            shortcode=parsed_project.project_metadata.shortcode,
            auth=auth,
            project_iri=project_iri,
        )
        if list_problems:
            overall_success = False
            print_problem_collection(list_problems)
    else:
        list_name_2_iri = get_existing_lists_on_server(parsed_project.project_metadata.shortcode, auth)

    # create the groups
    group_client = GroupClientLive(creds.server, auth)
    group_lookup = get_existing_group_to_iri_lookup(
        group_client, project_iri, parsed_project.project_metadata.shortname
    )
    if parsed_project.groups:
        group_lookup, group_problems = create_groups(
            groups=parsed_project.groups,
            group_client=group_client,
            project_iri=project_iri,
            group_lookup=group_lookup,
        )
        if group_problems:
            print_problem_collection(group_problems)
            overall_success = False

    if parsed_project.users:
        user_problems = create_users(
            users=parsed_project.users,
            user_memberships=parsed_project.user_memberships,
            group_lookup=group_lookup,
            auth=auth,
            project_iri=project_iri,
        )
        if user_problems:
            print_problem_collection(user_problems)
            overall_success = False

    # create the ontologies
    success, created_iris = create_ontologies(
        parsed_ontologies=parsed_project.ontologies,
        list_name_2_iri=list_name_2_iri,
        project_iri=project_iri,
        shortcode=parsed_project.project_metadata.shortcode,
        auth=auth,
    )
    if not success:
        overall_success = False

    # create the default permissions (DOAPs)
    perm_client = PermissionsClientLive(
        server=auth.server,
        auth=auth,
        project_iri=project_iri,
    )
    success = create_default_permissions(
        perm_client=perm_client,
        validated_permissions=parsed_project.permissions,
        created_iris=created_iris,
    )
    if not success:
        overall_success = False

    # final steps
    if overall_success:
        msg = (
            f"Successfully created project '{parsed_project.project_metadata.shortname}' "
            f"({parsed_project.project_metadata.shortcode}) with all its ontologies. "
            f"There were no problems during the creation process."
        )
        print(f"========================================================\n{msg}")
        logger.info(msg)
    else:
        msg = (
            f"The project '{parsed_project.project_metadata.shortname}' ({parsed_project.project_metadata.shortcode}) "
            f"with its ontologies could be created, "
            f"but during the creation process, some problems occurred. Please carefully check the console output."
        )
        print(f"========================================================\nWARNING: {msg}")
        logger.warning(msg)

    return overall_success
