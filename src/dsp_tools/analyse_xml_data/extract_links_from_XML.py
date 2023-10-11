import regex
from lxml import etree


def _extract_id_one_text_prop(text_prop: etree._Element) -> list[str]:
    # the same ID is in several separate <text-props> are considered separate links
    all_links = []
    for text in text_prop.getchildren():
        all_links.extend(_extract_id_one_text(text))
    return all_links


def _extract_id_one_text(text: etree._Element) -> list[str]:
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
