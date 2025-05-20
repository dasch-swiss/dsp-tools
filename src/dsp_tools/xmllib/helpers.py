from __future__ import annotations

import datetime
import json
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import regex
from lxml import etree
from regex import Match

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.error.xmllib_warnings_util import raise_input_error
from dsp_tools.xmllib.internal.checkers import is_nonempty_value_internal
from dsp_tools.xmllib.internal.constants import KNOWN_XML_TAG_REGEXES
from dsp_tools.xmllib.internal.input_converters import unescape_reserved_xml_chars
from dsp_tools.xmllib.models.config_options import NewlineReplacement
from dsp_tools.xmllib.models.licenses.other import LicenseOther
from dsp_tools.xmllib.models.licenses.recommended import License
from dsp_tools.xmllib.models.licenses.recommended import LicenseRecommended
from dsp_tools.xmllib.value_converters import replace_newlines_with_tags


def create_footnote_string(
    footnote_text: str, newline_replacement_option: NewlineReplacement = NewlineReplacement.LINEBREAK
) -> str:
    """
    Takes the text for a footnote, and returns a string with the correct formatting.
    You can use this if you want to add the footnote to a string.
    Currently, the newline replacement options are restricted to `LINEBREAK` and `NONE`.
    The reserved characters `<`, `>` and `&` will be escaped temporarily,
    but they will be correctly displayed in DSP-APP.

    Attention:
        - The text in the footnote may be richtext, i.e. contain XML tags.
        - Not all tags supported in ordinary richtext are currently implemented.
        - The allowed tags are:
            - `<br>` (break line)
            - `<strong>` (bold)
            - `<em>` (italic)
            - `<u>` (underline)
            - `<strike>` (strike through)
            - `<a href="URI">` (link to a URI)
            - `<a class="salsah-link" href="Knora IRI">` (link to a resource)

    Args:
        footnote_text: Text for the footnote
        newline_replacement_option: options to replace newlines

    Raises:
        InputError: If the text is empty, or if a newline replacement which is not implemented is entered

    Returns:
        The footnote as a string

    Examples:
        ```python
        result = xmllib.create_footnote_string("Text")
        # result == '<footnote content="Text"/>'
        ```

        ```python
        result = xmllib.create_footnote_string("Text\\nSecond Line")
        # result == '<footnote content="Text&lt;br/&gt;Second Line"/>'
        ```

        ```python
        result = xmllib.create_footnote_string("Already escaped &lt;&gt;")
        # already escaped characters will not be escaped again
        # result == '<footnote content="Already escaped &lt;&gt;"/>'
        ```
    """
    text_tag = create_footnote_element(footnote_text, newline_replacement_option)
    return etree.tostring(text_tag, encoding="unicode")


def create_footnote_element(
    footnote_text: str, newline_replacement_option: NewlineReplacement = NewlineReplacement.LINEBREAK
) -> etree._Element:
    """
    Takes the text for a footnote, and returns an `etree.Element`.
    You can use this if you are working with `lxml`.
    Currently, the newline replacement options are restricted to `LINEBREAK` and `NONE`.

    Attention:
        - The text in the footnote may be richtext, i.e. contain XML tags.
        - Not all tags supported in ordinary richtext are currently implemented.
        - The allowed tags are:
            - `<br>` (break line)
            - `<strong>` (bold)
            - `<em>` (italic)
            - `<u>` (underline)
            - `<strike>` (strike through)
            - `<a href="URI">` (link to a URI)
            - `<a class="salsah-link" href="Knora IRI">` (link to a resource)

    Args:
        footnote_text: Text for the footnote
        newline_replacement_option: options to replace newlines

    Raises:
        InputError: If the text is empty, or if a newline replacement which is not implemented is entered

    Returns:
        The footnote as a string
    """
    if newline_replacement_option not in {NewlineReplacement.LINEBREAK, NewlineReplacement.NONE}:
        raise_input_error(MessageInfo("Currently the only supported newline replacement is linebreak (<br/>) or None."))
    if not is_nonempty_value_internal(footnote_text):
        raise_input_error(MessageInfo("The input value is empty."))
    footnote_text = replace_newlines_with_tags(str(footnote_text), newline_replacement_option)
    unescaped_text = unescape_reserved_xml_chars(footnote_text)
    return etree.Element("footnote", attrib={"content": unescaped_text})


def create_standoff_link_to_resource(resource_id: str, displayed_text: str) -> str:
    """
    Creates a standoff link to a resource.

    Args:
        resource_id: ID of the resource that is linked
        displayed_text: text to display for the embedded link

    Returns:
        A standoff link in string form.

    Raises:
        InputError: if the resource ID or the displayed text are empty

    Examples:
        ```python
        result = xmllib.create_standoff_link_to_resource("resource_id", "Text")
        # result == '<a class="salsah-link" href="IRI:resource_id:IRI">Text</a>'
        ```
    """
    if not all([is_nonempty_value_internal(resource_id), is_nonempty_value_internal(displayed_text)]):
        msg_str = (
            f"The entered resource ID and displayed text may not be empty. "
            f"Your input: resource_id '{resource_id}' / displayed_text '{displayed_text}'"
        )
        raise_input_error(MessageInfo(msg_str))
    attribs = {"class": "salsah-link", "href": f"IRI:{resource_id}:IRI"}
    ele = etree.Element("a", attrib=attribs)
    ele.text = displayed_text
    return etree.tostring(ele, encoding="unicode")


