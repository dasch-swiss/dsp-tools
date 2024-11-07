import json
import uuid
from typing import Any
from typing import Iterable

import regex

from dsp_tools.models.exceptions import InputError
from dsp_tools.xmllib.value_checkers import is_nonempty_value


def create_label_to_name_list_node_mapping(
    project_json_path: str,
    list_name: str,
    language_of_label: str,
) -> dict[str, str]:
    """
    Often, data sources contain list values named after the "label" of the JSON project list node, instead of the "name"
    which is needed for the `dsp-tools xmlupload`.
    To create a correct XML, you need a dictionary that maps the "labels" to their correct "names".

    Args:
        project_json_path: path to a JSON project file (a.k.a. ontology)
        list_name: name of a list in the JSON project
        language_of_label: which language of the label to choose

    Returns:
        a dictionary of the form {label: name}
    """
    with open(project_json_path, encoding="utf-8") as f:
        json_file = json.load(f)
    json_subset = [x for x in json_file["project"]["lists"] if x["name"] == list_name]
    # json_subset is a list containing one item, namely the json object containing the entire json-list
    res = {}
    for label, name in _name_label_mapper_iterator(json_subset, language_of_label):
        if name != list_name:
            res[label] = name
            res[label.strip().lower()] = name
    return res


def _name_label_mapper_iterator(
    json_subset: list[dict[str, Any]],
    language_of_label: str,
) -> Iterable[tuple[str, str]]:
    """
    Go through list nodes of a JSON project and yield (label, name) pairs.

    Args:
        json_subset: list of DSP lists (a DSP list being a dictionary with the keys "name", "labels" and "nodes")
        language_of_label: which language of the label to choose

    Yields:
        (label, name) pairs
    """
    for node in json_subset:
        # node is the json object containing the entire json-list
        if "nodes" in node:
            # "nodes" is the json sub-object containing the entries of the json-list
            yield from _name_label_mapper_iterator(node["nodes"], language_of_label)
            # each yielded value is a (label, name) pair of a single list entry
        if "name" in node:
            yield node["labels"][language_of_label], node["name"]
            # the actual values of the name and the label


def make_xsd_compatible_id_with_uuid(string: str) -> str:
    """
    An xsd:ID may not contain all types of special characters.
    This function replaces illegal characters with "_".
    The UUID will be different each time the function is called.

    The string must contain at least one Unicode letter (matching the regex ``\\p{L}``),
    _, !, ?, or number, but must not be `None`, `<NA>`, `N/A`, or `-`.

    Args:
        string: input string

    Raises:
        InputError: if the input cannot be transformed to an xsd:ID

    Returns:
        an xsd ID based on the input string, with a UUID attached.
    """
    res = make_xsd_compatible_id(string)
    _uuid = uuid.uuid4()
    res = f"{res}_{_uuid}"
    return res


def make_xsd_compatible_id(string: str) -> str:
    """
    An xsd:ID may not contain all types of special characters.
    This function replaces illegal characters with "_".

    The string must contain at least one Unicode letter (matching the regex ``\\p{L}``),
    _, !, ?, or number, but must not be `None`, `<NA>`, `N/A`, or `-`.

    Args:
        string: input string

    Raises:
        InputError: if the input cannot be transformed to an xsd:ID

    Returns:
        An xsd ID compatible string based on the input string
    """
    if not isinstance(string, str) or not is_nonempty_value(string):
        raise InputError(f"The input '{string}' cannot be transformed to an xsd:ID")
    # if the start of string is neither letter nor underscore, add an underscore
    res = regex.sub(r"^(?=[^A-Za-z_])", "_", string)
    # replace all illegal characters by underscore
    res = regex.sub(r"[^\w_\-.]", "_", res, flags=regex.ASCII)
    return res
