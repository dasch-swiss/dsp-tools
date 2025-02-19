from __future__ import annotations

from lxml import etree

from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource


def extract_resources_from_xml(root: etree._Element, default_ontology: str) -> list[XMLResource]:
    """
    Takes the XML root and parses it into the XMLResource class

    Args:
        root: XML root
        default_ontology: default ontology

    Returns:
        list of resources with values
    """
    resources = list(root.iter(tag="resource"))
    return [XMLResource.from_node(res, default_ontology) for res in resources]