def create_standoff_link_to_uri(uri: str, displayed_text: str) -> str:
    """
    Creates a standoff link to a URI.

    Args:
        uri: the target URI that should be linked to
        displayed_text: text to display for the embedded link

    Returns:
        A standoff link in string form.

    Raises:
        InputError: if the URI or the displayed text are empty

    Examples:
        ```python
        result = xmllib.create_standoff_link_to_uri("https://www.dasch.swiss/", "This is DaSCH")
        # result == '<a href="https://www.dasch.swiss/">This is DaSCH</a>'
        ```
    """
    if not all([is_nonempty_value_internal(uri), is_nonempty_value_internal(displayed_text)]):
        msg_str = (
            f"The entered URI and displayed text may not be empty. "
            f"Your input: uri '{uri}' / displayed_text '{displayed_text}'"
        )
        raise_input_error(MessageInfo(msg_str))
    attribs = {"href": uri}
    ele = etree.Element("a", attrib=attribs)
    ele.text = displayed_text
    return etree.tostring(ele, encoding="unicode")


def _get_label_to_node_one_list(
    list_section: list[dict[str, Any]], list_name: str, language_of_label: str
) -> dict[str, str]:
    json_subset = [x for x in list_section if x["name"] == list_name]
    # json_subset is a list containing one item, namely the json object containing the entire json-list
    res = {}
    for label, name in _name_label_mapper_iterator(json_subset, language_of_label):
        if name != list_name:
            res[label] = name
            res[label.strip().lower()] = name
    return res


def _get_label_to_node_all_lists(
    list_section: list[dict[str, Any]], language_of_label: str
) -> dict[str, dict[str, str]]:
    mapper = {}
    for li in list_section:
        mapper[li["name"]] = _get_label_to_node_one_list(list_section, li["name"], language_of_label)
    return mapper


def _get_property_to_list_name_mapping(ontologies: list[dict[str, Any]], default_ontology: str) -> dict[str, str]:
    prop_lookup = {}
    for onto in ontologies:
        prefix = onto["name"]
        property_section = onto["properties"]
        for prop in property_section:
            if prop["gui_element"] == "List":
                prefixed_prop = f"{prefix}:{prop['name']}"
                prop_lookup[prefixed_prop] = prop["gui_attributes"]["hlist"]
    default_props = {
        k.replace(default_ontology, "", 1): v for k, v in prop_lookup.items() if k.startswith(f"{default_ontology}:")
    }
    prop_lookup = prop_lookup | default_props
    return prop_lookup


@dataclass
class ListLookup:
    _lookup: dict[str, dict[str, str]]
    _prop_to_list_name: dict[str, str]
    _label_language: str

    @staticmethod
    def create_new(project_json_path: str | Path, language_of_label: str, default_ontology: str) -> ListLookup:
        """
        Creates a list lookup based on list labels in a specified language and returning list node names.
        Works for all lists in a project.json

        Args:
            project_json_path: path to a JSON project file (a.k.a. ontology)
            language_of_label: label language used for the list
            default_ontology: ontology prefix which is defined as default in the XML file

        Returns:
            `ListLookup` for a project

        Examples:
            ```python
            list_lookup = xmllib.ListLookup.create_new(
                project_json_path="project.json",
                language_of_label="en",
                default_ontology="default-onto",
            )
            ```
        """
        with open(project_json_path, encoding="utf-8") as f:
            json_file = json.load(f)
        label_to_list_node_lookup = _get_label_to_node_all_lists(json_file["project"]["lists"], language_of_label)
        prop_to_list_mapper = _get_property_to_list_name_mapping(json_file["project"]["ontologies"], default_ontology)
        return ListLookup(
            _lookup=label_to_list_node_lookup,
            _prop_to_list_name=prop_to_list_mapper,
            _label_language=language_of_label,
        )

    def get_node_via_list_name(self, list_name: str, node_label: str) -> str:
        """
        Returns the list node name based on a label.
        The language of the label was specified when creating the `ListLookup`.

        Args:
            list_name: name of the list
            node_label: label of the node

        Returns:
            node name

        Examples:
            ```python
            node_name = list_lookup.get_node_via_list_name(
                list_name="list1",
                node_label="Label 1"  # or: "label 1" (capitalisation is not relevant)
            )
            # node_name == "node1"
            ```
        """
        if not (list_lookup := self._lookup.get(list_name)):
            emit_xmllib_input_warning(
                MessageInfo(f"The entered list name '{list_name}' was not found. An empty string is returned.")
            )
            return ""
        if not (found_node := list_lookup.get(node_label)):
            emit_xmllib_input_warning(
                MessageInfo(
                    f"'{node_label}' was not recognised as label of the list '{list_name}'. "
                    f"This ListLookup is configured for '{self._label_language}' labels. An empty string is returned."
                )
            )
            return ""
        return found_node

    def get_list_name_and_node_via_property(self, prop_name: str, node_label: str) -> tuple[str, str]:
        """
        Returns the list name and the node name based on a property that is used with the list and the label of a node.
        The language of the label was specified when creating the `ListLookup`.
        The list name needs to be referenced in the XML file.

        Args:
            prop_name: name of the list
            node_label: label of the node

        Returns:
            list name and node name

        Examples:
            ```python
            list_name, node_name = list_lookup.get_list_name_and_node_via_property(
                prop_name=":hasList",  # or: "default-onto:hasList"
                node_label="label 1"
            )
            # list_name == "list1"
            # node_name == "node1"
            ```
        """
        if not (list_name := self.get_list_name_via_property(prop_name)):
            return "", ""
        return list_name, self.get_node_via_list_name(list_name, node_label)

    def get_list_name_via_property(self, prop_name: str) -> str:
        """
        Returns the list name as specified in the ontology for a property.
        The list name needs to be referenced in the XML file.

        Args:
            prop_name: name of the property

        Returns:
            Name of the list

        Examples:
            ```python
            list_name = list_lookup.get_list_name_via_property(
                prop_name=":hasList",  # or: "default-onto:hasList"
            )
            # list_name == "list1"
            ```
        """
        if not (list_name := self._prop_to_list_name.get(prop_name)):
            emit_xmllib_input_warning(
                MessageInfo(f"The entered property '{prop_name}' was not found. An empty string is returned.")
            )
            return ""
        return list_name


