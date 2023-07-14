import json
from pathlib import Path
from typing import Any, Union


def _update_prop(prop: dict[str, Any]) -> dict[str, Any]:
    """
    If a property's "gui_element" is "SimpleText" or "Textarea",
    replace the object "TextValue" with "UnformattedTextValue".
    If the gui_element is "Richtext",
    replace the object "TextValue" with "FormattedTextValue".
    In both cases, remove the "gui_element" and "gui_attributes" afterwards.

    Args:
        prop: a text property

    Returns:
        the updated property
    """
    gui_element = prop.get("gui_element")
    if gui_element not in ["SimpleText", "Textarea", "Richtext"]:
        return prop

    if gui_element == "Richtext":
        prop["object"] = "FormattedTextValue"
    else:
        prop["object"] = "UnformattedTextValue"

    del prop["gui_element"]
    if prop.get("gui_attributes"):
        del prop["gui_attributes"]

    return prop


def _update_project(project: dict[str, Any]) -> dict[str, Any]:
    """
    Update all text properties in the project definition.

    Args:
        project: parsed JSON project definition

    Returns:
        modified project definition
    """
    for onto in project["project"]["ontologies"]:
        for prop in onto["properties"]:
            if prop["object"] == "TextValue":
                prop = _update_prop(prop=prop)
    return project


def _write_file(
    project: dict[str, Any],
    old_path: Path,
) -> None:
    """
    Write the updated project definition to a new file.

    Args:
        project: updated project definition as Python dict
        old_path: path to the original project definition file
    """
    new_path = old_path.parent / f"{old_path.stem}_updated.json"
    with open(new_path, mode="w", encoding="utf-8") as jsonFile:
        json.dump(project, jsonFile, indent=4, ensure_ascii=False)
    print(f"wrote file to '{new_path}'")


def update_text_properties(path: Union[str, Path]) -> bool:
    """
    Given a path to a JSON project definition file,
    change the text properties to the new format:
    Depending on the gui_element,
    replace the object "TextValue" with either "UnformattedTextValue" or "FormattedTextValue",
    then remove the gui_element.

    Args:
        path: path to the JSON project definition file

    Returns:
        success status
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as jsonFile:
        project = json.load(jsonFile)

    project = _update_project(project=project)
    _write_file(project=project, old_path=path)

    return True
