import json

from openpyxl import load_workbook


def resources_excel2json(excelfile: str, outfile: str):
    """
    Takes the arguments from the command line, checks file and starts the process of the output creation.

    Args:
        excelfile: path to the Excel file containing the resource data
        outfile: path to the JSON output file

    Returns:
        None
    """
    # load file
    wb = load_workbook(excelfile, read_only=True)

    # get overview
    sheet = wb['classes']
    resource_list = [c for c in sheet.iter_rows(min_row=2, values_only=True)]

    resources = []
    # for each resource in resources overview
    for res in resource_list:
        # get name
        name = res[0]
        # get labels
        labels = {}
        if res[1]:
            labels['en'] = res[1]
        if res[2]:
            labels['de'] = res[2]
        if res[3]:
            labels['fr'] = res[3]
        if res[4]:
            labels['it'] = res[4]
        # get super
        sup = res[5]

        # load details for this resource
        sh = wb[name]
        property_list = [c for c in sh.iter_rows(min_row=2, values_only=True)]

        cards = []
        # for each of the detail sheets
        for i, prop in enumerate(property_list):
            # get name and cardinality.
            # GUI-order is equal to order in the sheet.
            property_ = {
                "propname": ":" + prop[0],
                "cardinality": str(prop[1]),
                "gui_order": i + 1
            }
            cards.append(property_)

        # build resource dict
        resource = {
            "name": name,
            "labels": labels,
            "super": sup,
            "cardinalities": cards
        }
        # append to resources list
        resources.append(resource)

    with open(file=outfile, mode='w+', encoding='utf-8') as file:
        json.dump(resources, file, indent=4)
