from pathlib import Path

from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.create.communicate_problems import print_problem_collection
from dsp_tools.commands.create.create_on_server.lists import create_lists
from dsp_tools.commands.create.models.parsed_project import ParsedList
from dsp_tools.commands.create.models.parsed_project import ParsedProjectMetadata
from dsp_tools.commands.create.project_validate import parse_and_validate_lists
from dsp_tools.error.exceptions import ProjectNotFoundError
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_YELLOW
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT


def create_lists_only(project_file: Path, creds: ServerCredentials) -> bool:
    problems, metadata, parsed_lists = parse_and_validate_lists(project_file)
    if problems:
        print_problem_collection(problems)
        return False
    return _handle_parsed_project_result(metadata, parsed_lists, creds)


def _handle_parsed_project_result(
    project_metadata: ParsedProjectMetadata, parsed_lists: list[ParsedList], creds: ServerCredentials
) -> bool:
    match parsed_lists:
        case list():
            return _execute_list_creation(project_metadata, parsed_lists, creds)
        case None:
            msg = "Your file did not contain any lists, therefore no lists were created on the server."
            logger.info(msg)
            print(BACKGROUND_BOLD_YELLOW + msg + RESET_TO_DEFAULT)
            return False
        case _:
            raise UnreachableCodeError()


def _execute_list_creation(
    project_metadata: ParsedProjectMetadata, parsed_lists: list[ParsedList], creds: ServerCredentials
) -> bool:
    auth = AuthenticationClientLive(creds.server, creds.user, creds.password)
    project_info = ProjectClientLive(creds.server, auth)
    try:
        project_iri = project_info.get_project_iri(project_metadata.shortcode)
    except ProjectNotFoundError:
        # we want a more precise error message
        raise ProjectNotFoundError(
            f"This commands adds lists to an existing project. "
            f"The project with the shortcode {project_metadata.shortcode} does not exist on this server. "
            f"If you wish to create an entire project, please use the `create` command without the flag."
        ) from None

    _, problems = create_lists(parsed_lists, project_metadata.shortcode, auth, project_iri)
    if problems:
        print_problem_collection(problems)
        return False
    return True
