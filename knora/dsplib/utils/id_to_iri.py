"""
This module handles the replacement of internal IDs with their corresponding IRIs from DSP.
"""
import json
import os
from datetime import datetime

from lxml import etree


def id_to_iri(xml_file: str, json_file: str) -> None:
    """
    This function replaces all occurrences of internal IDs with their respective IRIs inside an XML file. It gets the
    mapping from the JSON file provided as parameter for this function.

    Args:
        xml_file : the XML file with the data to be replaced
        json_file : the JSON file with the mapping (dict) of internal IDs to IRIs

    Returns:
        None
    """

    # check that provided files exist
    if not os.path.isfile(xml_file):
        print(f"File {xml_file} could not be found.")

    if not os.path.isfile(json_file):
        print(f"File {json_file} could not be found.")

    # load JSON from provided json file to dict
    with open(json_file) as f:
        mapping = json.load(f)

    # parse XML from provided xml file
    tree = etree.parse(xml_file)

    # iterate through all XML elements and remove namespace declarations
    for elem in tree.getiterator():
        # skip comments and processing instructions as they do not have namespaces
        if not (
            isinstance(elem, etree._Comment)
            or isinstance(elem, etree._ProcessingInstruction)
        ):
            # remove namespace declarations
            elem.tag = etree.QName(elem).localname

    resource_elements = tree.xpath("/knora/resource/resptr-prop/resptr")
    for resptr_prop in resource_elements:
        try:
            resptr_prop.text = mapping[resptr_prop.text]
        except KeyError:
            print(f"Could not find internal ID '{resptr_prop.text}' in mapping file {json_file}.")
            pass

    # write xml with replaced IDs to file with timestamp
    timestamp_now = datetime.now()
    timestamp_str = timestamp_now.strftime("%Y%m%d_%H%M%S%f")

    replaced_id_file = "id2iri_replaced_" + timestamp_str + ".xml"

    et = etree.ElementTree(tree.getroot())
    et.write(replaced_id_file, pretty_print=True)
    print(f"Created new XML file {replaced_id_file} with replaced IDs.")