def get_list_nodes_from_string_via_list_name(
    string_with_list_labels: str, label_separator: str, list_name: str, list_lookup: ListLookup
) -> list[str]:
    """
    Takes a string containing list labels, the separator by which they can be split,
    a property name and the list lookup.
    Resolves the labels and returns the list name to be referenced in the XML file and a list of node names.
    If the string is empty, it returns an empty list.

    Args:
        string_with_list_labels: the string containing the labels
        label_separator: separator in the string that contains the labels
        list_name: name of the list
        list_lookup: `ListLookup` of the project

    Returns:
        The name of the list and a list of node names.

    Examples:
        ```python
        string_with_list_labels = "Label 1; Label 2"
        nodes = xmllib.get_list_nodes_from_string_via_list_name(
            string_with_list_labels=string_with_list_labels,
            label_separator=";",
            list_name="list1",
            list_lookup=list_lookup,
        )
        # nodes == ["node1", "node2"]
        ```

        ```python
        string_with_list_labels = ""
        nodes = xmllib.get_list_nodes_from_string_via_list_name(
            string_with_list_labels=string_with_list_labels,
            label_separator=";",
            list_name="list1",
            list_lookup=list_lookup,
        )
        # nodes == []
        ```

        ```python
        string_with_list_labels = pd.NA
        nodes = xmllib.get_list_nodes_from_string_via_list_name(
            string_with_list_labels=string_with_list_labels,
            label_separator=";",
            list_name="list1",
            list_lookup=list_lookup,
        )
        # nodes == []
        ```
    """
    if not is_nonempty_value_internal(string_with_list_labels):
        return []
    labels_list = create_list_from_string(string_with_list_labels, label_separator)
    nodes_list = [list_lookup.get_node_via_list_name(list_name, label) for label in labels_list]
    return nodes_list


def get_list_nodes_from_string_via_property(
    string_with_list_labels: str, label_separator: str, property_name: str, list_lookup: ListLookup
) -> tuple[str, list[str]]:
    """
    Takes a string containing list labels, the separator by which they can be split,
    a property name and the list lookup.
    Resolves the labels and returns the list name to be referenced in the XML file and a list of node names.
    If the string is empty, it returns an empty list.

    Args:
        string_with_list_labels: the string containing the labels
        label_separator: separator in the string that contains the labels
        property_name: name of the property
        list_lookup: `ListLookup` of the project

    Returns:
        The name of the list and a list of node names.

    Examples:
        ```python
        string_with_list_labels = "Label 1; Label 2"
        list_name, nodes = xmllib.get_list_nodes_from_string_via_property(
            string_with_list_labels=string_with_list_labels,
            label_separator=";",
            property_name=":hasList",
            list_lookup=list_lookup,
        )
        # list_name == "list1"
        # nodes == ["node1", "node2"]
        ```

        ```python
        string_with_list_labels = ""
        list_name, nodes = xmllib.get_list_nodes_from_string_via_property(
            string_with_list_labels=string_with_list_labels,
            label_separator=";",
            property_name=":hasList",
            list_lookup=list_lookup,
        )
        # list_name == ""
        # nodes == []
        ```

        ```python
        string_with_list_labels = pd.NA
        list_name, nodes = xmllib.get_list_nodes_from_string_via_property(
            string_with_list_labels=string_with_list_labels,
            label_separator=";",
            property_name=":hasList",
            list_lookup=list_lookup,
        )
        # list_name == ""
        # nodes == []
        ```
    """
    if not is_nonempty_value_internal(string_with_list_labels):
        return "", []
    labels_list = create_list_from_string(string_with_list_labels, label_separator)
    list_name = ""
    nodes = []
    for lbl in labels_list:
        list_name, node_name = list_lookup.get_list_name_and_node_via_property(property_name, lbl)
        nodes.append(node_name)
    return list_name, nodes


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


def escape_reserved_xml_characters(text: str) -> str:
    """
    From richtext strings (encoding="xml"), escape the reserved characters `<`, `>` and `&`,
    but only if they are not part of a standard standoff tag or escape sequence.

    [See the documentation for the standard standoff tags allowed by DSP-API,
    which will not be escaped.](https://docs.dasch.swiss/latest/DSP-API/03-endpoints/api-v2/text/standard-standoff/)

    Args:
        text: the richtext string to be escaped

    Returns:
        The escaped richtext string

    Examples:
        ```python
        result = xmllib.escape_reserved_xml_characters("Text <unknownTag>")
        # result == "Text &lt;unknownTag&gt;"
        ```

        ```python
        result = xmllib.escape_reserved_xml_characters("Text <br/> text after")
        # result == "Text <br/> text after"
        ```
    """
    allowed_tags_regex = "|".join(KNOWN_XML_TAG_REGEXES)
    lookahead = rf"(?!/?({allowed_tags_regex})/?>)"
    illegal_lt = rf"<{lookahead}"
    lookbehind = rf"(?<!</?({allowed_tags_regex})/?)"
    illegal_gt = rf"{lookbehind}>"
    illegal_amp = r"&(?![#a-zA-Z0-9]+;)"
    text = regex.sub(illegal_lt, "&lt;", text)
    text = regex.sub(illegal_gt, "&gt;", text)
    text = regex.sub(illegal_amp, "&amp;", text)
    return text


