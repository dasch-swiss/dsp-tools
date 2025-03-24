from typing import Any
from typing import cast

from loguru import logger

from dsp_tools.commands.project.models.project_definition import ProjectDefinition
from dsp_tools.commands.project.models.project_definition import ProjectMetadata
from dsp_tools.error.exceptions import InputError


def parse_project_json(
    project_json: dict[str, Any],
) -> ProjectDefinition:
    """
    Takes a validated project json and parses the content.

    Args:
        project_json: json of the project

    Returns:
        Object with the parsed information
    """
    metadata = ProjectMetadata(
        shortcode=project_json["project"]["shortcode"],
        shortname=project_json["project"]["shortname"],
        longname=project_json["project"]["longname"],
        keywords=project_json["project"].get("keywords"),
        descriptions=project_json["project"].get("descriptions"),
    )
    all_lists: list[dict[str, Any]] | None = project_json["project"].get("lists")
    all_ontos = _parse_all_ontos(project_json, all_lists)

    groups = project_json["project"].get("groups")
    users = project_json["project"].get("users")
    return ProjectDefinition(metadata=metadata, ontologies=all_ontos, lists=all_lists, groups=groups, users=users)


def _parse_all_ontos(project_json: dict[str, Any], all_lists: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    all_ontos: list[dict[str, Any]] = project_json["project"]["ontologies"]
    if all_lists is None:
        return all_ontos
    # rectify the "hlist" of the "gui_attributes" of the properties
    for onto in all_ontos:
        if onto.get("properties"):
            onto["properties"] = _rectify_hlist_of_properties(
                lists=all_lists,
                properties=onto["properties"],
            )
    return all_ontos


def _rectify_hlist_of_properties(
    lists: list[dict[str, Any]],
    properties: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Check the "hlist" of the "gui_attributes" of the properties.
    If they don't refer to an existing list name,
    check if there is a label of a list that corresponds to the "hlist".
    If so, rectify the "hlist" to refer to the name of the list instead of the label.

    Args:
        lists: "lists" section of the JSON project definition
        properties: "properties" section of one of the ontologies of the JSON project definition

    Raises:
        InputError: if the "hlist" refers to no existing list name or label

    Returns:
        the rectified "properties" section
    """

    if not lists or not properties:
        return properties

    existing_list_names = [lst["name"] for lst in lists]

    for prop in properties:
        if not prop.get("gui_attributes"):
            continue
        if not prop["gui_attributes"].get("hlist"):
            continue
        list_name = prop["gui_attributes"]["hlist"] if prop["gui_attributes"]["hlist"] in existing_list_names else None
        if list_name:
            continue

        deduced_list_name = None
        for root_node in lists:
            if prop["gui_attributes"]["hlist"] in root_node["labels"].values():
                deduced_list_name = cast(str, root_node["name"])
        if deduced_list_name:
            msg = (
                f"INFO: Property '{prop['name']}' references the list '{prop['gui_attributes']['hlist']}' "
                f"which is not a valid list name. "
                f"Assuming that you meant '{deduced_list_name}' instead."
            )
            logger.warning(msg)
            print(msg)
        else:
            msg = f"Property '{prop['name']}' references an unknown list: '{prop['gui_attributes']['hlist']}'"
            logger.error(msg)
            raise InputError(f"ERROR: {msg}")
        prop["gui_attributes"]["hlist"] = deduced_list_name

    return properties
