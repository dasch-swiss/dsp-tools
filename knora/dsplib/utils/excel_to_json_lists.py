"""This file handles all the operations which are used for the creation of JSON lists form Excel files."""
import csv
import glob
import json
import os
import re
import unicodedata
from typing import List

import jsonschema
import openpyxl
from jsonschema import validate
from openpyxl import load_workbook

list_of_lists = []
cell_names = []


def get_values_from_excel(excelfiles: List[str], worksheet: openpyxl.worksheet._read_only.ReadOnlyWorksheet, parentnode: {},
                          row: int, col: int, preval: List[str]) -> int:
    """
    This function calls itself recursively to go through the Excel file. It extracts the cell values and creates the
    JSON list.

    Args:
        excelfiles: List of Excel files with the different languages
        worksheet: Worksheet of the Excel file
        parentnode: Name(s) of the parent node(s) of the actual node
        row: The index of the actual row of the Excel sheet
        col: The index of the actual column of the Excel sheet
        preval: List of previous values, needed to check the consistency of the list hierarchy

    Returns:
        int: Row index for the next loop (actual row index minus 1)

    """
    nodes = []
    currentnode = {}
    cell = worksheet.cell(column=col, row=row)

    if col > 1:
        # append the cell value of the parent node (which is one value to the left of the actual cell) to the list
        # of previous values
        preval.append(worksheet.cell(column=col - 1, row=row).value)

    while cell.value:
        # check if all predecessors in row (values to the left) are consistent with the values in preval list
        for idx, val in enumerate(preval[:-1]):
            if val != worksheet.cell(column=idx + 1, row=row).value:
                print(f"Inconsistency in Excel list! {val} not equal to {worksheet.cell(column=idx + 1, row=row).value}")
                quit()

        # loop through the row until the last value is found
        if worksheet.cell(column=col + 1, row=row).value:
            row = get_values_from_excel(excelfiles=excelfiles, worksheet=worksheet, parentnode=currentnode, col=col + 1, row=row,
                                        preval=preval)

        # if value was last in row (no further values to the right), it's a node, continue here
        else:
            # check if there are duplicate nodes (identical rows), quit the program if so
            new_check_list = preval.copy()
            new_check_list.append(cell.value)

            list_of_lists.append(new_check_list)

            if check_list_for_duplicates(list_of_lists):
                print("There is at least one duplicate node in the list. Found duplicate: ", cell.value)
                quit()

            # create a simplified version of the cell value and use it as name of the node
            cellname = simplify_name(cell.value)
            cell_names.append(cellname)

            if check_list_for_duplicates(cell_names):
                n = cell_names.count(cellname)
                if n > 1:
                    cellname = cellname + "-" + str(n)

            labels_dict = {}

            # read label values from the other Excel files (other languages)
            for filename_other_lang in excelfiles:
                wb_other_lang = load_workbook(filename=filename_other_lang, read_only=True)
                ws_other_lang = wb_other_lang.worksheets[0]

                lang = os.path.splitext(filename_other_lang)[0].split('_')[-1]
                labels_dict[lang] = ws_other_lang.cell(column=col, row=row).value

            # create current node from extracted cell values and append it to the nodes list
            currentnode = {"name": cellname, "labels": labels_dict}

            nodes.append(currentnode)

            print(f"Added list node: {cell.value}")

        # go one row down and repeat loop if there is a value
        row += 1
        cell = worksheet.cell(column=col, row=row)

    if col > 1:
        preval.pop()

    # add the new nodes to the parentnode
    parentnode["nodes"] = nodes

    return row - 1


def make_json_list_from_excel(rootnode: {}, excelfiles: List[str]) -> None:
    """
    Reads an Excel file and makes a JSON list file from it. The JSON can then be used in an ontology that is uploaded to the
    DaSCH Service Platform.

    Args:
        rootnode: The root node of the JSON list
        excelfiles: A list with all the Excel files to be processed

    Returns:
        None

    """
    # Define starting point in Excel file
    startrow = 1
    startcol = 1

    # Check if english file is available, take last one from list of Excel files. The node names are derived from the labels of
    # the base file.
    base_file = ""

    for filename in excelfiles:
        base_file = filename
        if "_en.xlsx" in os.path.basename(filename):
            base_file = filename
            break

    wb = load_workbook(filename=base_file, read_only=True)
    worksheet = wb.worksheets[0]

    get_values_from_excel(excelfiles=excelfiles, worksheet=worksheet, parentnode=rootnode, row=startrow, col=startcol, preval=[])


def check_list_for_duplicates(list_to_check: list) -> bool:
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


def make_root_node_from_args(excelfiles: List[str], listname_from_args: str) -> dict:
    """
    Creates the root node for the JSON list

    Args:
        excelfiles: List of Excel files (names) to be checked
        listname_from_args: Listname from arguments provided by the user via the command line

    Returns:
        dict: The root node of the list as dictionary (JSON)

    """
    rootnode_labels_dict = {}
    listname = listname_from_args
    listname_en = ""

    for filename in excelfiles:
        basename = os.path.basename(filename)
        label, lang_code = os.path.splitext(basename)[0].rsplit('_', 1)

        # check if language code is valid
        if not check_language_code(lang_code):
            print("Invalid language code is used. Only language codes from ISO 639-1 and ISO 639-2 are accepted.")
            quit()

        rootnode_labels_dict[lang_code] = label
        listname = label

        if "_en.xlsx" in filename:
            listname_en = label

    # if an english list is available use its label as listname
    if listname_en:
        listname = listname_en

    # if the user provided a listname use it
    if listname_from_args:
        listname = listname_from_args

    rootnode = {"name": listname, "labels": rootnode_labels_dict}

    return rootnode


def validate_list_with_schema(json_list: str) -> bool:
    """
    This function checks if a list is valid according to the schema.

    Args:
        json_list (json): the json list to be validated

    Returns:
        True if the list is valid, False otherwise

    """
    current_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(current_dir, 'knora-schema-lists-only.json')) as schema:
        list_schema = json.load(schema)

    try:
        validate(instance=json_list, schema=list_schema)
    except jsonschema.exceptions.ValidationError as err:
        print(err)
        return False
    print("List passed schema validation.")
    return True


def list_excel2json(listname: str, excelfolder: str, outfile: str):
    """
    Takes the arguments from the command line and starts the process of list creation.

    Args:
        listname: name of the list to be created, file name is taken if omitted
        excelfolder: path to the folder containing the Excel file(s)
        outfile: path to the JSON file which the output is written to
    """
    # crate a list with all excel files from the path provided by the user
    excel_files = [filename for filename in glob.iglob(f'{excelfolder}/*.xlsx') if
                   not os.path.basename(filename).startswith("~$")]

    # create root node of list
    rootnode = make_root_node_from_args(excel_files, listname)

    # create rest of the list from Excel worksheet
    make_json_list_from_excel(rootnode, excel_files)

    # validate list with schema
    if validate_list_with_schema(json.loads(json.dumps(rootnode, indent=4))):
        # write final list to JSON file
        with open(outfile, 'w', encoding="utf-8") as fp:
            json.dump(rootnode, fp, indent=4, sort_keys=False, ensure_ascii=False)
    else:
        print("List is not valid according to schema.")