def find_dates_in_string(string: str) -> set[str]:
    """
    Checks if a string contains date values (single dates, or date ranges),
    and return all found dates as set of DSP-formatted strings.
    Returns an empty set if no date was found.
    [See XML documentation for details](https://docs.dasch.swiss/latest/DSP-TOOLS/file-formats/xml-data-file/#date).

    Notes:
        - If no era or calendar is given, dates are interpreted in the Common Era and the Gregorian calendar.
        - Standalone numbers from 000-2999, in 3/4-digit form, are interpreted as years CE.
        - If a number (with any number of digits) is followed by CE, C.E., AD, A.D., it is interpreted as years CE.
        - If a number (with any number of digits) is followed by BCE, BC, B.C., B.C.E., av. J.-C.,
          it is interpreted as years BCE.
        - Dates written with slashes are always interpreted in a European manner: 5/11/2021 is the 5th of November.
        - In the European notation, 2-digit years are expanded to 4 digits, with the current year as watershed:
            - 30.4.24 -> 30.04.2024
            - 30.4.50 -> 30.04.1950

    Currently supported date formats:
        - 0476-09-04 -> GREGORIAN:CE:0476-09-04:CE:0476-09-04
        - 0476_09_04 -> GREGORIAN:CE:0476-09-04:CE:0476-09-04
        - 30.4.2021 -> GREGORIAN:CE:2021-04-30:CE:2021-04-30
        - 30.4.21 -> GREGORIAN:CE:2021-04-30:CE:2021-04-30
        - 5/11/2021 -> GREGORIAN:CE:2021-11-05:CE:2021-11-05
        - Jan 26, 1993 -> GREGORIAN:CE:1993-01-26:CE:1993-01-26
        - 26 Jan 1993 -> GREGORIAN:CE:1993-01-26:CE:1993-01-26
        - 26 January 1993 -> GREGORIAN:CE:1993-01-26:CE:1993-01-26
        - 26. Jan. 1993 -> GREGORIAN:CE:1993-01-26:CE:1993-01-26
        - 26. Januar 1993 -> GREGORIAN:CE:1993-01-26:CE:1993-01-26
        - 28.2.-1.12.1515 -> GREGORIAN:CE:1515-02-28:CE:1515-12-01
        - 25.-26.2.0800 -> GREGORIAN:CE:0800-02-25:CE:0800-02-26
        - 1.9.2022-3.1.2024 -> GREGORIAN:CE:2022-09-01:CE:2024-01-03
        - 1848 -> GREGORIAN:CE:1848:CE:1848
        - 1849/1850 -> GREGORIAN:CE:1849:CE:1850
        - 1849/50 -> GREGORIAN:CE:1849:CE:1850
        - 1845-50 -> GREGORIAN:CE:1845:CE:1850
        - 840-50 -> GREGORIAN:CE:840:CE:850
        - 840-1 -> GREGORIAN:CE:840:CE:841
        - 9 BC / 9 B.C. / 9 B.C.E. / 9 BCE -> GREGORIAN:BC:9:BC:9
        - 20 BCE - 50 CE -> GREGORIAN:BC:20:CE:50
        - 1000-900 av. J.-C. -> GREGORIAN:BC:1000:BC:900
        - 45 av. J.-C. -> GREGORIAN:BC:45:BC:45

    Args:
        string: string to check

    Returns:
        (possibly empty) set of DSP-formatted date strings

    Examples:
        ```python
        result = xmllib.find_dates_in_string("1849/1850")
        # result == {"GREGORIAN:CE:1849:CE:1850"}
        ```

        ```python
        result = xmllib.find_dates_in_string("not a valid date")
        # result == {}
        ```

        ```python
        result = xmllib.find_dates_in_string("first date: 2024. Second: 2025.")
        # result == {"GREGORIAN:CE:2024:CE:2024", "GREGORIAN:CE:2025:CE:2025"}
        ```
    """

    # sanitise input, just in case that the function was called on an empty or N/A cell
    if not is_nonempty_value_internal(string):
        return set()
    return _find_dates_in_string(string)


_months_dict = {
    "January": 1,
    "Januar": 1,
    "Jan": 1,
    "February": 2,
    "Februar": 2,
    "Feb": 2,
    "March": 3,
    "März": 3,
    "Mar": 3,
    "April": 4,
    "Apr": 4,
    "May": 5,
    "Mai": 5,
    "June": 6,
    "Juni": 6,
    "Jun": 6,
    "July": 7,
    "Juli": 7,
    "Jul": 7,
    "August": 8,
    "Aug": 8,
    "September": 9,
    "Sept": 9,
    "October": 10,
    "Oktober": 10,
    "Oct": 10,
    "Okt": 10,
    "November": 11,
    "Nov": 11,
    "December": 12,
    "Dezember": 12,
    "Dec": 12,
    "Dez": 12,
}
all_months = "|".join(_months_dict)


