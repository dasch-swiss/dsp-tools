from dsp_tools.commands.excel2json.models.json_header import EmptyJsonHeader
from dsp_tools.commands.excel2json.models.json_header import JsonHeader


def get_json_header() -> JsonHeader:
    """
    Returns the header of the JSON file.
    If an Excel file with the information is provided it is filled out.
    Otherwise it will return a header with the fields left blank.

    Returns:
        JsonHeader object
    """
    return EmptyJsonHeader()
