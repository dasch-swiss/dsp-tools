import regex
from lxml import etree


def _extract_links_one_text_prop(text_prop: etree._Element) -> list[str]:
    all_links = set()
    for child in text_prop.iterdescendants():
        if href := child.attrib.get("href"):
            searched = regex.findall(r"IRI:(.*):IRI", href)[0]
            match type(searched):
                case str:
                    all_links.add(searched)
    return list(all_links)
