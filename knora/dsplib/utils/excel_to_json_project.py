import json
import os
import re

from knora.dsplib.models.helpers import BaseError
from knora.dsplib.utils.excel_to_json_lists import excel2lists
from knora.dsplib.utils.excel_to_json_properties import excel2properties
from knora.dsplib.utils.excel_to_json_resources import excel2resources


def excel2json(
    data_model_files: str,
    path_to_output_file: str
) -> None:
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

    Returns:
        None
    """

    # validate input
    # --------------
    if not os.path.isdir(data_model_files):
        raise BaseError(f"ERROR: {data_model_files} is not a directory.")
    folder = [x for x in os.scandir(data_model_files) if not re.search(r"^(\.|~\$).+", x.name)]

    processed_files = []
    onto_folders = [x for x in folder if os.path.isdir(x) and re.search(r"([\w.-]+) (\([\w.\- ]+\))", x.name)]
    if len(onto_folders) == 0:
        raise BaseError(f"'{data_model_files}' must contain at least one subfolder named after the pattern "
                        f"'onto_name (onto_label)'")
    for onto_folder in onto_folders:
        contents = sorted([x.name for x in os.scandir(onto_folder) if not re.search(r"^(\.|~\$).+", x.name)])
        if contents != ["properties.xlsx", "resources.xlsx"]:
            raise BaseError(f"ERROR: '{data_model_files}/{onto_folder.name}' must contain one file 'properties.xlsx' "
                            f"and one file 'resources.xlsx', but nothing else.")
        processed_files.extend([f"{data_model_files}/{onto_folder.name}/{file}" for file in contents])

    listfolder = [x for x in folder if os.path.isdir(x) and x.name == "lists"]
    if listfolder:
        listfolder_contents = [x for x in os.scandir(listfolder[0]) if not re.search(r"^(\.|~\$).+", x.name)]
        if not all([re.search(r"(de|en|fr|it|rm).xlsx", file.name) for file in listfolder_contents]):
            raise BaseError(f"The only files allowed in '{data_model_files}/lists' are en.xlsx, de.xlsx, fr.xlsx, "
                            f"it.xlsx, rm.xlsx")
        processed_files = [f"{data_model_files}/lists/{file.name}" for file in listfolder_contents] + processed_files

    if len(onto_folders) + len(listfolder) != len(folder):
        raise BaseError(f"The only allowed subfolders in '{data_model_files}' are 'lists' and folders that match the "
                        f"pattern 'onto_name (onto_label)'")

    print(f"The following files will be processed:")
    [print(f" - {file}") for file in processed_files]


    # create output
    # -------------
    lists = excel2lists(f"{data_model_files}/lists") if listfolder else None

    ontologies = []
    for onto_folder in onto_folders:
        name, label = re.search(r"([\w.-]+) \(([\w.\- ]+)\)", onto_folder.name).groups()
        ontologies.append({
            "name": name,
            "label": label,
            "properties": excel2properties(f"{data_model_files}/{onto_folder.name}/properties.xlsx"),
            "resources": excel2resources(f"{data_model_files}/{onto_folder.name}/resources.xlsx")
        })

    project = {
        "prefixes": {
            "": ""
        },
        "$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/knora/dsplib/schemas/ontology.json",
        "project": {
            "shortcode": "",
            "shortname": "",
            "longname": "",
            "descriptions": {
                "en": ""
            },
            "keywords": [
                ""
            ]
        }
    }
    if lists:
        project["project"]["lists"] = lists
    project["project"]["ontologies"] = ontologies

    with open(path_to_output_file, "w") as f:
        json.dump(project, f, indent=4, ensure_ascii=False)

    print(f"JSON project file successfully saved at {path_to_output_file}")
