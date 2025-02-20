from __future__ import annotations

import warnings
from datetime import datetime
from pathlib import Path

import regex
from lxml import etree

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.iri_util import is_resource_iri
from dsp_tools.utils.xml_parsing.models.text_value_validation import InconsistentTextValueEncodings
from dsp_tools.utils.xml_parsing.models.text_value_validation import TextValueData
from dsp_tools.utils.xml_parsing.parse_and_clean import parse_and_basic_cleaning
from dsp_tools.utils.xml_parsing.parse_and_transform_file import transform_special_tags_make_localname
from dsp_tools.utils.xml_parsing.schema_validation import validate_xml_with_schema
from dsp_tools.utils.xml_parsing.validations import list_separator


def prepare_input_xml_file(input_file: Path, imgdir: str) -> tuple[etree._Element, str, str]:
    """
    Parses the file and does some rudimentary checks.

    Args:
        input_file: input XML
        imgdir: directory of the images

    Returns:
        The root element of the parsed XML file, the shortcode, and the default ontology
    """
    root, shortcode, default_ontology = validate_and_parse(input_file)
    check_if_bitstreams_exist(root, imgdir)
    return root, shortcode, default_ontology


def validate_and_parse(input_file: Path) -> tuple[etree._Element, str, str]:
    """Parse and validate an XML file.

    Args:
        input_file: Path to the XML file

    Returns:
        The root element of the parsed XML file, the shortcode, and the default ontology
    """
    root = parse_and_basic_cleaning(input_file)

    validate_xml_with_schema(root)
    print("The XML file is syntactically correct.")
    root = transform_special_tags_make_localname(root)
    check_if_link_targets_exist(root)
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    return root, shortcode, default_ontology


def check_if_link_targets_exist(root: etree._Element) -> None:
    """
    Make sure that all targets of links (resptr and salsah-links)
    are either IRIs or IDs that exist in the present XML file.

    Args:
        root: parsed XML file

    Raises:
        UserError: if a link target does not exist in the XML file
    """
    resptr_errors = _check_if_resptr_targets_exist(root)
    salsah_errors = _check_if_salsah_targets_exist(root)
    if errors := resptr_errors + salsah_errors:
        sep = "\n - "
        msg = f"It is not possible to upload the XML file, because it contains invalid links:{sep}{sep.join(errors)}"
        raise UserError(msg)


def _check_if_resptr_targets_exist(root: etree._Element) -> list[str]:
    link_values = [x for x in root.iter() if x.tag == "resptr"]
    resource_ids = [x.attrib["id"] for x in root.iter() if x.tag == "resource"]
    invalid_link_values = [x for x in link_values if x.text not in resource_ids]
    invalid_link_values = [x for x in invalid_link_values if not is_resource_iri(str(x.text))]
    errors = []
    for inv in invalid_link_values:
        prop_name = next(inv.iterancestors(tag="resptr-prop")).attrib["name"]
        res_id = next(inv.iterancestors(tag="resource")).attrib["id"]
        errors.append(f"Resource '{res_id}', property '{prop_name}' has an invalid link target '{inv.text}'")
    return errors


def _check_if_salsah_targets_exist(root: etree._Element) -> list[str]:
    link_values = [x for x in root.iter() if x.tag == "a"]
    resource_ids = [x.attrib["id"] for x in root.iter() if x.tag == "resource"]
    invalid_link_values = [x for x in link_values if regex.sub(r"IRI:|:IRI", "", x.attrib["href"]) not in resource_ids]
    invalid_link_values = [x for x in invalid_link_values if x.attrib.get("class") == "salsah-link"]
    invalid_link_values = [x for x in invalid_link_values if not is_resource_iri(x.attrib["href"])]
    errors = []
    for inv in invalid_link_values:
        prop_name = next(inv.iterancestors(tag="text-prop")).attrib["name"]
        res_id = next(inv.iterancestors(tag="resource")).attrib["id"]
        errors.append(f"Resource '{res_id}', property '{prop_name}' has an invalid link target '{inv.attrib['href']}'")
    return errors


def check_if_bitstreams_exist(root: etree._Element, imgdir: str) -> None:
    """
    Make sure that all bitstreams referenced in the XML file exist in the imgdir.

    Args:
        root: parsed XML file
        imgdir: folder where the bitstreams are stored

    Raises:
        UserError: if a bitstream does not exist in the imgdir
    """
    multimedia_resources = [x for x in root if any((y.tag == "bitstream" for y in x.iter()))]
    for res in multimedia_resources:
        pth = next(Path(x.text.strip()) for x in res.iter() if x.tag == "bitstream" and x.text)
        if not Path(imgdir / pth).is_file():
            raise UserError(
                f"Bitstream '{pth!s}' of resource '{res.attrib['label']}' does not exist in the imgdir '{imgdir}'."
            )