def _find_dates_in_string(string: str) -> set[str]:
    year_regex = r"([0-2]?[0-9][0-9][0-9])"
    year_regex_2_or_4_digits = r"((?:[0-2]?[0-9])?[0-9][0-9])"
    month_regex = r"([0-1]?[0-9])"
    day_regex = r"([0-3]?[0-9])"
    sep_regex = r"[\./]"
    lookbehind = r"(?<![0-9A-Za-z])"
    lookahead = r"(?![0-9A-Za-z])"
    range_operator_regex = r" ?- ?"

    remaining_string = string
    results: set[str | None] = set()

    remaining_string = _extract_already_parsed_date(remaining_string, results)

    remaining_string = _find_english_BC_or_CE_dates(
        string=remaining_string,
        lookbehind=lookbehind,
        lookahead=lookahead,
        range_operator_regex=range_operator_regex,
        results=results,
    )

    remaining_string = _find_french_bc_dates(
        string=remaining_string,
        lookbehind=lookbehind,
        lookahead=lookahead,
        range_operator_regex=range_operator_regex,
        results=results,
    )

    # template: 2021-01-01 | 2015_01_02
    iso_dates_regex = rf"{lookbehind}{year_regex}[_-]([0-1][0-9])[_-]([0-3][0-9]){lookahead}"
    if iso_dates := list(regex.finditer(iso_dates_regex, remaining_string)):
        results.update(_from_iso_date(x) for x in iso_dates)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in iso_dates])

    # template: 6.-8.3.1948 | 6/2/1947 - 24.03.1948
    eur_date_range_regex = (
        rf"{lookbehind}"
        rf"{day_regex}{sep_regex}(?:{month_regex}{sep_regex}{year_regex_2_or_4_digits}?)?{range_operator_regex}"
        rf"{day_regex}{sep_regex}{month_regex}{sep_regex}{year_regex_2_or_4_digits}"
        rf"{lookahead}"
    )
    if eur_date_ranges := list(regex.finditer(eur_date_range_regex, remaining_string)):
        results.update(_from_eur_date_range(x) for x in eur_date_ranges)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in eur_date_ranges])

    # template: 1.4.2021 | 5/11/2021
    eur_date_regex = rf"{lookbehind}{day_regex}{sep_regex}{month_regex}{sep_regex}{year_regex_2_or_4_digits}{lookahead}"
    if eur_dates := list(regex.finditer(eur_date_regex, remaining_string)):
        results.update(_from_eur_date(x) for x in eur_dates)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in eur_dates])

    # template: March 9, 1908 | March5,1908 | May 11, 1906
    monthname_date_regex = rf"{lookbehind}({all_months}) ?{day_regex}, ?{year_regex}{lookahead}"
    if monthname_dates := list(regex.finditer(monthname_date_regex, remaining_string)):
        results.update(_from_monthname_date(x) for x in monthname_dates)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in monthname_dates])

    # template: 9 March 1908
    monthname_after_day_regex = rf"{lookbehind}{day_regex} ?({all_months}) ?{year_regex}{lookahead}"
    if monthname_after_days := list(regex.finditer(monthname_after_day_regex, remaining_string)):
        results.update(_from_monthname_after_day(x) for x in monthname_after_days)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in monthname_after_days])

    # template: 26. Januar 1993 | 26. Jan. 1993 | 26. Jan 1993
    german_monthname_date_regex = rf"{lookbehind}{day_regex}\.? ?({all_months})\.? ?{year_regex}{lookahead}"
    if german_monthname_dates := list(regex.finditer(german_monthname_date_regex, remaining_string)):
        results.update(_from_german_monthname_date(x) for x in german_monthname_dates)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in german_monthname_dates])

    # template: 1849/50 | 1849-50 | 1849/1850
    if year_ranges := list(regex.finditer(lookbehind + year_regex + r"[/-](\d{1,4})" + lookahead, remaining_string)):
        results.update(_from_year_range(x) for x in year_ranges)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in year_ranges])

    # template: 1907
    if year_onlies := list(regex.finditer(rf"{lookbehind}{year_regex}{lookahead}", remaining_string)):
        results.update(f"GREGORIAN:CE:{int(x.group(0))}:CE:{int(x.group(0))}" for x in year_onlies)
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in year_onlies])

    return {x for x in results if x}


def _remove_used_spans(string: str, spans: list[tuple[int, int]]) -> str:
    """Once a regex has matched parts of the original string, remove these parts, so that they're not matched again."""
    for start, end in reversed(spans):
        string = string[:start] + string[end:]
    return string


def _find_english_BC_or_CE_dates(
    string: str,
    lookbehind: str,
    lookahead: str,
    range_operator_regex: str,
    results: set[str | None],
) -> str:
    eraless_date_regex = r"(\d+)"
    bc_era_regex = r"(?:BC|BCE|B\.C\.|B\.C\.E\.)"
    bc_date_regex = rf"(?:{eraless_date_regex} ?{bc_era_regex})"
    ce_era_regex = r"(?:CE|AD|C\.E\.|A\.D\.)"
    ce_date_regex = rf"(?:{eraless_date_regex} ?{ce_era_regex})"
    bc_or_ce_date_regex = rf"(?:{bc_date_regex}|{ce_date_regex})"

    remaining_string = string
    results_new: set[str | None] = set()

    range_regex = (
        rf"{lookbehind}(?:{bc_or_ce_date_regex}|{eraless_date_regex})"
        rf"{range_operator_regex}"
        rf"{bc_or_ce_date_regex}{lookahead}"
    )
    if matchs := list(regex.finditer(range_regex, remaining_string)):
        results_new.update(
            _from_english_BC_or_CE_range(
                string=x.group(0),
                range_operator_regex=range_operator_regex,
                bc_era_regex=bc_era_regex,
                ce_era_regex=ce_era_regex,
                eraless_date_regex=eraless_date_regex,
            )
            for x in matchs
        )
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in matchs])

    if matchs := list(regex.finditer(rf"{lookbehind}{bc_date_regex}{lookahead}", remaining_string)):
        results_new.update({f"GREGORIAN:BC:{x.group(1)}:BC:{x.group(1)}" for x in matchs})
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in matchs])

    if matchs := list(regex.finditer(rf"{lookbehind}{ce_date_regex}{lookahead}", remaining_string)):
        results_new.update({f"GREGORIAN:CE:{x.group(1)}:CE:{x.group(1)}" for x in matchs})
        remaining_string = _remove_used_spans(remaining_string, [x.span() for x in matchs])

    results.update({x for x in results_new if x})
    return remaining_string


def _from_english_BC_or_CE_range(
    string: str, range_operator_regex: str, bc_era_regex: str, ce_era_regex: str, eraless_date_regex: str
) -> str | None:
    split_result = regex.split(range_operator_regex, string)
    if len(split_result) != 2:
        return None
    start_raw, end_raw = split_result
    if regex.search(bc_era_regex, end_raw):
        end_era = "BC"
    elif regex.search(ce_era_regex, end_raw):
        end_era = "CE"
    else:
        return None

    if regex.search(bc_era_regex, start_raw):
        start_era = "BC"
    elif regex.search(ce_era_regex, start_raw):
        start_era = "CE"
    else:
        start_era = end_era

    if not (start_year_match := regex.search(eraless_date_regex, start_raw)):
        return None
    if not (end_year_match := regex.search(eraless_date_regex, end_raw)):
        return None

    return f"GREGORIAN:{start_era}:{start_year_match.group(0)}:{end_era}:{end_year_match.group(0)}"


