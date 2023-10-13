from itertools import chain

import regex
from lxml import etree

from dsp_tools.analyse_xml_data.models_xml_to_graph import ResptrLink, TripleGraph, XMLLink


def create_classes_from_root(root: etree._Element) -> list[ResptrLink] and list[XMLLink] and set[str]:
    resptr_instances = []
    xml_instances = []
    all_link_ids = []
    for resource in root.iter(tag="{https://dasch.swiss/schema}resource"):
        resptr, xml, all_links = _create_classes_single_resource(resource)
        if resptr:
            resptr_instances.extend(resptr)
        if xml:
            xml_instances.extend(xml)
        if all_link_ids:
            all_link_ids.extend(all_links)
    return resptr_instances, xml_instances, set(all_link_ids)


def _create_classes_single_resource(
    resource: etree._Element,
) -> list[ResptrLink] | None and list[XMLLink] | None and list[str] | None:
    subject_id = resource.attrib.get("id")
    all_used_ids = []
    resptr_links, xml_links = _get_all_links_one_resource(resource)
    if resptr_links:
        all_used_ids.extend(resptr_links)
        weight_dict = _make_weighted_resptr_links(resptr_links)
        resptr_links = [ResptrLink(subject_id=subject_id, object_id=k, edge_weight=v) for k, v in weight_dict.items()]
    if xml_links:
        all_used_ids.extend(chain.from_iterable(xml_links))
        xml_links = [XMLLink(subject_id=subject_id, object_link_ids=x) for x in xml_links]
    return resptr_links, xml_links, all_used_ids


def _make_weighted_resptr_links(resptr_links: list[str]) -> dict[str, int]:
    weight_dict = {link: 0 for link in set(resptr_links)}
    for link in resptr_links:
        weight_dict[link] += 1
    return weight_dict


def _get_all_links_one_resource(resource: etree._Element) -> list[str] | None and list[set[str]] | None:
    resptr_links = []
    xml_links = []
    for prop in resource.getchildren():
        match prop.tag:
            case "{https://dasch.swiss/schema}resptr-prop":
                links = _extract_id_one_resptr_prop(prop)
                match links:
                    case list():
                        resptr_links.extend(links)
                    case None:
                        continue
            case "{https://dasch.swiss/schema}text-prop":
                links = _extract_id_one_text_prop(prop)
                match links:
                    case list():
                        xml_links.extend(links)
                    case None:
                        continue
    if len(resptr_links) == 0:
        resptr_links = None
    if len(xml_links) == 0:
        xml_links = None
    return resptr_links, xml_links


def _extract_id_one_resptr_prop(resptr_prop: etree._Element) -> list[str]:
    return [x.text for x in resptr_prop.getchildren()]


def _extract_id_one_text_prop(text_prop: etree._Element) -> list[set[str]] | None:
    # the same ID is in several separate <text> in one <text-prop> are considered separate links
    xml_props = []
    for text in text_prop.getchildren():
        links = _extract_id_one_text(text)
        match links:
            case set():
                xml_props.append(links)
            case None:
                continue
    if len(xml_props) == 0:
        return None
    else:
        return xml_props


def _extract_id_one_text(text: etree._Element) -> set[str] | None:
    # the same id in one <text> only means one link to the resource
    all_links = set()
    for ele in text.iterdescendants():
        if href := ele.attrib.get("href"):
            searched = regex.search(r"IRI:(.*):IRI", href)
            match searched:
                case regex.Match():
                    all_links.add(searched.group(1))
                case None:
                    continue
    if len(all_links) == 0:
        return None
    else:
        return all_links