def find_mixed_encodings_in_text_tags(xml_no_namespace: etree._Element) -> list[str]:
    """Finds if any text tags contain mixed encoding."""
    problems = []
    _find_xml_tags_in_simple_text_elements(xml_no_namespace)
    problems.extend(_find_mixed_encodings_in_one_text_prop(xml_no_namespace))
    _check_for_deprecated_syntax(xml_no_namespace)
    return problems


def _find_xml_tags_in_simple_text_elements(xml_no_namespace: etree._Element) -> None:
    """
    Checks if there are angular brackets in simple text.
    It is possible that the user mistakenly added XML tags into a simple text field.
    But it is also possible that an angular bracket should be displayed.
    So that the user does not insert XML tags mistakenly into simple text fields,
    the user is warned, if there is any present.
    """
    resources_with_potential_xml_tags = []
    for text in xml_no_namespace.findall(path="resource/text-prop/text"):
        regex_finds_tags = bool(regex.search(r'<([a-zA-Z/"]+|[^\s0-9].*[^\s0-9])>', str(text.text)))
        etree_finds_tags = bool(list(text.iterchildren()))
        has_tags = regex_finds_tags or etree_finds_tags
        if text.attrib["encoding"] == "utf8" and has_tags:
            sourceline = f"line {text.sourceline}: " if text.sourceline else " "
            propname = text.getparent().attrib["name"]  # type: ignore[union-attr]
            resname = text.getparent().getparent().attrib["id"]  # type: ignore[union-attr]
            resources_with_potential_xml_tags.append(f"{sourceline}resource '{resname}', property '{propname}'")
    if resources_with_potential_xml_tags:
        err_msg = (
            "Angular brackets in the format of <text> were found in text properties with encoding=utf8.\n"
            "Please note that these will not be recognised as formatting in the text field, "
            "but will be displayed as-is.\n"
            f"The following resources of your XML file contain angular brackets:{list_separator}"
            f"{list_separator.join(resources_with_potential_xml_tags)}"
        )
        warnings.warn(DspToolsUserWarning(err_msg))


def _find_mixed_encodings_in_one_text_prop(xml_no_namespace: etree._Element) -> list[str]:
    problems = check_if_only_one_encoding_is_used_per_prop_in_root(xml_no_namespace)
    if not problems:
        return []
    msg, df = InconsistentTextValueEncodings(problems).execute_problem_protocol()
    if df is not None:
        csv_path = Path(f"XML_syntax_errors_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv")
        msg = f"\nAll the problems are listed in the file: '{csv_path.absolute()}'{msg}"
        df.to_csv(csv_path)
    return [msg]


def _check_for_deprecated_syntax(data_xml: etree._Element) -> None:
    pass


def check_if_only_one_encoding_is_used_per_prop_in_root(
    root: etree._Element,
) -> list[TextValueData]:
    """
    Check if all the encodings in the `<text>` elements are consistent within one `<text-prop>`

    This is correct:
    ```
    <text-prop name=":hasSimpleText">
        <text encoding="utf8">Text 1</text>
        <text encoding="utf8">Text 2</text>
    </text-prop>
    ```

    This is wrong:
    ```
    <text-prop name=":hasSimpleText">
        <text encoding="utf8">Text 1</text>
        <text encoding="xml">Text 2</text>
    </text-prop>
    ```

    Args:
        root: root of the data xml document

    Returns:
          A list of all the inconsistent `<text-props>`
    """
    text_props = _get_all_ids_and_encodings_from_root(root)
    return _find_all_text_props_with_multiple_encodings(text_props)


def _get_all_ids_and_encodings_from_root(
    root: etree._Element,
) -> list[TextValueData]:
    res_list = []
    for res_input in root.iterchildren(tag="resource"):
        res_list.extend(_get_encodings_from_one_resource(res_input))
    return res_list


def _get_encodings_from_one_resource(resource: etree._Element) -> list[TextValueData]:
    res_id = resource.attrib["id"]
    return [_get_encodings_from_one_property(res_id, child) for child in list(resource.iterchildren(tag="text-prop"))]


def _get_encodings_from_one_property(res_id: str, prop: etree._Element) -> TextValueData:
    prop_name = prop.attrib["name"]
    encodings = {x.attrib["encoding"] for x in prop.iterchildren()}
    return TextValueData(res_id, prop_name, encodings)


def _find_all_text_props_with_multiple_encodings(text_props: list[TextValueData]) -> list[TextValueData]:
    return [x for x in text_props if len(x.encoding) != 1]