def _find_french_bc_dates(
    string: str,
    lookbehind: str,
    lookahead: str,
    range_operator_regex: str,
    results: set[str | None],
) -> str:
    remaining_string = string
    results_new: set[str | None] = set()
    french_bc_regex = r"av(?:\. |\.| )J\.?-?C\.?"

    year_regex = r"\d{1,5}"
    year_range_regex = rf"{lookbehind}({year_regex}){range_operator_regex}({year_regex}) {french_bc_regex}{lookahead}"
    for year_range in reversed(list(regex.finditer(year_range_regex, remaining_string))):
        start_year = int(year_range.group(1))
        end_year = int(year_range.group(2))
        if end_year > start_year:
            continue
        results_new.add(f"GREGORIAN:BC:{start_year}:BC:{end_year}")
        remaining_string = _remove_used_spans(remaining_string, [year_range.span()])

    single_year_regex = rf"{lookbehind}({year_regex}) {french_bc_regex}{lookahead}"
    for single_year in reversed(list(regex.finditer(single_year_regex, remaining_string))):
        start_year = int(single_year.group(1))
        results_new.add(f"GREGORIAN:BC:{start_year}:BC:{start_year}")
        remaining_string = _remove_used_spans(remaining_string, [single_year.span()])

    results.update({x for x in results_new if x})
    return remaining_string


def _from_iso_date(iso_date: Match[str]) -> str | None:
    year = int(iso_date.group(1))
    month = int(iso_date.group(2))
    day = int(iso_date.group(3))
    try:
        date = datetime.date(year, month, day)
        return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"
    except ValueError:
        return None


def _expand_2_digit_year(year: int) -> int:
    current_year = datetime.date.today().year - 2000
    if year <= current_year:
        return year + 2000
    elif year <= 99:
        return year + 1900
    else:
        return year


def _from_eur_date_range(eur_date_range: Match[str]) -> str | None:
    startday = int(eur_date_range.group(1))
    startmonth = int(eur_date_range.group(2)) if eur_date_range.group(2) else int(eur_date_range.group(5))
    startyear = int(eur_date_range.group(3)) if eur_date_range.group(3) else int(eur_date_range.group(6))
    startyear = _expand_2_digit_year(startyear)
    endday = int(eur_date_range.group(4))
    endmonth = int(eur_date_range.group(5))
    endyear = int(eur_date_range.group(6))
    endyear = _expand_2_digit_year(endyear)
    try:
        startdate = datetime.date(startyear, startmonth, startday)
        enddate = datetime.date(endyear, endmonth, endday)
    except ValueError:
        return None
    if enddate < startdate:
        return None
    return f"GREGORIAN:CE:{startdate.isoformat()}:CE:{enddate.isoformat()}"


def _from_eur_date(eur_date: Match[str]) -> str | None:
    startday = int(eur_date.group(1))
    startmonth = int(eur_date.group(2))
    startyear = int(eur_date.group(3))
    startyear = _expand_2_digit_year(startyear)
    try:
        date = datetime.date(startyear, startmonth, startday)
        return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"
    except ValueError:
        return None


def _from_monthname_date(monthname_date: Match[str]) -> str | None:
    day = int(monthname_date.group(2))
    month = _months_dict[monthname_date.group(1)]
    year = int(monthname_date.group(3))
    try:
        date = datetime.date(year, month, day)
        return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"
    except ValueError:
        return None


def _from_monthname_after_day(monthname_after_day: Match[str]) -> str | None:
    day = int(monthname_after_day.group(1))
    month = _months_dict[monthname_after_day.group(2)]
    year = int(monthname_after_day.group(3))
    try:
        date = datetime.date(year, month, day)
        return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"
    except ValueError:
        return None


def _from_german_monthname_date(german_monthname_date: Match[str]) -> str | None:
    day = int(german_monthname_date.group(1))
    month = _months_dict[german_monthname_date.group(2)]
    year = int(german_monthname_date.group(3))
    try:
        date = datetime.date(year, month, day)
        return f"GREGORIAN:CE:{date.isoformat()}:CE:{date.isoformat()}"
    except ValueError:
        return None


def _from_year_range(year_range: Match[str]) -> str | None:
    startyear = int(year_range.group(1))
    endyear = int(year_range.group(2))
    if endyear // 10 == 0:
        # endyear is only 1-digit: add the first 2-3 digits of startyear
        endyear = startyear // 10 * 10 + endyear
    elif endyear // 100 == 0:
        # endyear is only 2-digit: add the first 1-2 digits of startyear
        endyear = startyear // 100 * 100 + endyear
    if endyear <= startyear:
        return None
    return f"GREGORIAN:CE:{startyear}:CE:{endyear}"


def _extract_already_parsed_date(string: str, results: set[str | None]) -> str:
    rgx_year = r"\d+(-\d{2}(-\d{2})?)?"
    era_with_colon = r"(CE:|BC:)"
    rgx = rf"(GREGORIAN|JULIAN|ISLAMIC):{era_with_colon}{rgx_year}:{era_with_colon}?{rgx_year}"
    if matchs := list(regex.finditer(rgx, string)):
        results.update({x.group(0) for x in matchs})
        remaining_string = _remove_used_spans(string, [x.span() for x in matchs])
        return remaining_string
    return string


def make_xsd_compatible_id(input_value: str | float | int) -> str:
    """
    An xsd:ID may not contain all types of special characters,
    and it must start with a letter or underscore.
    Replace illegal characters with `_`, and prepend a leading `_` if necessary.

    The string must contain at least one Unicode letter (matching the regex ``\\p{L}``),
    `_`, `!`, `?`, or number, but must not be `None`, `<NA>`, `N/A`, or `-`.

    Args:
        input_value: input value

    Raises:
        InputError: if the input cannot be transformed to an xsd:ID

    Returns:
        An xsd ID compatible string based on the input value

    Examples:
        ```python
        result = xmllib.make_xsd_compatible_id("0_Universität_Basel")
        # result == "_0_Universit_t_Basel"
        ```
    """
    if not is_nonempty_value_internal(input_value):
        raise_input_error(MessageInfo(f"The input '{input_value}' cannot be transformed to an xsd:ID"))
    # if the start of string is neither letter nor underscore, add an underscore
    res = regex.sub(r"^(?=[^A-Za-z_])", "_", str(input_value))
    # replace all illegal characters by underscore
    res = regex.sub(r"[^\w_\-.]", "_", res, flags=regex.ASCII)
    return res


