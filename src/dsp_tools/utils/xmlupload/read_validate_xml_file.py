from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Union

from lxml import etree

from dsp_tools.models.exceptions import UserError
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def parse_xml_file(input_file: Union[str, Path, etree._ElementTree[Any]]) -> etree._Element:
    """
    Parse an XML file with DSP-conform data,
    remove namespace URI from the elements' names,
    and transform the special tags <annotation>, <region>, and <link>
    to their technically correct form
    <resource restype="Annotation">, <resource restype="Region">, and <resource restype="LinkObj">.

    Args:
        input_file: path to the XML file, or parsed ElementTree

    Returns:
        the root element of the parsed XML file
    """

    # remove comments and processing instructions (commented out properties break the XMLProperty constructor)
    if isinstance(input_file, (str, Path)):
        parser = etree.XMLParser(remove_comments=True, remove_pis=True)
        tree = etree.parse(source=input_file, parser=parser)
    else:
        tree = copy.deepcopy(input_file)
        for c in tree.xpath("//comment()"):
            c.getparent().remove(c)
        for c in tree.xpath("//processing-instruction()"):
            c.getparent().remove(c)

    # remove namespace URI from the elements' names and transform the special tags to their technically correct form
    for elem in tree.iter():
        elem.tag = etree.QName(elem).localname  # remove namespace URI in the element's name
        if elem.tag == "annotation":
            elem.attrib["restype"] = "Annotation"
            elem.tag = "resource"
        elif elem.tag == "link":
            elem.attrib["restype"] = "LinkObj"
            elem.tag = "resource"
        elif elem.tag == "region":
            elem.attrib["restype"] = "Region"
            elem.tag = "resource"

    return tree.getroot()


def _check_if_onto_name_exists(
    resclass_name_2_type: dict[str, type],
    ontoname: str,
    shortcode: str,
) -> None:
    """
    Check if the "default-ontology" of the <knora> tag of the XML file exists on the DSP server.

    Args:
        resclass_name_2_type: infos about the resource classes that exist on the DSP server for the current ontology
        ontoname: name of the ontology as referenced in the XML file
        shortcode: shortcode of the project as referenced in the XML file

    Raises:
        UserError: if the ontology does not exist on the DSP server
    """
    existing_onto_names = {x.split(":")[0] for x in resclass_name_2_type}
    existing_onto_names.remove("knora-api")
    if ontoname not in existing_onto_names:
        err_msg = (
            f"ERROR: The <knora> tag of your XML file references the default-ontology '{ontoname}', "
            f"but the project {shortcode} on the DSP server contains only the ontologies {existing_onto_names}"
        )
        logger.error(err_msg)
        raise UserError(err_msg)


def check_consistency_with_ontology(
    resources: list[XMLResource],
    resclass_name_2_type: dict[str, type],
    shortcode: str,
    ontoname: str,
    verbose: bool = False,
) -> None:
    """
    Checks if the "default-ontology" of the <knora> tag of the XML file exists on the DSP server,
    and if the resource types and property types in the XML are consistent with the ontology.

    Args:
        resources: a list of parsed XMLResources
        resclass_name_2_type: infos about the resource classes that exist on the DSP server for the current ontology
        shortcode: the shortcode of the project
            as referenced in the attribute "shortcode" of the <knora> tag of the XML file
        ontoname: the name of the ontology
            as referenced in the attribute "default-ontology" of the <knora> tag of the XML file
        verbose: verbose switch

    Raises:
        UserError: if there is an inconsistency between the ontology and the data
    """
    if verbose:
        print("Check if the resource types and properties are consistent with the ontology...")
        logger.info("Check if the resource types and properties are consistent with the ontology...")
    _check_if_onto_name_exists(
        resclass_name_2_type=resclass_name_2_type,
        ontoname=ontoname,
        shortcode=shortcode,
    )
    _check_if_resource_types_exist(resources=resources, resclass_name_2_type=resclass_name_2_type)
    _check_if_property_types_exist(resources=resources, resclass_name_2_type=resclass_name_2_type)


