from __future__ import annotations

import uuid
from typing import cast

import regex
from lxml import etree

from dsp_tools.commands.xmlupload.stash.graph_models import InfoForGraph
from dsp_tools.commands.xmlupload.stash.graph_models import LinkValueLink
from dsp_tools.commands.xmlupload.stash.graph_models import StandOffLink
from dsp_tools.utils.iri_util import is_resource_iri


def create_info_from_xml_for_graph(
    root: etree._Element,
) -> InfoForGraph:
    """
    Create link objects (ResptrLink/XMLLink) from the XML file,
    and add a reference UUID to each XML element that contains a link (<resptr> or <text>).
    With this UUID, the link objects can be identified in the XML data file.

    Args:
        root: root of the parsed XML file

    Returns:
        - All resptr links contained in the XML file, represented as ResptrLink objects.
        - All XML links contained in the XML file, represented as XMLLink objects.
        - A list with all resource IDs used in the XML file.
    """
    resptr_links = []
    xml_links = []
    all_resource_ids = []
    for resource in root.iter(tag="resource"):
        resptr, xml = _create_info_from_xml_for_graph_from_one_resource(resource)
        all_resource_ids.append(resource.attrib["id"])
        resptr_links.extend(resptr)
        xml_links.extend(xml)
    return InfoForGraph(all_resource_ids=all_resource_ids, link_values=resptr_links, standoff_links=xml_links)


def _create_info_from_xml_for_graph_from_one_resource(
    resource: etree._Element,
) -> tuple[list[LinkValueLink], list[StandOffLink]]:
    resptr_links: list[LinkValueLink] = []
    xml_links: list[StandOffLink] = []
    for prop in resource.getchildren():
        match prop.tag:
            case "resptr-prop":
                resptr_links.extend(_create_resptr_link_objects(resource.attrib["id"], prop))
            case "text-prop":
                xml_links.extend(_create_text_link_objects(resource.attrib["id"], prop))
            case "hasComment" | "hasDescription":
                if xml_link := _create_text_link_object_from_special_tags(resource.attrib["id"], prop):
                    xml_links.append(xml_link)
            case "isAudioSegmentOf" | "isVideoSegmentOf" | "relatesTo":
                if segment_link := _create_segmentOf_link_objects(resource.attrib["id"], prop):
                    resptr_links.append(segment_link)
    return resptr_links, xml_links


def _create_segmentOf_link_objects(subject_id: str, resptr: etree._Element) -> LinkValueLink | None:
    resptr.text = cast(str, resptr.text)
    if is_resource_iri(resptr.text):
        return None
    link_object = LinkValueLink(subject_id, resptr.text, str(uuid.uuid4()))
    # this UUID is so that the links that were stashed can be identified in the XML data file
    resptr.attrib["linkUUID"] = link_object.link_uuid
    return link_object


def _create_resptr_link_objects(subject_id: str, resptr_prop: etree._Element) -> list[LinkValueLink]:
    resptr_links = []
    for resptr in resptr_prop.getchildren():
        resptr.text = cast(str, resptr.text)
        if not is_resource_iri(resptr.text):
            link_object = LinkValueLink(subject_id, resptr.text, str(uuid.uuid4()))
            # this UUID is so that the links that were stashed can be identified in the XML data file
            resptr.attrib["linkUUID"] = link_object.link_uuid
            resptr_links.append(link_object)
    return resptr_links


def _create_text_link_objects(subject_id: str, text_prop: etree._Element) -> list[StandOffLink]:
    # if the same ID is in several separate <text> values of one <text-prop>, they are considered separate links
    xml_props = []
    for text in text_prop.getchildren():
        if links := _extract_ids_from_one_text_value(text):
            xml_link = StandOffLink(subject_id, links, str(uuid.uuid4()))
            xml_props.append(xml_link)
            # this UUID is so that the links that were stashed can be identified in the XML data file
            text.attrib["linkUUID"] = xml_link.link_uuid
    return xml_props


def _create_text_link_object_from_special_tags(subject_id: str, special_tag: etree._Element) -> StandOffLink | None:
    # This is for <hasDescription> and <hasComment> properties of <video-segment>s or <audio-segment>s
    if not (links := _extract_ids_from_one_text_value(special_tag)):
        return None
    xml_link = StandOffLink(subject_id, links, str(uuid.uuid4()))
    # this UUID is so that the links that were stashed can be identified in the XML data file
    special_tag.attrib["linkUUID"] = xml_link.link_uuid
    return xml_link


def _extract_ids_from_one_text_value(text: etree._Element) -> set[str]:
    # the same id in one <text> only means one link to the resource
    all_links = set()
    for ele in text.iterdescendants():
        if href := ele.attrib.get("href"):
            if internal_id := regex.search(r"IRI:(.*):IRI", href):
                all_links.add(internal_id.group(1))
    return all_links