def make_xsd_compatible_id_with_uuid(input_value: str | float | int) -> str:
    """
    An xsd:ID may not contain all types of special characters,
    and it must start with a letter or underscore.
    Replace illegal characters with `_`, and prepend a leading `_` if necessary.
    Additionally, add a UUID at the end.
    The UUID will be different each time the function is called.

    The string must contain at least one Unicode letter (matching the regex ``\\p{L}``),
    `_`, `!`, `?`, or number, but must not be `None`, `<NA>`, `N/A`, or `-`.

    Args:
        input_value: input value

    Raises:
        InputError: if the input cannot be transformed to an xsd:ID

    Returns:
        an xsd ID based on the input value, with a UUID attached.

    Examples:
        ```python
        result = xmllib.make_xsd_compatible_id_with_uuid("Universität_Basel")
        # result == "Universit_t_Basel_88f5cd0b-f333-4174-9030-65900b17773d"
        ```
    """
    res = make_xsd_compatible_id(input_value)
    _uuid = uuid.uuid4()
    res = f"{res}_{_uuid}"
    return res


def create_list_from_string(string: str, separator: str) -> list[str]:
    """
    Creates a list from a string.
    Trailing and leading whitespaces are removed from the list items.

    Args:
        string: input string
        separator: The character that separates the different values in the string.
            For example, a comma or newline.

    Returns:
        The list that results from splitting the input string.
            If the original string is empty or consists only of whitespace characters, the resulting list will be empty.

    Raises:
        InputError: If the input value is not a string.

    Examples:
        ```python
        result = xmllib.create_non_empty_list_from_string(" One/  Two\\n/", "/")
        # result == ["One", "Two"]
        ```

        ```python
        result = xmllib.create_list_from_string("   \\n    ", "\\n")
        # result == []
        ```
    """
    if not isinstance(string, str):
        raise_input_error(
            MessageInfo(f"The input for this function must be a string. Your input is a {type(string).__name__}.")
        )
    return [strpd for x in string.split(separator) if (strpd := x.strip())]


def create_non_empty_list_from_string(
    string: str, separator: str, resource_id: str | None = None, prop_name: str | None = None
) -> list[str]:
    """
    Creates a list from a string.
    Trailing and leading whitespaces are removed from the list items.

    If the resulting list is empty it will raise an `InputError`.

    Args:
        string: input string
        separator: The character that separates the different values in the string.
            For example, a comma or newline.
        resource_id: If the ID of the resource is provided, a better error message can be composed
        prop_name: If the name of the property is provided, a better error message can be composed

    Returns:
        The list that results from splitting the input string.

    Raises:
        InputError: If the resulting list is empty.

    Examples:
        ```python
        result = xmllib.create_non_empty_list_from_string("One\\nTwo   ", "\\n")
        # result == ["One", "Two"]
        ```

        ```python
        result = xmllib.create_non_empty_list_from_string("   \\n/    ", "/")
        # raises InputError
        ```
    """
    lst = create_list_from_string(string, separator)
    if len(lst) == 0:
        msg_info = MessageInfo(
            message="The input for this function must result in a non-empty list. Your input results in an empty list.",
            resource_id=resource_id,
            prop_name=prop_name,
        )
        raise_input_error(msg_info)
    return lst


def clean_whitespaces_from_string(string: str) -> str:
    """
    Remove redundant whitespaces (space, `\\n`, `\\t`, etc.) and replace them with a single space.

    If the resulting string is empty, a warning will be printed.

    Args:
        string: input string

    Returns:
        The cleaned string.

    Examples:
        ```python
        result = xmllib.clean_whitespaces_from_string("\\t Text\\nafter newline")
        # result == "Text after newline"
        ```

        ```python
        result = xmllib.clean_whitespaces_from_string("      \\n\\t ")
        # result == ""
        # warns that the string is now empty
        ```
    """
    cleaned = regex.sub(r"\s+", " ", string).strip()
    if len(cleaned) == 0:
        emit_xmllib_input_warning(
            MessageInfo(
                "The entered string is empty after all redundant whitespaces were removed. An empty string is returned."
            )
        )
    return cleaned


