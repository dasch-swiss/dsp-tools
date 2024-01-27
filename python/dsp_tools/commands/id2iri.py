import copy
import json
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path

import regex
from lxml import etree

from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.xml_utils import parse_and_clean_xml_file

logger = get_logger(__name__)


def _check_input_parameters(
    xml_file: str,
    json_file: str,
) -> tuple[Path, Path]:
    """
    Transform the input parameters into Path objects
    and check if they are valid files.

    Args:
        xml_file: the XML file with the data to be replaced
        json_file: the JSON file with the mapping (dict) of internal IDs to IRIs

    Raises:
        UserError: if one of the files could not be found

    Returns:
        path objects of the input parameters
    """
    xml_file_as_path = Path(xml_file)
    if not xml_file_as_path.is_file():
        logger.error(f"File {xml_file} could not be found.")
        raise UserError(f"File {xml_file} could not be found.")

    json_file_as_path = Path(json_file)
    if not json_file_as_path.is_file():
        logger.error(f"File {json_file} could not be found.")
        raise UserError(f"File {json_file} could not be found.")

    return xml_file_as_path, json_file_as_path


def _parse_json_file(json_file: Path) -> dict[str, str]:
    """
    Read JSON file and parse it into a dictionary.

    Args:
        json_file: path to JSON file

    Returns:
        dictionary with the contents of the JSON file
    """
    with open(json_file, encoding="utf-8", mode="r") as file:
        mapping: dict[str, str] = json.load(file)
    return mapping


def _replace_resptrs(
    tree: etree._Element,
    mapping: Mapping[str, str],
    used_mapping_entries: set[str],
) -> tuple[etree._Element, set[str]]:
    """
    Replace the internal IDs in the <resptr> tags by IRIs.

    Args:
        tree: parsed XML file
        mapping: mapping of internal IDs to IRIs
        used_mapping_entries: IDs of the mapping that have been found in the XML and have been replaced

    Returns:
        a tuple of the modified copy of the XML tree, and the set of the IDs that have been replaced
    """
    modified_tree = copy.deepcopy(tree)
    resptr_xpath = "|".join([f"/knora/{x}/resptr-prop/resptr" for x in ["resource", "annotation", "link", "region"]])
    resptr_elems = modified_tree.xpath(resptr_xpath)
    resptr_elems_replaced = 0
    for resptr_elem in resptr_elems:
        value_before = resptr_elem.text
        if value_after := mapping.get(value_before):
            resptr_elem.text = value_after
            resptr_elems_replaced += 1
            used_mapping_entries.add(value_before)

    logger.info(f"Replaced {resptr_elems_replaced}/{len(resptr_elems)} resptr links in the XML file")
    print(f"Replaced {resptr_elems_replaced}/{len(resptr_elems)} resptr links in the XML file")

    return modified_tree, used_mapping_entries


def _replace_salsah_links(
    tree: etree._Element,
    mapping: Mapping[str, str],
    used_mapping_entries: set[str],
) -> tuple[etree._Element, set[str]]:
    """
    Replace the internal IDs in the salsah-links of the <text> tags by IRIs.

    Args:
        tree: parsed XML file
        mapping: mapping of internal IDs to IRIs
        used_mapping_entries: IDs of the mapping that have been found in the XML and have been replaced

    Returns:
        a tuple of the modified copy of the XML tree, and the set of the IDs that have been replaced
    """
    modified_tree = copy.deepcopy(tree)
    salsah_xpath = "|".join([f"/knora/{x}/text-prop/text//a" for x in ["resource", "annotation", "link", "region"]])
    salsah_links = [x for x in modified_tree.xpath(salsah_xpath) if x.attrib.get("class") == "salsah-link"]
    salsah_links_replaced = 0
    for salsah_link in salsah_links:
        value_before = regex.sub("IRI:|:IRI", "", salsah_link.attrib.get("href", ""))
        if value_after := mapping.get(value_before):
            salsah_link.attrib["href"] = value_after
            salsah_links_replaced += 1
            used_mapping_entries.add(value_before)

    logger.info(f"Replaced {salsah_links_replaced}/{len(salsah_links)} salsah-links in the XML file")
    print(f"Replaced {salsah_links_replaced}/{len(salsah_links)} salsah-links in the XML file")

    return modified_tree, used_mapping_entries


