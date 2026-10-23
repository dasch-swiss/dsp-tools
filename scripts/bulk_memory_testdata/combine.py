import copy
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from scripts.bulk_memory_testdata.xml_ids import get_resources
from scripts.bulk_memory_testdata.xml_ids import is_element
from scripts.bulk_memory_testdata.xml_ids import localname
from scripts.bulk_memory_testdata.xml_ids import make_files_unique
from scripts.bulk_memory_testdata.xml_ids import rename_ids

_ONTOLOGY_ATTRIBUTES = ("restype", "name")


@dataclass(frozen=True)
class SourceFile:
    path: Path
    tag: str


def combine_xml_files(sources: list[SourceFile], shortcode: str, default_ontology: str) -> etree._Element:
    """
    Combines several XML data files of one project into one root.
    Each id gets the tag of its source file as prefix, so that ids from different files do not collide.
    Each file name gets the tag as suffix, so that files from different source files do not count as duplicates.
    """
    roots = [_prepare_source(src, default_ontology) for src in sources]
    combined = etree.Element(roots[0].tag, nsmap=roots[0].nsmap)
    combined.attrib["shortcode"] = shortcode
    combined.attrib["default-ontology"] = default_ontology
    for kind in ("permissions", "authorship"):
        for root in roots:
            combined.extend(x for x in root if is_element(x) and localname(x) == kind)
    for root in roots:
        combined.extend(get_resources(root))
    return combined


def _prepare_source(source: SourceFile, default_ontology: str) -> etree._Element:
    root = copy.deepcopy(etree.parse(source.path).getroot())
    rename_ids(
        root,
        resource_ids=_prefix_map(get_resources(root), source.tag),
        permission_ids=_prefix_map(_children(root, "permissions"), source.tag),
        authorship_ids=_prefix_map(_children(root, "authorship"), source.tag),
    )
    for res in get_resources(root):
        make_files_unique(res, f"_{source.tag}")
    source_ontology = root.attrib["default-ontology"]
    if source_ontology != default_ontology:
        _qualify_default_prefix(root, source_ontology)
    return root


def _children(root: etree._Element, tag: str) -> list[etree._Element]:
    return [x for x in root if is_element(x) and localname(x) == tag]


def _prefix_map(elements: list[etree._Element], tag: str) -> dict[str, str]:
    return {x.attrib["id"]: f"{tag}__{x.attrib['id']}" for x in elements}


def _qualify_default_prefix(root: etree._Element, ontology: str) -> None:
    for element in root.iter():
        if not is_element(element):
            continue
        for attr in _ONTOLOGY_ATTRIBUTES:
            value = element.attrib.get(attr)
            if value and value.startswith(":"):
                element.attrib[attr] = f"{ontology}{value}"
