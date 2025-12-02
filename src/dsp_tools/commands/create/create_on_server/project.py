import sys

from loguru import logger

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata
from dsp_tools.commands.create.serialisation.project import serialise_project
from dsp_tools.error.exceptions import ProjectNotFoundError
from dsp_tools.error.exceptions import UnableToCreateProject
from dsp_tools.utils.ansi_colors import BOLD_RED
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.request_utils import is_server_error


def create_project(project: ParsedProjectMetadata, auth: AuthenticationClient) -> str:
    client = ProjectClientLive(auth.server, auth)
    try:
        project_iri = client.get_project_iri(project.shortcode)
        msg = (
            f"A project with the shortcode '{project.shortcode}' already exists on the server. "
            f"Do you wish to continue uploading additional information? [y/n] "
        )
        logger.debug(msg)
        resp = None
        while resp not in ["y", "n"]:
            resp = input(BOLD_RED + msg + RESET_TO_DEFAULT)
        if resp == "y":
            return project_iri
        logger.debug("Response 'n' abort command.")
        sys.exit(1)

    except ProjectNotFoundError:
        logger.debug("No project with the shortcode exists. Continuing creating the project.")

    serialised = serialise_project(project)
    result = client.post_new_project(serialised)
    if isinstance(result, str):
        return result
    if is_server_error(result):
        msg = "Due to a server error it was not possible to create the project. "
    else:
        msg = "Unable to create project."
    raise UnableToCreateProject(
        msg + f"\nOriginal response code: {result.status_code}\nOriginal response message: {result.text}"
    )
