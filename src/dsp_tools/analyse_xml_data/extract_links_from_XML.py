from typing import Any

import regex
from lxml import etree


def _get_links_all_resources_from_root(root: etree._Element) -> dict[str : list[Any]]:
    resource_links = dict()
    for resource in root.iter(tag="{https://dasch.swiss/schema}resource"):
        resource_links[resource.attrib["id"]] = _get_all_links_one_resource(resource)
    return resource_links


def _get_all_links_one_resource(resource: etree._Element) -> list[Any]:
    id_list = []
    for prop in resource.getchildren():
        match prop.tag:
            case "{https://dasch.swiss/schema}text-prop":
                id_list.extend(_extract_id_one_text_prop(prop))
            case "{https://dasch.swiss/schema}resptr-prop":
                id_list.extend(_extract_id_one_resptr_prop(prop))
    return id_list


def _extract_id_one_text_prop(text_prop: etree._Element) -> list[Any]:
    # the same ID is in several separate <text-props> are considered separate links
    all_links = []
    for text in text_prop.getchildren():
        all_links.extend(_extract_id_one_text(text))
    return all_links


def _extract_id_one_text(text: etree._Element) -> list[Any]:
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
    return list(all_links)


def _extract_id_one_resptr_prop(resptr_prop: etree._Element) -> list[Any]:
    return [x.text for x in resptr_prop.getchildren()]