def find_license_in_string(string: str) -> License | None:  # noqa: PLR0911 (too many return statements)
    """
    Checks if a string contains a license, and returns it.
    Returns None if no license was found.
    The case (upper case/lower case) is ignored.

    Look out: Your string should contain no more than 1 license.
    If it contains more, there is no guarantee which one will be returned.

    See [recommended licenses](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-api-reference/licenses/recommended/)
    for details.

    Args:
        string: string to check

    Returns:
        `License` object or `None`

    Examples:
        ```python
        result = xmllib.find_license_in_string("CC BY")
        # result == LicenseRecommended.CC.BY
        ```

        ```python
        result = xmllib.find_license_in_string("Creative Commons Developing Nations 2.0 Generic Deed")
        # result == None
        ```

    Currently supported license formats:
        - "AI" -> LicenseRecommended.DSP.AI_GENERATED
        - "KI" -> LicenseRecommended.DSP.AI_GENERATED
        - "IA" -> LicenseRecommended.DSP.AI_GENERATED
        - "public domain" -> LicenseRecommended.DSP.PUBLIC_DOMAIN
        - "gemeinfrei" -> LicenseRecommended.DSP.PUBLIC_DOMAIN
        - "frei von Urheberrechten" -> LicenseRecommended.DSP.PUBLIC_DOMAIN
        - "urheberrechtsbefreit" -> LicenseRecommended.DSP.PUBLIC_DOMAIN
        - "libre de droits" -> LicenseRecommended.DSP.PUBLIC_DOMAIN
        - "domaine public" -> LicenseRecommended.DSP.PUBLIC_DOMAIN
        - "unknown" -> LicenseRecommended.DSP.UNKNOWN
        - "unbekannt" -> LicenseRecommended.DSP.UNKNOWN
        - "inconnu" -> LicenseRecommended.DSP.UNKNOWN
        - "CC BY" -> LicenseRecommended.CC.BY
        - "Creative Commons BY 4.0" -> LicenseRecommended.CC.BY
        - "CC 0 1.0" -> LicenseOther.Public.CC_0_1_0
        - "CC PDM 1.0" -> LicenseOther.Public.CC_PDM_1_0
        - "BORIS Standard License" -> LicenseOther.Various.BORIS_STANDARD
        - "LICENCE OUVERTE 2.0" -> LicenseOther.Various.FRANCE_OUVERTE
    """
    if lic := _get_already_parsed_license(string):
        return lic

    sep = r"[-_\p{Zs}]+"  # Zs = unicode category for space separator characters

    if regex.search(rf"\b(Creative{sep}Commons|CC){sep}0({sep}1\.0)?\b", string, flags=regex.IGNORECASE):
        return LicenseOther.Public.CC_0_1_0

    if regex.search(rf"\b(Creative{sep}Commons|CC){sep}PDM({sep}1\.0)?\b", string, flags=regex.IGNORECASE):
        return LicenseOther.Public.CC_PDM_1_0

    if match := regex.search(
        rf"\b(CC|Creative{sep}Commons)({sep}(BY|NC|ND|SA))*({sep}[\d\.]+)?\b", string, flags=regex.IGNORECASE
    ):
        return _find_cc_license(match.group(0))

    if regex.search(r"\b(AI|IA|KI)\b", string, flags=regex.IGNORECASE):
        return LicenseRecommended.DSP.AI_GENERATED

    rgx_public_domain = (
        rf"\b(public{sep}domain|gemeinfrei|frei{sep}von{sep}Urheberrechten|urheberrechtsbefreit|"
        rf"libre{sep}de{sep}droits|domaine{sep}public)\b"
    )
    if regex.search(rgx_public_domain, string, flags=regex.IGNORECASE):
        return LicenseRecommended.DSP.PUBLIC_DOMAIN

    if regex.search(r"\b(unknown|unbekannt|inconnu)\b", string, flags=regex.IGNORECASE):
        return LicenseRecommended.DSP.UNKNOWN

    if regex.search(
        rf"\b(BORIS|Bern{sep}Open{sep}Repository{sep}and{sep}Information{sep}System){sep}Standard{sep}License\b",
        string,
        flags=regex.IGNORECASE,
    ):
        return LicenseOther.Various.BORIS_STANDARD

    if regex.search(
        rf"\b(France{sep})?Licence{sep}ouverte({sep}2\.0)?\b",
        string,
        flags=regex.IGNORECASE,
    ):
        return LicenseOther.Various.FRANCE_OUVERTE

    return None


def _find_cc_license(string: str) -> License | None:  # noqa: PLR0911 (too many return statements)
    string = string.lower()
    if "by" not in string:
        return None
    if any((string.count("by") > 1, string.count("nd") > 1, string.count("sa") > 1, string.count("nc") > 1)):
        return None
    has_nc = "nc" in string
    has_nd = "nd" in string
    has_sa = "sa" in string
    if not any((has_nc, has_nd, has_sa)):
        return LicenseRecommended.CC.BY
    if not has_nc and has_nd and not has_sa:
        return LicenseRecommended.CC.BY_ND
    if not has_nc and not has_nd and has_sa:
        return LicenseRecommended.CC.BY_SA
    if has_nc and not has_nd and not has_sa:
        return LicenseRecommended.CC.BY_NC
    if has_nc and has_nd and not has_sa:
        return LicenseRecommended.CC.BY_NC_ND
    if has_nc and not has_nd and has_sa:
        return LicenseRecommended.CC.BY_NC_SA
    return None


def _get_already_parsed_license(string: str) -> License | None:
    already_parsed_dict: dict[str, License] = {
        r"http://rdfh\.ch/licenses/cc-by-4\.0": LicenseRecommended.CC.BY,
        r"http://rdfh\.ch/licenses/cc-by-sa-4\.0": LicenseRecommended.CC.BY_SA,
        r"http://rdfh\.ch/licenses/cc-by-nc-4\.0": LicenseRecommended.CC.BY_NC,
        r"http://rdfh\.ch/licenses/cc-by-nc-sa-4\.0": LicenseRecommended.CC.BY_NC_SA,
        r"http://rdfh\.ch/licenses/cc-by-nd-4\.0": LicenseRecommended.CC.BY_ND,
        r"http://rdfh\.ch/licenses/cc-by-nc-nd-4\.0": LicenseRecommended.CC.BY_NC_ND,
        r"http://rdfh\.ch/licenses/ai-generated": LicenseRecommended.DSP.AI_GENERATED,
        r"http://rdfh\.ch/licenses/unknown": LicenseRecommended.DSP.UNKNOWN,
        r"http://rdfh\.ch/licenses/public-domain": LicenseRecommended.DSP.PUBLIC_DOMAIN,
        r"http://rdfh\.ch/licenses/cc-0-1.0": LicenseOther.Public.CC_0_1_0,
        r"http://rdfh\.ch/licenses/cc-pdm-1.0": LicenseOther.Public.CC_PDM_1_0,
        r"http://rdfh\.ch/licenses/boris": LicenseOther.Various.BORIS_STANDARD,
        r"http://rdfh\.ch/licenses/open-licence-2.0": LicenseOther.Various.FRANCE_OUVERTE,
    }
    for rgx, lic in already_parsed_dict.items():
        if regex.search(rgx, string):
            return lic
    return None
