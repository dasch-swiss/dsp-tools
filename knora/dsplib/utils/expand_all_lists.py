from typing import Dict, List

from knora.dsplib.utils.excel_to_json_lists import make_json_list_from_excel, prepare_list_creation


def expand_lists_from_excel(data_model: Dict) -> List[str]:
    """
    Gets all lists from an ontology and expands them to json if they are only referenced via an Excel file

    Args:
        data_model: The data model (json) the lists are read from

    Returns:
        A list of all expanded lists. It can be added to the root node of an ontology as list section.
    """
    # create and add lists from Excel references to the ontology
    lists = data_model['project'].get('lists')

    if not lists:
        return []

    new_lists = []
    for rootnode in lists:
        nodes = rootnode['nodes']
        # check if the folder parameter is used
        if rootnode.get('nodes') and isinstance(nodes, dict) and nodes.get('folder'):
            # get the Excel files from the folder and create the rootnode of the list
            excel_folder = nodes['folder']
            rootnode, excel_files = prepare_list_creation(excel_folder, rootnode.get('name'), rootnode.get('comments'))

            # create the list from the Excel files
            make_json_list_from_excel(rootnode, excel_files)

            new_lists.append(rootnode)
        else:
            new_lists.append(rootnode)

    return new_lists
