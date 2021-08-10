from typing import List, Dict

from knora.dsplib.utils.excel_to_json_lists import prepare_list_creation, make_json_list_from_excel


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
    new_lists = []
    if lists is not None:
        for rootnode in lists:
            # check if the folder parameter is used
            if rootnode.get('nodes') is not None and isinstance(rootnode['nodes'], dict) and rootnode['nodes'].get(
                'folder') is not None:
                # get the Excel files from the folder and crate the rootnode of the list
                excel_folder = rootnode['nodes']['folder']
                rootnode, excel_files = prepare_list_creation(excel_folder, rootnode.get('name'))

                # create the list from the Excel files
                make_json_list_from_excel(rootnode, excel_files)

                new_lists.append(rootnode)
            else:
                new_lists.append(rootnode)

    return new_lists
