from typing import Any

import regex
from lxml import etree


def get_links_all_resources_from_root(root: etree._Element) -> dict[str, list[str]]:
    """
    This function takes the root of an XML file an extracts all the links from the resources.
    It returns a dictionary with the resources that contain links as keys
    And a list of the target resources as keys.
    If a resource does not have any targets links it is not in the dictionary

    Args:
        root: root of an xml

    Returns:
        Dictionary with resource ids as key and a list with links as value
    """
    resource_links = dict()
    for resource in root.iter(tag="{https://dasch.swiss/schema}resource"):
        links = _get_all_links_one_resource(resource)
        match links:
            case list():
                resource_links[resource.attrib["id"]] = links
            case None:
                continue
    return resource_links


def _get_all_links_one_resource(resource: etree._Element) -> list[str] | None:
    id_list = []
    for prop in resource.getchildren():
        match prop.tag:
            case "{https://dasch.swiss/schema}text-prop":
                id_list.extend(_extract_id_one_text_prop(prop))
            case "{https://dasch.swiss/schema}resptr-prop":
                id_list.extend(_extract_id_one_resptr_prop(prop))
    match len(id_list):
        case 0:
            return None
        case _:
            return id_list


def _extract_id_one_text_prop(text_prop: etree._Element) -> list[Any]:
    # the same ID is in several separate <text> in one <text-prop> are considered separate links
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


def _extract_id_one_resptr_prop(resptr_prop: etree._Element) -> list[str]:
    return [x.text for x in resptr_prop.getchildren()]


def _extract_weighted_id_one_resource(resource: etree._Element) -> dict[str, int | float] | None:
    id_list: list[dict[str, int | float]] = []
    for prop in resource.getchildren():
        match prop.tag:
            case "{https://dasch.swiss/schema}text-prop":
                id_list.extend(_extract_weighted_id_one_text_prop(prop))
            case "{https://dasch.swiss/schema}resptr-prop":
                resptr_links = _extract_id_one_resptr_prop(prop)
                # TODO change tuple
                resptr_links = [tuple(x, 1) for x in resptr_links]
                id_list.extend(resptr_links)
    if len(id_list) == 0:
        return None
    else:
        # TODO: count
        return id_list


def _extract_weighted_id_one_text_prop(text_prop: etree._Element) -> list[dict[str, int | float]]:
    # the same ID is in several separate <text> in one <text-prop> are considered separate links
    all_links = []
    for text in text_prop.getchildren():
        all_links.append(_extract_weighted_text_id(text))
    return all_links


def _extract_weighted_text_id(text: etree._Element) -> dict[str, int | float]:
    ids = _extract_id_one_text(text)
    weight = 1 / len(ids)
    return {_id: weight for _id in ids}
