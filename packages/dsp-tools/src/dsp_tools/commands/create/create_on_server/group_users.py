from typing import Any

from loguru import logger
from tqdm import tqdm

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.group_user_clients import GroupClient
from dsp_tools.clients.group_user_clients import UserClient
from dsp_tools.clients.group_user_clients_live import UserClientLive
from dsp_tools.commands.create.models.create_problems import CollectedProblems
from dsp_tools.commands.create.models.create_problems import CreateProblem
from dsp_tools.commands.create.models.create_problems import UploadProblem
from dsp_tools.commands.create.models.create_problems import UploadProblemType
from dsp_tools.commands.create.models.parsed_project import ParsedGroup
from dsp_tools.commands.create.models.parsed_project import ParsedUser
from dsp_tools.commands.create.models.parsed_project import ParsedUserMemberShipInfo
from dsp_tools.commands.create.models.server_project_info import GroupNameToIriLookup
from dsp_tools.commands.create.models.server_project_info import ServerUser
from dsp_tools.commands.create.models.server_project_info import ServerUserLookup
from dsp_tools.commands.create.models.server_project_info import UserNameToIriLookup
from dsp_tools.commands.create.serialisation.project import serialise_one_group
from dsp_tools.commands.create.serialisation.project import serialise_one_user_for_creation
from dsp_tools.setup.ansi_colors import BOLD
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT


def create_users(
    users: list[ParsedUser],
    user_memberships: list[ParsedUserMemberShipInfo],
    group_lookup: GroupNameToIriLookup,
    auth: AuthenticationClient,
    project_iri: str,
) -> CollectedProblems | None:
    print(BOLD + "Processing user section:" + RESET_TO_DEFAULT)
    client = UserClientLive(auth.server, auth)
    server_users = _construct_server_user_lookup(client.get_all_users())
    user_to_iri, problems = _create_all_users(users, client, server_users)
    membership_problems = _add_all_memberships(user_memberships, user_to_iri, group_lookup, client, project_iri)
    problems.extend(membership_problems)
    if problems:
        return CollectedProblems("During the creation of the users the following problems occurred:", problems)
    return None


def _construct_server_user_lookup(all_users: list[dict[str, Any]]) -> ServerUserLookup:
    server_users = [ServerUser(iri=usr["id"], username=usr["username"], email=usr["email"]) for usr in all_users]
    return ServerUserLookup(
        by_username={usr.username: usr for usr in server_users},
        by_email={usr.email: usr for usr in server_users},
    )


def _create_all_users(
    users: list[ParsedUser], client: UserClient, server_users: ServerUserLookup
) -> tuple[UserNameToIriLookup, list[CreateProblem]]:
    problems: list[CreateProblem] = []
    user_to_iri = UserNameToIriLookup()
    progress_bar = tqdm(users, desc="    Creating users", dynamic_ncols=True)
    logger.debug("Creating users")
    for usr in progress_bar:
        result = _create_one_user(usr, client, server_users)
        if isinstance(result, UploadProblem):
            problems.append(result)
        else:
            user_to_iri.add_iri(usr.username, result)
    return user_to_iri, problems


def _create_one_user(user: ParsedUser, client: UserClient, server_users: ServerUserLookup) -> str | UploadProblem:
    existing = _resolve_existing_user(user, server_users)
    if existing is not None:
        return existing
    serialised_user = serialise_one_user_for_creation(user)
    if new_iri := client.post_new_user(serialised_user):
        return new_iri
    return UploadProblem(user.username, UploadProblemType.USER_COULD_NOT_BE_CREATED)


def _resolve_existing_user(user: ParsedUser, server_users: ServerUserLookup) -> str | UploadProblem | None:
    """
    Returns the IRI if a server user has the same username and email,
    None if neither the username nor the email exist on the server,
    and a problem if only one of them matches or they match different server users.
    """
    by_username = server_users.by_username.get(user.username)
    by_email = server_users.by_email.get(user.email)
    if by_username is None and by_email is None:
        return None
    if by_username is not None and by_email is not None and by_username.iri == by_email.iri:
        logger.debug(f"User '{user.username}' already exists on the server, using the existing user.")
        return by_username.iri
    return UploadProblem(user.username, UploadProblemType.USER_EXISTS_WITH_DIFFERENT_CREDENTIALS)


