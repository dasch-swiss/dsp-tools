"""This module handles all the operations which are used for the creation of JSON lists from Excel files."""
import csv
import glob
import json
import os
import re
import unicodedata
from typing import Any, Union, Optional

import jsonschema
from openpyxl import load_workbook
from openpyxl.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet

# Global variables used to ensure that there are no duplicate node names
list_of_lists_of_previous_cell_values: list[list[str]] = []
list_of_previous_node_names: list[str] = []


def get_values_from_excel(
    excelfiles: dict[str, Worksheet],
    base_file: dict[str, Worksheet],
    parentnode: dict[str, Any],
    row: int,
    col: int,
    preval: list[str]
) -> tuple[int, dict[str, Any]]:
    """
    This function calls itself recursively to go through the Excel files. It extracts the cell values and creates
    the JSON list file.

    Args:
        excelfiles: List of Excel files with the values in different languages
        base_file: File name of the base file
        parentnode: Name(s) of the parent node(s) of the current node
        row: The index of the current row of the Excel sheet
        col: The index of the current column of the Excel sheet
        preval: List of previous values, needed to check the consistency of the list hierarchy

    Returns:
        int: Row index for the next loop (current row index minus 1)
        dict: The JSON list up to the current recursion. At the last recursion, this is the final JSON list.
    """
    nodes: list[dict[str, Any]] = []
    currentnode: dict[str, Any] = dict()
    base_file_ws: Worksheet = list(base_file.values())[0]
    cell: Cell = base_file_ws.cell(column=col, row=row)

    for excelfile in excelfiles.values():
        if any((not excelfile['A1'].value, excelfile['B1'].value)):
            print(f'Inconsistency in Excel list: The first row must consist of exactly one value, in cell A1. '
                  f'All other cells of row 1 must be empty.\nInstead, found the following:\n'
                  f'Cell A1: "{excelfile["A1"].value}"\n'
                  f'Cell B1: "{excelfile["B1"].value}"')
            quit()

    if col > 1:
        # append the cell value of the parent node (which is one value to the left of the current cell) to the list of
        # previous values
        preval.append(base_file_ws.cell(column=col-1, row=row).value.strip())

    while cell.value:
        # check if all predecessors in row (values to the left) are consistent with the values in preval list
        for idx, val in enumerate(preval[:-1]):
            if val != base_file_ws.cell(column=idx+1, row=row).value.strip():
                print(f'Inconsistency in Excel list: {val} not equal to '
                      f'{base_file_ws.cell(column=idx+1, row=row).value.strip()}')
                quit()

        # loop through the row until the last (furthest right) value is found
        if base_file_ws.cell(column=col+1, row=row).value:
            row, _ = get_values_from_excel(
                excelfiles=excelfiles,
                base_file=base_file,
                parentnode=currentnode,
                col=col+1,
                row=row,
                preval=preval
            )

        # if value was last in row (no further values to the right), it's a node, continue here
        else:
            # check if there are duplicate nodes (i.e. identical rows), quit the program if so
            new_check_list = preval.copy()
            new_check_list.append(cell.value.strip())
            list_of_lists_of_previous_cell_values.append(new_check_list)

            if contains_duplicates(list_of_lists_of_previous_cell_values):
                print(f'There is at least one duplicate node in the list. Found duplicate in column {cell.column}, '
                      f'row {cell.row}:\n"{cell.value.strip()}"')
                quit(1)

            # create a simplified version of the cell value and use it as name of the node
            nodename = simplify_name(cell.value.strip())
            list_of_previous_node_names.append(nodename)

            # append a number (p.ex. node-name-2) if there are list nodes with identical names
            if contains_duplicates(list_of_previous_node_names):
                n = list_of_previous_node_names.count(nodename)
                if n > 1:
                    nodename = nodename + '-' + str(n)

            # read label values from the other Excel files (other languages)
            labels_dict: dict[str, str] = {}
            for other_lang, ws_other_lang in excelfiles.items():
                cell_value = ws_other_lang.cell(column=col, row=row).value
                if not(isinstance(cell_value, str) and len(cell_value) > 0):
                    print(f'ERROR: Malformed Excel file: The Excel file with the language code "{other_lang}" '
                          f'should have a value in row {row}, column {col}')
                    quit(1)
                else:
                    labels_dict[other_lang] = cell_value.strip()

            # create current node from extracted cell values and append it to the nodes list
            currentnode = {'name': nodename, 'labels': labels_dict}
            nodes.append(currentnode)
            print(f'Added list node: {cell.value.strip()} ({nodename})')

        # go one row down and repeat loop if there is a value
        row += 1
        cell = base_file_ws.cell(column=col, row=row)

    if col > 1:
        preval.pop()

    # add the new nodes to the parentnode
    parentnode['nodes'] = nodes

    return row - 1, parentnode