def _check_if_resource_types_exist(
    resources: list[XMLResource],
    resclass_name_2_type: dict[str, type],
) -> None:
    """
    Check if the resource types in the XML file are consistent with the ontology.

    Args:
        resources: a list of parsed XMLResources
        resclass_name_2_type: infos about the resource classes that exist on the DSP server for the current ontology

    Raises:
        UserError: if there is an inconsistency between the ontology and the data
    """
    for resource in resources:
        # check that the resource type is consistent with the ontology
        if resource.restype not in resclass_name_2_type:
            res_syntaxes = [
                'DSP-API internals: <resource restype="restype">',
                'current ontology:  <resource restype=":restype">',
                'other ontology:    <resource restype="other:restype">',
            ]
            res_explanations = [
                'will be interpreted as "knora-api:restype"',
                '"restype" must be defined in the "resources" section of your ontology',
                'not yet implemented: "other" must be defined in the same JSON project file as your ontology',
            ]
            err_msg = (
                f"=========================\n"
                f"ERROR: Resource '{resource.label}' (ID: {resource.id}) "
                f"has an invalid resource type '{resource.restype}'. "
                "Is your syntax correct? Remember the rules:\n"
            )
            for res_syntax, res_explanation in zip(res_syntaxes, res_explanations):
                err_msg += f" - {res_syntax:<55} ({res_explanation})\n"
            logger.error(err_msg)
            raise UserError(err_msg)


def _check_if_property_types_exist(
    resources: list[XMLResource],
    resclass_name_2_type: dict[str, type],
) -> None:
    """
    Check if the property types in the XML file are either a DSP base property
    or a property that was defined for this specific resource (not every resource can have every property).

    Args:
        resources: a list of parsed XMLResources
        resclass_name_2_type: infos about the resource classes that exist on the DSP server for the current ontology

    Raises:
        UserError: if there is an inconsistency between the ontology and the data
    """
    knora_properties = resclass_name_2_type[resources[0].restype].knora_properties  # type: ignore[attr-defined]
    for resource in resources:
        # check that the property types are consistent with the ontology
        resource_properties = resclass_name_2_type[resource.restype].properties.keys()  # type: ignore[attr-defined]
        for propname in [prop.name for prop in resource.properties]:
            if propname not in knora_properties and propname not in resource_properties:
                prop_syntaxes = [
                    'DSP-API internals: <text-prop name="propname">',
                    'current ontology:  <text-prop name=":propname">',
                    'other ontology:    <text-prop name="other:propname">',
                ]
                prop_explanations = [
                    'will be interpreted as "knora-api:propname"',
                    '"propname" must be defined in the "properties" section of your ontology',
                    'not yet implemented: "other" must be defined in the same JSON project file as your ontology',
                ]
                err_msg = (
                    f"=========================\n"
                    f"ERROR: Resource '{resource.label}' (ID: {resource.id}) has an invalid property '{propname}'. "
                    f"Is your syntax correct? Remember the rules:\n"
                )
                for prop_syntax, prop_explanation in zip(prop_syntaxes, prop_explanations):
                    err_msg += f" - {prop_syntax:<55} ({prop_explanation})\n"
                logger.error(err_msg)
                raise UserError(err_msg)

    print("Resource types and properties are consistent with the ontology.")
    logger.info("Resource types and properties are consistent with the ontology.")


def check_if_bitstreams_exist(
    root: etree._Element,
    imgdir: str,
) -> None:
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
        pth = [Path(x.text) for x in res.iter() if x.tag == "bitstream" and x.text][0]
        if not Path(imgdir / pth).is_file():
            raise UserError(
                f"Bitstream '{pth!s}' of resource '{res.attrib['label']}' does not exist in the imgdir '{imgdir}'."
            )
