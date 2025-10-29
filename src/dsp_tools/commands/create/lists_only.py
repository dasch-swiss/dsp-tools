from pathlib import Path
from typing import Any

from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.clients.project_client_live import ProjectInfoClientLive
from dsp_tools.commands.create.communicate_problems import print_problem_collection
from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.parsing.parse_project import parse_lists_only
from dsp_tools.error.exceptions import ProjectNotFoundError
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_CYAN
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT


def create_lists_only(project_file_as_path_or_parsed: str | Path | dict[str, Any], creds: ServerCredentials) -> bool:
    result = parse_lists_only(project_file_as_path_or_parsed)
    if isinstance(result, CollectedProblems):
        print_problem_collection(result)
        return False
    project_metadata, parsed_lists = result
    if not parsed_lists:
        msg = "Your file did not contain any lists, therefore no lists were created on the server."
        logger.info(msg)
        print(BACKGROUND_BOLD_CYAN + msg + RESET_TO_DEFAULT)
        return True
    project_info = ProjectInfoClientLive(creds.server)
    project_iri = project_info.get_project_iri(project_metadata.shortcode)
    if not project_iri:
        raise ProjectNotFoundError(
            f"This commands adds lists to an existing project. "
            f"The project with the shortcode {project_metadata.shortcode} does not exist on this server. "
            f"If you wish to create an entire project use the `create` command without the flag."
        )
