from typing import Any

from loguru import logger

from dsp_tools.commands.project.models.project_create_client import ProjectCreateClient
from dsp_tools.commands.project.models.project_definition import ProjectMetadata
from dsp_tools.models.exceptions import UserError


def create_project_on_server(
    project_definition: ProjectMetadata,
    proj_client: ProjectCreateClient,
) -> bool:
    """
    Create the project on the DSP server.

    Raises:
        UserError: if the project already exists on the server
        UserError: if the project cannot be created on the DSP server

    Returns:
        success status (True if everything went smoothly, False otherwise)
    """
    project_designation = f"{project_definition.shortcode} {project_definition.shortname}"
    existing_shortcodes, existing_shortnames = proj_client.get_existing_shortcodes_and_shortnames()
    if project_definition.shortcode in existing_shortcodes or project_definition.shortname in existing_shortnames:
        raise UserError(f"A project with the shortcode/shortname {project_designation} already exists on the server.")
    data: dict[str, Any] = {
        "shortcode": project_definition.shortcode,
        "shortname": project_definition.shortname,
        "longname": project_definition.longname,
        "keywords": project_definition.keywords,
        "selfjoin": False,  # was hardcoded already before
        "status": True,  # was hardcoded already before
    }
    if desc := project_definition.descriptions:
        data["description"] = [{"language": lang, "value": val} for lang, val in desc.items()]

    if not (success := proj_client.create_project(data)):
        raise UserError(f"Cannot create project {project_designation} on DSP server")
    print(f"    Created project {project_designation}")
    logger.info(f"Created project {project_designation}")

    return success