def make_json_list_from_excel(rootnode: dict[str, Any], excelfile_names: list[str]) -> dict[str, Any]:
    """
    Reads Excel files and makes a JSON list file from them. The JSON can then be used in an ontology that
    is uploaded to the DaSCH Service Platform.

    Args:
        rootnode: The root node of the JSON list
        excelfile_names: A list with all the Excel files to be processed

    Returns:
        The finished list as a dict
    """
    # Define starting point in Excel file
    startrow = 1
    startcol = 1

    # Check if English file is available and take it as base file. Take last one from list of Excel files if English
    # is not available. The node names are later derived from the labels of the base file.
    base_file: dict[str, Worksheet] = dict()
    for filename in excelfile_names:
        if '_en.xlsx' in os.path.basename(filename):
            lang = 'en'
            ws = load_workbook(filename, read_only=True).worksheets[0]
            base_file = {lang: ws}
    if len(base_file) == 0:
        file = excelfile_names[-1]
        lang = os.path.splitext(file)[0].split('_')[-1]
        ws = load_workbook(file, read_only=True).worksheets[0]
        base_file = {lang: ws}

    excelfiles: dict[str, Worksheet] = {}
    for f in excelfile_names:
        lang = os.path.splitext(f)[0].split('_')[-1]
        ws = load_workbook(f, read_only=True).worksheets[0]
        excelfiles[lang] = ws

    _, finished_list = get_values_from_excel(
        excelfiles=excelfiles,
        base_file=base_file,
        parentnode=rootnode,
        row=startrow,
        col=startcol,
        preval=[]
    )

    return finished_list


def contains_duplicates(list_to_check: list[Any]) -> bool:
    """
    Checks if the given list contains any duplicate items.

    Args:
        list_to_check: A list of items to be checked for duplicates

    Returns:
        True if there is a duplicate, false otherwise
    """
    has_duplicates = False

    for item in list_to_check:
        if list_to_check.count(item) > 1:
            has_duplicates = True

    return has_duplicates


def simplify_name(value: str) -> str:
    """
    Simplifies a given value in order to use it as node name

    Args:
        value: The value to be simplified

    Returns:
        str: The simplified value
    """
    simplified_value = str(value).lower()

    # normalize characters (p.ex. ä becomes a)
    simplified_value = unicodedata.normalize('NFKD', simplified_value)

    # replace forward slash and whitespace with a dash
    simplified_value = re.sub('[/\\s]+', '-', simplified_value)

    # delete all characters which are not letters, numbers or dashes
    simplified_value = re.sub('[^A-Za-z0-9\\-]+', '', simplified_value)

    return simplified_value


