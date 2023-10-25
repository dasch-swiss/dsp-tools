from copy import deepcopy
from importlib import resources

import regex
from lxml import etree

from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def remove_qnames_and_transform_special_tags(
    root: etree._Element,
) -> etree._Element:
    cp = deepcopy(root)
    for elem in cp.iter():
        elem.tag = etree.QName(elem).localname  # remove namespace URI in the element's name
        match elem.tag:
            case "annotation":
                elem.attrib["restype"] = "Annotation"
                elem.tag = "resource"
            case "region":
                elem.attrib["restype"] = "Region"
                elem.tag = "resource"
            case "link":
                # raise NotImplementedError("Link Objects are not supported right now.")
                elem.attrib["restype"] = "LinkObj"
                elem.tag = "resource"
    return cp


def validate_xml_against_schema(xml: etree._Element) -> tuple[bool, str | None]:
    """
    Validates an XML file against the DSP XSD schema.

    Args:
        xml: the xml element tree to be validated

    Returns:
        True and None if the XML file is valid, False and an error message if not
    """
    with resources.files("dsp_tools").joinpath("resources/schema/data.xsd").open(encoding="utf-8") as schema_file:
        xmlschema = etree.XMLSchema(etree.parse(schema_file))

    if not xmlschema.validate(xml):
        error_msg = "The XML file cannot be uploaded due to the following validation error(s):"
        for error in xmlschema.error_log:
            error_msg = error_msg + f"\n  Line {error.line}: {error.message}"
        error_msg = error_msg.replace("{https://dasch.swiss/schema}", "")
        return False, error_msg

    logger.info("The XML file is syntactically correct and passed validation.")
    print("The XML file is syntactically correct and passed validation.")
    return True, None


def validate_xml_tags_in_text_properties(xml: etree._Element) -> tuple[bool, str | None]:
    """
    Makes sure that there are no XML tags in simple texts.
    This can only be done with a regex,
    because even if the simple text contains some XML tags,
    the simple text itself is not valid XML that could be parsed.
    The extra challenge is that lxml transforms
    "pebble (&lt;2cm) and boulder (&gt;20cm)" into
    "pebble (<2cm) and boulder (>20cm)"
    (but only if &gt; follows &lt;).
    This forces us to write a regex that carefully distinguishes
    between a real tag (which is not allowed) and a false-positive-tag.

    Args:
        xml: parsed XML file

    Returns:
        True and None if the XML file is valid, False and an error message if not
    """
    resources_with_illegal_xml_tags = list()
    for text in xml.findall(path="resource/text-prop/text"):
        if text.attrib["encoding"] == "utf8":
            if (
                regex.search(r'<([a-zA-Z/"]+|[^\s0-9].*[^\s0-9])>', str(text.text))
                or len(list(text.iterchildren())) > 0
            ):
                sourceline = f" line {text.sourceline}: " if text.sourceline else " "
                propname = text.getparent().attrib["name"]  # type: ignore[union-attr]
                resname = text.getparent().getparent().attrib["id"]  # type: ignore[union-attr]
                resources_with_illegal_xml_tags.append(f" -{sourceline}resource '{resname}', property '{propname}'")
    if resources_with_illegal_xml_tags:
        err_msg = (
            "XML-tags are not allowed in text properties with encoding=utf8. "
            "The following resources of your XML file violate this rule:\n"
        )
        err_msg += "\n".join(resources_with_illegal_xml_tags)
        return False, err_msg

    return True, None
