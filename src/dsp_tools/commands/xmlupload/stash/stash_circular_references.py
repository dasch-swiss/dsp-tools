from __future__ import annotations

from typing import cast
from uuid import uuid4

from lxml import etree

from dsp_tools.commands.xmlupload.models.deserialise.deserialise_value import XMLProperty
from dsp_tools.commands.xmlupload.models.deserialise.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import create_info_from_xml_for_graph
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import generate_upload_order
from dsp_tools.commands.xmlupload.stash.construct_and_analyze_graph import make_graph
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStash
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStash
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash


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
        standoff_xml = cast(FormattedTextValue, value.value)
        uuid = str(uuid4())
        standoff_stash_item = StandoffStashItem(
            res_id=res_id,
            res_type=restype,
            uuid=uuid,
            prop_name=link_prop.name,
            value=standoff_xml,
        )
        value.value = FormattedTextValue(uuid)
        stashed_items.append(standoff_stash_item)
    return stashed_items


def _stash_resptr(
    res_id: str,
    restype: str,
    link_prop: XMLProperty,
    stash_lookup: dict[str, list[str]],
    permission_lookup: dict[str, Permissions],
) -> list[LinkValueStashItem]:
    stashed_items = []
    for value in link_prop.values.copy():
        if value.link_uuid not in stash_lookup[res_id]:
            continue
        permission = str(permission_lookup[value.permissions]) if value.permissions else None
        # value.value is the ID of the target resource. stash it, then delete it
        link_stash_item = LinkValueStashItem(
            res_id=res_id,
            res_type=restype,
            prop_name=link_prop.name,
            target_id=str(value.value),
            permission=permission,
        )
        link_prop.values.remove(value)
        stashed_items.append(link_stash_item)
    return stashed_items


def stash_circular_references(
    resources: list[XMLResource],
    stash_lookup: dict[str, list[str]],
    permission_lookup: dict[str, Permissions],
) -> Stash | None:
    """
    Stashes problematic resource-references from a list of resources.
    The resources are modified in-place.

    Args:
        resources: all resources of the XML file
        stash_lookup: A dictionary which maps the resources that have stashes to the UUIDs of the stashed links
        permission_lookup: A dictionary which maps the permissions of the stashed links to their string representation

    Returns:
        stash: an object that contains the stashed references

    Raises:
        ValueError: If a link property of one of the resources is not "text" or "resptr"
    """
    stashed_standoff_values: list[StandoffStashItem] = []
    stashed_link_values: list[LinkValueStashItem] = []

    for res in resources:
        if res.res_id not in stash_lookup:
            continue
        for link_prop in res.get_props_with_links():
            if link_prop.valtype == "text":
                standoff_stash_item = _stash_standoff(res.res_id, res.restype, link_prop, stash_lookup)
                stashed_standoff_values.extend(standoff_stash_item)
            elif link_prop.valtype == "resptr":
                link_stash_item = _stash_resptr(res.res_id, res.restype, link_prop, stash_lookup, permission_lookup)
                stashed_link_values.extend(link_stash_item)
            else:
                raise ValueError(f"Unknown value type: '{link_prop.valtype}' (should be 'text' or 'resptr')")

            if len(link_prop.values) == 0:
                # if all values of a link property have been stashed, the property needs to be removed
                res.properties.remove(link_prop)

    standoff_stash = StandoffStash.make(stashed_standoff_values)
    link_value_stash = LinkValueStash.make(stashed_link_values)
    return Stash.make(standoff_stash, link_value_stash)


def identify_circular_references(root: etree._Element) -> tuple[dict[str, list[str]], list[str]]:
    """
    Identifies problematic resource-references inside an XML tree.
    A reference is problematic if it creates a circle (circular references).
    The XML tree is modified in-place:
    A reference UUID is added to each XML element that contains a link (`<resptr>` or `<text>`).

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