def check_language_code(lang_code: str) -> bool:
    """
    Checks if a given language code is valid. The code is valid if it is listed in language-codes-3b2_csv.csv. This
    file provides all ISO 639-1 and ISO 639-2 language codes.

    Args:
        lang_code: the language code to be checked

    Returns:
        True if valid, False if not
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, 'language-codes-3b2_csv.csv'), 'r') as language_codes_file:
        language_codes = csv.reader(language_codes_file, delimiter=',')
        for row in language_codes:
            if lang_code in row:
                return True
    return False


def make_root_node_from_args(
    excelfiles: list[str],
    listname_from_args: Optional[str],
    comments: dict[str, str]
) -> dict[str, Any]:
    """
    Creates the root node for the JSON list

    Args:
        excelfiles: List of Excel files (names) to be checked
        listname_from_args: Listname from arguments provided by the user via the command line
        comments: Comments provided by the ontology

    Returns:
        dict: The root node of the list as dictionary (JSON)
    """
    listname_from_lang_code = {}
    listname_en: str = ''
    lang_specific_listname: str = ''

    for filename in excelfiles:
        basename = os.path.basename(filename)
        lang_specific_listname, lang_code = os.path.splitext(basename)[0].rsplit('_', 1)

        if not check_language_code(lang_code):
            print(f'Invalid language code "{lang_code}" is used. Only language codes from ISO 639-1 ',
                  f'and ISO 639-2 are accepted.')
            quit()

        listname_from_lang_code[lang_code] = lang_specific_listname

        if '_en.xlsx' in filename:
            listname_en = lang_specific_listname

    # the listname is taken from the following sources, with descending priority
    if listname_from_args:
        listname = listname_from_args
    elif listname_en:
        listname = listname_en
    else:
        listname = lang_specific_listname

    rootnode = {'name': listname, 'labels': listname_from_lang_code, 'comments': comments}

    return rootnode


def validate_list_with_schema(json_list: str) -> bool:
    """
    This function checks if a list is valid according to the schema.

    Args:
        json_list (json): the json list to be validated

    Returns:
        True if the list passed validation, False otherwise
    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, '../schemas/lists-only.json')) as schema:
        list_schema = json.load(schema)

    try:
        jsonschema.validate(instance=json_list, schema=list_schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return False
    print('List passed schema validation.')
    return True


def prepare_list_creation(
    excelfolder: str,
    listname: Optional[str],
    comments: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    """
    Creates the list from Excel files that can be used to build a JSON list. Then, creates the root node for the JSON list.

    Args:
        excelfolder: path to the folder containing the Excel file(s)
        listname: name of the list to be created
        comments: comments for the list to be created

    Returns:
        rootnode: The rootnode of the list as a dictionary
        excel_files: list of the Excel files to process
    """
    # reset the global variables before list creation starts
    global list_of_previous_node_names
    global list_of_lists_of_previous_cell_values

    list_of_previous_node_names = []
    list_of_lists_of_previous_cell_values = []

    # check if the given folder parameter is actually a folder
    if not os.path.isdir(excelfolder):
        print(excelfolder, ' is not a directory.')
        exit(1)

    # create a list with all excel files from the path provided by the user
    excel_files = [filename for filename in glob.iglob(f'{excelfolder}/*.xlsx')
                   if not os.path.basename(filename).startswith('~$')
                   and os.path.isfile(filename)]

    # print the files that can be used
    print('Found the following files:')
    for file in excel_files:
        print(file)

    # create root node of list
    rootnode = make_root_node_from_args(excel_files, listname, comments)

    return rootnode, excel_files


def list_excel2json(listname: Union[str, None], excelfolder: str, outfile: str) -> None:
    """
    Takes the arguments from the command line, checks folder and files and starts the process of list creation.

    Args:
        listname: name of the list to be created, file name is taken if omitted
        excelfolder: path to the folder containing the Excel file(s)
        outfile: path to the JSON file the output is written into

    Return:
        None
    """
    # get the Excel files from the folder and create the rootnode of the list
    rootnode, excel_files = prepare_list_creation(excelfolder, listname, comments={})

    # create the list from the Excel files
    finished_list = make_json_list_from_excel(rootnode, excel_files)

    # validate created list with schema
    if validate_list_with_schema(json.loads(json.dumps(finished_list, indent=4))):
        with open(outfile, 'w', encoding='utf-8') as fp:
            json.dump(finished_list, fp, indent=4, sort_keys=False, ensure_ascii=False)
            print('List was created successfully and written to file:', outfile)
    else:
        print('List is not valid according to schema.')
