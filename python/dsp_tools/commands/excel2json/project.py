import json
from pathlib import Path
from typing import Any

import regex

from dsp_tools.commands.excel2json.lists import excel2lists
from dsp_tools.commands.excel2json.properties import excel2properties
from dsp_tools.commands.excel2json.resources import excel2resources
from dsp_tools.models.exceptions import UserError


def excel2json(
    data_model_files: str,
    path_to_output_file: str,
) -> bool:
    """
    Converts a folder containing Excel files into a JSON data model file. The folder must be structured like this:

    ::

        data_model_files
        |-- lists
        |   |-- de.xlsx
        |   `-- en.xlsx
        `-- onto_name (onto_label)
            |-- properties.xlsx
            `-- resources.xlsx

    The names of the files must be exactly like in the example. The folder "lists" can be missing, because it is
    optional to have lists in a DSP project. Only XLSX files are allowed.

    Args:
        data_model_files: path to the folder (called "data_model_files" in the example)
        path_to_output_file: path to the file where the output JSON file will be saved

    Raises:
        UserError: if something went wrong
        BaseError: if something went wrong

    Returns:
        True if everything went well
    """

    listfolder, onto_folders = _validate_folder_structure_get_filenames(data_model_files)

    overall_success, project = _create_project_json(data_model_files, listfolder, onto_folders)

    with open(path_to_output_file, "w", encoding="utf-8") as f:
        json.dump(project, f, indent=4, ensure_ascii=False)

    print(f"JSON project file successfully saved at {path_to_output_file}")

    return overall_success


def _validate_folder_structure_get_filenames(data_model_files: str) -> tuple[list[Path], list[Path]]:
    if not Path(data_model_files).is_dir():
        raise UserError(f"ERROR: {data_model_files} is not a directory.")
    folder = [x for x in Path(data_model_files).glob("*") if _non_hidden(x)]
    processed_files = []
    onto_folders, processed_onto = _get_validate_onto_folder(data_model_files, folder)
    processed_files.extend(processed_onto)
    listfolder, processed_lists = _get_validate_list_folder(data_model_files, folder)
    processed_files.extend(processed_lists)
    if len(onto_folders) + len(listfolder) != len(folder):
        raise UserError(
            f"The only allowed subfolders in '{data_model_files}' are 'lists' "
            "and folders that match the pattern 'onto_name (onto_label)'"
        )
    print("The following files will be processed:")
    print(*(f" - {file}" for file in processed_files), sep="\n")
    return listfolder, onto_folders


def _get_validate_list_folder(data_model_files: str, folder: list[Path]) -> tuple[list[Path], list[str]]:
    processed_files: list[str] = []
    listfolder = [x for x in folder if x.is_dir() and x.name == "lists"]
    if listfolder:
        listfolder_contents = [x for x in Path(listfolder[0]).glob("*") if _non_hidden(x)]
        if not all(regex.search(r"(de|en|fr|it|rm).xlsx", file.name) for file in listfolder_contents):
            raise UserError(
                f"The only files allowed in '{data_model_files}/lists' are en.xlsx, de.xlsx, fr.xlsx, it.xlsx, rm.xlsx"
            )
        processed_files = [f"{data_model_files}/lists/{file.name}" for file in listfolder_contents]
    return listfolder, processed_files


def _get_validate_onto_folder(data_model_files: str, folder: list[Path]) -> tuple[list[Path], list[str]]:
    processed_files = []
    onto_folders = [x for x in folder if x.is_dir() and regex.search(r"([\w.-]+) \(([\w.\- ]+)\)", x.name)]
    if not onto_folders:
        raise UserError(
            f"'{data_model_files}' must contain at least one subfolder named after the pattern 'onto_name (onto_label)'"
        )
    for onto_folder in onto_folders:
        contents = sorted([x.name for x in Path(onto_folder).glob("*") if _non_hidden(x)])
        if contents != ["properties.xlsx", "resources.xlsx"]:
            raise UserError(
                f"ERROR: '{data_model_files}/{onto_folder.name}' must contain one file 'properties.xlsx' "
                "and one file 'resources.xlsx', but nothing else."
            )
        processed_files.extend([f"{data_model_files}/{onto_folder.name}/{file}" for file in contents])
    return onto_folders, processed_files


def _non_hidden(path: Path) -> bool:
    return not regex.search(r"^(\.|~\$).+", path.name)


def _create_project_json(
    data_model_files: str, listfolder: list[Path], onto_folders: list[Path]
) -> tuple[bool, dict[str, Any]]:
    overall_success = True
    lists, success = excel2lists(excelfolder=f"{data_model_files}/lists") if listfolder else (None, True)
    if not success:
        overall_success = False
    ontologies, success = _get_ontologies(data_model_files, onto_folders)
    if not success:
        overall_success = False
    schema = "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/project.json"
    project = {
        "prefixes": {"": ""},
        "$schema": schema,
        "project": {
            "shortcode": "",
            "shortname": "",
            "longname": "",
            "descriptions": {"en": ""},
            "keywords": [""],
        },
    }
    if lists:
        project["project"]["lists"] = lists  # type: ignore[index]
    project["project"]["ontologies"] = ontologies  # type: ignore[index]
    return overall_success, project


def _get_ontologies(data_model_files: str, onto_folders: list[Path]) -> tuple[list[dict[str, Any]], bool]:
    success = True
    ontologies = []
    for onto_folder in onto_folders:
        name, label = regex.search(r"([\w.-]+) \(([\w.\- ]+)\)", onto_folder.name).groups()  # type: ignore[union-attr]
        resources, success1 = excel2resources(f"{data_model_files}/{onto_folder.name}/resources.xlsx")
        properties, success2 = excel2properties(f"{data_model_files}/{onto_folder.name}/properties.xlsx")
        if not success1 or not success2:
            success = False
        ontologies.append(
            {
                "name": name,
                "label": label,
                "properties": properties,
                "resources": resources,
            }
        )
    return ontologies, success
