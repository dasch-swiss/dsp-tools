from typing import Any, Union

from knora.dsplib.utils.excel_to_json_lists import make_json_list_from_excel, prepare_list_creation


def expand_lists_from_excel(data_model: dict[str, dict[str, dict[str, dict[str, Any]]]]) -> list[dict[str, Any]]:
    """
    Get all list definitions from a data model and expand them to JSON if they are only referenced via an Excel file

    Args:
        data_model: The data model (JSON) the lists are read from

    Returns:
        A list of all expanded lists. It can be added to the root node of an ontology as lists section.
    """

    if 'project' not in data_model or 'lists' not in data_model['project']:
        return []

    lists = data_model['project']['lists']
    new_lists = []

    for rootnode in lists.values():
        nodes = rootnode.get("nodes")
        # check if the folder parameter is used
        if nodes and isinstance(nodes, dict) and nodes.get("folder"):
            # get the Excel files from the folder and create the rootnode of the list
            prepared_rootnode, excel_files = prepare_list_creation(
                nodes['folder'], rootnode['name'], rootnode['comments']
            )
            # create the list from the Excel files
            finished_list = make_json_list_from_excel(prepared_rootnode, excel_files)
            new_lists.append(finished_list)
        else:
            new_lists.append(rootnode)

    return new_lists