def _add_all_memberships(
    memberships: list[ParsedUserMemberShipInfo],
    user_to_iri: UserNameToIriLookup,
    group_lookup: GroupNameToIriLookup,
    client: UserClient,
    project_iri: str,
) -> list[CreateProblem]:
    problems: list[CreateProblem] = []
    progress_bar = tqdm(memberships, desc="    Updating user information", dynamic_ncols=True)
    logger.debug("Updating user information")
    for memb in progress_bar:
        if usr_iri := user_to_iri.get_iri(memb.username):
            result = _add_user_to_project_memberships(memb, usr_iri, project_iri, client)
            problems.extend(result)
            if memb.groups:
                result = _add_user_to_custom_groups(memb, usr_iri, client, group_lookup)
                problems.extend(result)
        else:
            logger.debug(f"IRI of user '{memb.username}' could not be found, no project membership added.")
    return problems


def _add_user_to_project_memberships(
    membership: ParsedUserMemberShipInfo, user_iri: str, project_iri: str, client: UserClient
) -> list[CreateProblem]:
    problems: list[CreateProblem] = []
    membership_good = client.add_user_as_project_member(user_iri, project_iri)
    if not membership_good:
        problems.append(UploadProblem(membership.username, UploadProblemType.PROJECT_MEMBERSHIP_COULD_NOT_BE_ADDED))
    if membership.is_admin:
        good = client.add_user_as_project_admin(user_iri, project_iri)
        if not good:
            problems.append(UploadProblem(membership.username, UploadProblemType.PROJECT_ADMIN_COULD_NOT_BE_ADDED))
    return problems


def _add_user_to_custom_groups(
    membership: ParsedUserMemberShipInfo, user_iri: str, client: UserClient, group_lookup: GroupNameToIriLookup
) -> list[CreateProblem]:
    problems: list[CreateProblem] = []
    groups_not_found = []
    groups_iris = []
    for gr in membership.groups:
        if found := group_lookup.get_iri(gr):
            groups_iris.append(found)
        else:
            groups_not_found.append(gr)
    if groups_iris:
        group_good = client.add_user_to_custom_groups(user_iri, groups_iris)
        if not group_good:
            problems.append(UploadProblem(membership.username, UploadProblemType.USER_COULD_NOT_BE_ADDED_TO_GROUP))
    if groups_not_found:
        problems.append(UploadProblem(membership.username, UploadProblemType.USER_GROUPS_NOT_FOUND))
    return problems


def create_groups(
    groups: list[ParsedGroup],
    group_client: GroupClient,
    project_iri: str,
    group_lookup: GroupNameToIriLookup,
) -> tuple[GroupNameToIriLookup, CollectedProblems | None]:
    problems: list[CreateProblem] = []
    print(BOLD + "Processing group section:" + RESET_TO_DEFAULT)
    progress_bar = tqdm(groups, desc="    Creating groups", dynamic_ncols=True)
    logger.debug("Creating groups")
    for gr in progress_bar:
        if group_lookup.check_exists(gr.name):
            logger.debug(f"Group with the name '{gr.name}' already exists, skipping.")
            continue
        result = _create_one_group(gr, group_client, project_iri)
        if isinstance(result, UploadProblem):
            problems.append(result)
        else:
            group_lookup.add_iri(gr.name, result)
    all_problems = None
    if problems:
        all_problems = CollectedProblems("During the creation of the groups the following problems happened:", problems)
    return group_lookup, all_problems


def _create_one_group(group: ParsedGroup, group_client: GroupClient, project_iri: str) -> str | UploadProblem:
    serialised = serialise_one_group(group, project_iri)
    new_iri = group_client.create_new_group(serialised)
    if new_iri:
        return new_iri
    return UploadProblem(group.name, UploadProblemType.GROUP_COULD_NOT_BE_CREATED)


def get_existing_group_to_iri_lookup(
    group_client: GroupClient, project_iri: str, shortname: str
) -> GroupNameToIriLookup:
    all_groups = group_client.get_all_groups()
    return _construct_group_lookup(all_groups, project_iri, shortname)


def _construct_group_lookup(all_groups: list[dict[str, Any]], project_iri: str, shortname: str) -> GroupNameToIriLookup:
    lookup = GroupNameToIriLookup({}, shortname)
    for group in all_groups:
        group_project_iri = group["project"]["id"]
        if group_project_iri == project_iri:
            lookup.add_iri(group["name"], group["id"])
    return lookup
