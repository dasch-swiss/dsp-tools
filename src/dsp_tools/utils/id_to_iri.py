import json
from datetime import datetime
from pathlib import Path

from lxml import etree
import regex

from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.logging import get_logger
from dsp_tools.utils.xml_upload import parse_xml_file


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


def _replace_ids_by_iris(
    tree: etree._Element,
    mapping: dict[str, str],
) -> tuple[etree._Element, bool]:
    """
    Iterate over the <resptr> tags and the salsah-links of the <text> tags,
    and replace the internal IDs by IRIs.
    If an internal ID cannot be found in the mapping, the original ID is kept.

    Args:
        tree: parsed XML file
        mapping: mapping of internal IDs to IRIs

    Returns:
        modified XML tree
    """
    success = True
    used_mapping_entries = set()

    resptr_elems = tree.xpath("/knora/resource/resptr-prop/resptr")
    resptr_elems_replaced = 0
    for resptr_elem in resptr_elems:
        value_before = resptr_elem.text
        if value_after := mapping.get(value_before):
            resptr_elem.text = value_after
            resptr_elems_replaced += 1
            used_mapping_entries.add(value_before)

    salsah_links = [
        x for x in tree.xpath("/knora/resource/text-prop/text//a") if x.attrib.get("class") == "salsah-link"
    ]
    salsah_links_replaced = 0
    for salsah_link in salsah_links:
        value_before = regex.sub("IRI:|:IRI", "", salsah_link.attrib.get("href", ""))
        if value_after := mapping.get(value_before):
            salsah_link.attrib["href"] = value_after
            salsah_links_replaced += 1
            used_mapping_entries.add(value_before)

    msg = (
        f"Replaced {resptr_elems_replaced}/{len(resptr_elems)} resptr links "
        f"and {salsah_links_replaced}/{len(salsah_links)} salsah-links in the XML file. "
        f"Used {len(used_mapping_entries)}/{len(mapping)} entries from the mapping file."
    )
    logger.info(msg)
    print(msg)

    return tree, success


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
    out_file = orig_xml_file.stem + "_replaced_" + timestamp_str + ".xml"
    et = etree.ElementTree(tree)
    et.write(out_file, pretty_print=True, xml_declaration=True, encoding="utf-8")
    logger.info(f"XML with replaced IDs was written to file {out_file}.")
    print(f"XML with replaced IDs was written to file {out_file}.")


def id_to_iri(
    xml_file: str,
    json_file: str,
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

    Raises:
        BaseError: if one of the two input files is not a valid file

    Returns:
        True if everything went well, False otherwise
    """
    xml_file_as_path, json_file_as_path = _check_input_parameters(xml_file=xml_file, json_file=json_file)
    mapping = _parse_json_file(json_file_as_path)
    tree = parse_xml_file(xml_file_as_path)
    tree, success = _replace_ids_by_iris(
        tree=tree,
        mapping=mapping,
    )
    _write_output_file(orig_xml_file=xml_file_as_path, tree=tree)
    return success
