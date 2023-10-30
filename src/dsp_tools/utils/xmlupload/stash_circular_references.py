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
from dsp_tools.models.xmlproperty import XMLProperty
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


def _stash_standoff(
    res_id: str,
    restype: str,
    link_prop: XMLProperty,
    stash_lookup: dict[str, list[str]],
) -> list[StandoffStashItem]:
    stashed_items = []
    for value in link_prop.values:
        if value.link_uuid not in stash_lookup[res_id]:
            continue
        # value.value is a KnoraStandoffXml text with problematic links.
        # stash it, then replace the problematic text with a UUID
        standoff_xml = cast(KnoraStandoffXml, value.value)
        uuid = str(uuid4())
        standoff_stash_item = StandoffStashItem(
            res_id=res_id,
            res_type=restype,
            uuid=uuid,
            prop_name=link_prop.name,
            value=standoff_xml,
        )
        value.value = KnoraStandoffXml(uuid)
        stashed_items.append(standoff_stash_item)
    return stashed_items


def _stash_resptr(
    res_id: str,
    restype: str,
    link_prop: XMLProperty,
    stash_lookup: dict[str, list[str]],
) -> list[LinkValueStashItem]:
    stashed_items = []
    for value in link_prop.values.copy():
        if value.link_uuid not in stash_lookup[res_id]:
            continue
        # value.value is the ID of the target resource. stash it, then delete it
        link_stash_item = LinkValueStashItem(
            res_id=res_id,
            res_type=restype,
            prop_name=link_prop.name,
            target_id=str(value.value),
        )
        link_prop.values.remove(value)
        stashed_items.append(link_stash_item)
    return stashed_items


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

    for res in resources:
        if not res.id in stash_lookup:
            continue
        for link_prop in res.get_props_with_links():
            assert link_prop.valtype in ["text", "resptr"]
            if link_prop.valtype == "text":
                standoff_stash_item = _stash_standoff(res.id, res.restype, link_prop, stash_lookup)
                stashed_standoff_values.extend(standoff_stash_item)
            elif link_prop.valtype == "resptr":
                link_stash_item = _stash_resptr(res.id, res.restype, link_prop, stash_lookup)
                stashed_link_values.extend(link_stash_item)

            if len(link_prop.values) == 0:
                # if all values of a link property have been stashed, the property needs to be removed
                res.properties.remove(link_prop)

    standoff_stash = StandoffStash.make(stashed_standoff_values)
    link_value_stash = LinkValueStash.make(stashed_link_values)
    stash = Stash.make(standoff_stash, link_value_stash)

    return stash


def identify_circular_references(root: etree._Element) -> tuple[dict[str, list[str]], list[str]]:
    """
    Identifies problematic resource-references inside an XML tree.
    A reference is problematic if it creates a circle (circular references).
    The XML tree is modified in-place:
    A reference UUID is added to each XML element that contains a link (<resptr> or <text>).

    Args:
        root: the root element of the parsed XML document

    Returns:
        stash_lookup: A dictionary which maps the resources that have stashes to the UUIDs of the stashed links
        upload_order: A list of resource IDs in the order in which they should be uploaded
    """
    resptr_links, xml_links, all_resource_ids = create_info_from_xml_for_graph(root)
    graph, node_to_id, edges = make_graph(resptr_links, xml_links, all_resource_ids)
    stash_lookup, upload_order, _ = generate_upload_order(graph, node_to_id, edges)
    return stash_lookup, upload_order
