from __future__ import annotations

import json
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import regex
from lxml import etree

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.error.xmllib_warnings_util import raise_xmllib_input_error
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
        XmllibInputError: If the text is empty, or if a newline replacement which is not implemented is entered

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
        XmllibInputError: If the text is empty, or if a newline replacement which is not implemented is entered

    Returns:
        The footnote as a string
    """
    if newline_replacement_option not in {NewlineReplacement.LINEBREAK, NewlineReplacement.NONE}:
        raise_xmllib_input_error(
            MessageInfo("Currently the only supported newline replacement is linebreak (<br/>) or None.")
        )
    if not is_nonempty_value_internal(footnote_text):
        raise_xmllib_input_error(MessageInfo("The input value is empty."))
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
        XmllibInputError: if the resource ID or the displayed text are empty

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
        raise_xmllib_input_error(MessageInfo(msg_str))
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
        XmllibInputError: if the URI or the displayed text are empty

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
        raise_xmllib_input_error(MessageInfo(msg_str))
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
    Resolves list labels to node names.

    Args:
        string_with_list_labels: the string containing list labels
        label_separator: separator in the string that contains the labels
        list_name: name of the list
        list_lookup: `ListLookup` of the project

    Returns:
        A list of node names. If the string is empty, it returns an empty list.

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
    labels_list = create_list_from_input(string_with_list_labels, label_separator)
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
    labels_list = create_list_from_input(string_with_list_labels, label_separator)
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
            # the actual values of the name and the label
            if found := node["labels"].get(language_of_label):
                yield found, node["name"]
            else:
                msg = (
                    f"The language of the labels is '{language_of_label}', "
                    f"the list node with the name '{node['name']}' does not have a label in this language."
                )
                emit_xmllib_input_warning(MessageInfo(msg))


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
        XmllibInputError: if the input cannot be transformed to an xsd:ID

    Returns:
        An xsd ID compatible string based on the input value

    Examples:
        ```python
        result = xmllib.make_xsd_compatible_id("0_Universität_Basel")
        # result == "_0_Universit_t_Basel"
        ```
    """
    if not is_nonempty_value_internal(input_value):
        raise_xmllib_input_error(MessageInfo(f"The input '{input_value}' cannot be transformed to an xsd:ID"))
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
        XmllibInputError: if the input cannot be transformed to an xsd:ID

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


def create_list_from_string(string: str, separator: str) -> list[str]:  # noqa:ARG001
    """
    Attention:
        This function is deprecated, use the new function called 'create_list_from_input' instead.
    """
    raise_xmllib_input_error(
        MessageInfo(
            "The function 'create_list_from_string' is deprecated. "
            "Use the new function called 'create_list_from_input' instead."
        )
    )


def create_list_from_input(input_value: Any, separator: str) -> list[str]:
    """
    Create a list of strings from the input value, using the provided separator.
    If the input is empty it returns an empty list.

    Args:
        input_value: input value to check and convert
        separator: The character that separates the different values in the string.
            For example, a comma or newline.

    Returns:
        The list that results from splitting the input string.

    Examples:
        ```python
        result = xmllib.create_list_from_input("  one, two,  three", ",")
        # result == ["one", "two", "three"]
        ```

        ```python
        result = xmllib.create_list_from_input(1, "-")
        # result == ["1"]
        ```

        ```python
        result = xmllib.create_list_from_input("   \\n    ", "\\n")
        # result == []
        ```

        ```python
        result = xmllib.create_list_from_input(None, ",")
        # result == []
        ```
    """
    if not is_nonempty_value_internal(input_value):
        return []
    if isinstance(input_value, str):
        return [strpd for x in input_value.split(separator) if (strpd := x.strip())]
    return [str(input_value)]


def create_non_empty_list_from_string(
    string: str, separator: str, resource_id: str | None = None, prop_name: str | None = None
) -> list[str]:
    """
    Creates a list from a string.
    Trailing and leading whitespaces are removed from the list items.

    If the resulting list is empty it will raise an `XmllibInputError`.

    Args:
        string: input string
        separator: The character that separates the different values in the string.
            For example, a comma or newline.
        resource_id: If the ID of the resource is provided, a better error message can be composed
        prop_name: If the name of the property is provided, a better error message can be composed

    Returns:
        The list that results from splitting the input string.

    Raises:
        XmllibInputError: If the resulting list is empty.

    Examples:
        ```python
        result = xmllib.create_non_empty_list_from_string("One\\nTwo   ", "\\n")
        # result == ["One", "Two"]
        ```

        ```python
        result = xmllib.create_non_empty_list_from_string("   \\n/    ", "/")
        # raises XmllibInputError
        ```
    """
    lst = create_list_from_input(string, separator)
    if len(lst) == 0:
        msg_info = MessageInfo(
            message="The input for this function must result in a non-empty list. Your input results in an empty list.",
            resource_id=resource_id,
            prop_name=prop_name,
        )
        raise_xmllib_input_error(msg_info)
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

    See [recommended licenses](https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/licenses/recommended/)
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
