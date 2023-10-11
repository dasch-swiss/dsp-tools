import regex
from lxml import etree


def _extract_id_one_text_prop(text_prop: etree._Element) -> list[str]:
    all_links = set()
    for child in text_prop.iterdescendants():
        if href := child.attrib.get("href"):
            searched = regex.search(r"IRI:(.*):IRI", href)
            match searched:
                case regex.Match():
                    all_links.add(searched.group(1))
                case None:
                    continue
    return list(all_links)
