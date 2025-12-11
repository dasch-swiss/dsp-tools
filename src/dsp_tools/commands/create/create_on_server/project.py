import sys

from loguru import logger

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.project_client import ProjectClient
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.create.exceptions import UnableToCreateProjectError
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata
from dsp_tools.commands.create.serialisation.project import serialise_project
from dsp_tools.error.exceptions import ProjectNotFoundError
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_YELLOW
from dsp_tools.setup.ansi_colors import BOLD
from dsp_tools.setup.ansi_colors import BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.request_utils import is_server_error


def create_project(project: ParsedProjectMetadata, auth: AuthenticationClient, exit_if_exists: bool) -> str:
    client = ProjectClientLive(auth.server, auth)
    try:
        project_iri = client.get_project_iri(project.shortcode)
        _exit_if_create_should_not_continue(project.shortcode, exit_if_exists)
        return project_iri

    except ProjectNotFoundError:
        logger.debug("No project with the shortcode exists. Continuing creating the project.")
        return _create_project_on_server(project, client)


def _exit_if_create_should_not_continue(shortcode: str, exit_if_exists: bool) -> None:
    if exit_if_exists:
        msg = (
            "The project already exists on the server and the flag '--exit-if-exists' was set. "
            "The process is aborted without further uploads."
        )
        logger.info(msg)
        print(BACKGROUND_BOLD_YELLOW + msg + RESET_TO_DEFAULT)
        sys.exit(0)

    msg = (
        f"A project with the shortcode '{shortcode}' already exists on the server. "
        f"Do you wish to continue uploading additional information? [y/n] "
    )
    logger.debug(msg)
    resp = None
    while resp not in ["y", "n"]:
        resp = input(BOLD_RED + msg + RESET_TO_DEFAULT)
    if resp == "n":
        logger.debug("Response 'n' abort command.")
        sys.exit(1)


def _create_project_on_server(project: ParsedProjectMetadata, client: ProjectClient) -> str:
    info_str = f"Creating project '{project.shortname}' ({project.shortcode})"
    print(BOLD + info_str + RESET_TO_DEFAULT)
    logger.debug(info_str)
    serialised = serialise_project(project)
    result = client.post_new_project(serialised)
    if isinstance(result, str):
        return result
    if is_server_error(result):
        msg = "Due to a server error it was not possible to create the project. "
    else:
        msg = "Unable to create project."
    raise UnableToCreateProjectError(
        msg + f"\nOriginal response code: {result.status_code}\nOriginal response message: {result.text}"
    )
