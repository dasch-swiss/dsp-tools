from __future__ import annotations

from typing import cast
from uuid import uuid4

from lxml import etree

from dsp_tools.analyse_xml_data.construct_and_analyze_graph import (
    create_info_from_xml_for_graph,
    generate_upload_order,
    make_graph,
)
from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.xmlupload.stash.stash_models import (
    LinkValueStash,
    LinkValueStashItem,
    StandoffStash,
    StandoffStashItem,
    Stash,
)

logger = get_logger(__name__)


def stash_circular_references(
    resources: list[XMLResource],
    stash_lookup: dict[str, list[str]],
) -> Stash | None:
    """
    Stashes problematic resource-references from a list of resources.
    The resources are modified in-place.

    Args:
        resources: all resources of the XML file
        stash_lookup: A dictionary which maps the resources that have stashes to the UUIDs of the stashed links

    Returns:
        stash: an object that contains the stashed references
    """
    stashed_standoff_values: list[StandoffStashItem] = []
    stashed_link_values: list[LinkValueStashItem] = []

    for res in resources.copy():
        if not res.id in stash_lookup:
            continue
        for link_prop in res.get_props_with_links():
            if link_prop.valtype == "text":
                for value in link_prop.values:
                    if not value.link_uuid in stash_lookup[res.id]:
                        continue
                    # value.value is a KnoraStandoffXml text with problematic links.
                    # stash it, then replace the problematic text with a UUID
                    standoff_xml = cast(KnoraStandoffXml, value.value)
                    uuid = str(uuid4())
                    standoff_stash_item = StandoffStashItem(
                        res_id=res.id,
                        res_type=res.restype,
                        uuid=uuid,
                        prop_name=link_prop.name,
                        value=standoff_xml,
                    )
                    stashed_standoff_values.append(standoff_stash_item)
                    value.value = KnoraStandoffXml(uuid)
            elif link_prop.valtype == "resptr":
                for value in link_prop.values.copy():
                    if not value.link_uuid in stash_lookup[res.id]:
                        continue
                    # value.value is the ID of the target resource. stash it, then delete it
                    link_stash_item = LinkValueStashItem(
                        res_id=res.id,
                        res_type=res.restype,
                        prop_name=link_prop.name,
                        target_id=str(value.value),
                    )
                    stashed_link_values.append(link_stash_item)
                    link_prop.values.remove(value)

            if len(link_prop.values) == 0:
                # if all values of a link property have been stashed, the property needs to be removed
                res.properties.remove(link_prop)

    standoff_stash = StandoffStash.make(stashed_standoff_values)
    link_value_stash = LinkValueStash.make(stashed_link_values)
    stash = Stash.make(standoff_stash, link_value_stash)

    return stash


def identify_circular_references(
    root: etree._Element,
    verbose: bool,
) -> tuple[dict[str, list[str]], list[str]]:
    """
    Identifies problematic resource-references inside an XML tree.
    A reference is problematic if it creates a circle (circular references).
    The XML tree is modified in-place:
    A reference UUID is added to each XML element that contains a link (<resptr> or <text>).

    Args:
        root: the root element of the parsed XML document
        verbose: verbose output if True

    Returns:
        stash_lookup: A dictionary which maps the resources that have stashes to the UUIDs of the stashed links
        upload_order: A list of resource IDs in the order in which they should be uploaded
    """
    logger.info("Checking resources for circular references...")
    if verbose:
        print("Checking resources for circular references...")
    resptr_links, xml_links, all_resource_ids = create_info_from_xml_for_graph(root)
    graph, node_to_id, edges = make_graph(resptr_links, xml_links, all_resource_ids)
    stash_lookup, upload_order, _ = generate_upload_order(graph, node_to_id, edges)
    return stash_lookup, upload_order