def _replace_ids_by_iris(
    tree: etree._Element,
    mapping: Mapping[str, str],
) -> etree._Element:
    """
    Iterate over the <resptr> tags and the salsah-links of the <text> tags,
    and replace the internal IDs by IRIs.
    If an internal ID cannot be found in the mapping, the original ID is kept.

    Args:
        tree: parsed XML file
        mapping: mapping of internal IDs to IRIs

    Returns:
        a modified copy of the XML tree
    """
    used_mapping_entries: set[str] = set()

    tree, used_mapping_entries = _replace_resptrs(
        tree=tree,
        mapping=mapping,
        used_mapping_entries=used_mapping_entries,
    )

    tree, used_mapping_entries = _replace_salsah_links(
        tree=tree,
        mapping=mapping,
        used_mapping_entries=used_mapping_entries,
    )

    logger.info(f"Used {len(used_mapping_entries)}/{len(mapping)} entries from the mapping file")
    print(f"Used {len(used_mapping_entries)}/{len(mapping)} entries from the mapping file")

    return tree


def _remove_resources_if_id_in_mapping(
    tree: etree._Element,
    mapping: Mapping[str, str],
) -> etree._Element:
    """
    Remove all resources from the XML file if their ID is in the mapping.

    Args:
        tree: parsed XML file
        mapping: mapping of internal IDs to IRIs

    Returns:
        a modified copy of the XML tree
    """
    modified_tree = copy.deepcopy(tree)
    resources = modified_tree.xpath("|".join([f"/knora/{x}" for x in ["resource", "annotation", "link", "region"]]))
    resources_to_remove = [x for x in resources if x.attrib.get("id") in mapping]
    for resource in resources_to_remove:
        resource.getparent().remove(resource)

    msg = (
        f"Removed {len(resources_to_remove)}/{len(resources)} resources from the XML file, "
        "because their ID was in the mapping"
    )
    logger.info(msg)
    print(msg)

    return modified_tree


def _write_output_file(
    orig_xml_file: Path,
    tree: etree._Element,
) -> None:
    """
    Write modified XML file with replaced IDs to disk.

    Args:
        orig_xml_file: XML file that was provided as input
        tree: modified XML tree with replaced IDs
    """
    timestamp_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_file = f"{orig_xml_file.stem}_replaced_{timestamp_str}.xml"
    et = etree.ElementTree(tree)
    et.write(out_file, pretty_print=True, xml_declaration=True, encoding="utf-8")
    logger.info(f"XML with replaced IDs was written to file {out_file}.")
    print(f"XML with replaced IDs was written to file {out_file}.")


def id2iri(
    xml_file: str,
    json_file: str,
    remove_resource_if_id_in_mapping: bool = False,
) -> bool:
    """
    Replace internal IDs of an XML file
    (<resptr> tags and salsah-links inside <text> tags)
    by IRIs provided in a mapping file.
    If an internal ID cannot be found in the mapping, the original ID is kept.
    The output is written to a new XML file named "[original name]_replaced_[timestamp].xml".

    Args:
        xml_file: the XML file with the data to be replaced
        json_file: the JSON file with the mapping (dict) of internal IDs to IRIs
        remove_resource_if_id_in_mapping: if True, remove all resources from the XML file if their ID is in the mapping

    Raises:
        BaseError: if one of the two input files is not a valid file

    Returns:
        success status
    """
    xml_file_as_path, json_file_as_path = _check_input_parameters(xml_file=xml_file, json_file=json_file)
    mapping = _parse_json_file(json_file_as_path)
    tree = parse_and_clean_xml_file(xml_file_as_path)
    tree = _replace_ids_by_iris(
        tree=tree,
        mapping=mapping,
    )
    if remove_resource_if_id_in_mapping:
        tree = _remove_resources_if_id_in_mapping(
            tree=tree,
            mapping=mapping,
        )
    _write_output_file(orig_xml_file=xml_file_as_path, tree=tree)
    return True
