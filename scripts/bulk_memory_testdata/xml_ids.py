import copy
import re
from collections.abc import Mapping
from pathlib import PurePosixPath

from lxml import etree

RESOURCE_TAGS = {"resource", "link", "region", "video-segment", "audio-segment"}
_REFERENCE_TEXT_TAGS = {"resptr", "region-preview", "isSegmentOf", "relatesTo"}
_STANDOFF_REFERENCE = re.compile(r"IRI:([\w.\-]+):IRI")
_IIIF_IDENTIFIER = re.compile(r"/([^/]+?)(\.[^./]+)?(/full/)")


def localname(element: etree._Element) -> str:
    return etree.QName(element).localname


def is_element(node: etree._Element) -> bool:
    """Comments and processing instructions have a non-string tag."""
    return isinstance(node.tag, str)


def get_resources(root: etree._Element) -> list[etree._Element]:
    return [x for x in root if is_element(x) and localname(x) in RESOURCE_TAGS]


def copy_non_resource_children(root: etree._Element) -> list[etree._Element]:
    resources = set(get_resources(root))
    return [copy.deepcopy(x) for x in root if is_element(x) and x not in resources]


def get_references(resource: etree._Element) -> set[str]:
    """Returns every resource id or IRI that the resource references."""
    refs: set[str] = set()
    for element in resource.iter():
        if not is_element(element):
            continue
        if localname(element) in _REFERENCE_TEXT_TAGS and element.text:
            refs.add(element.text.strip())
        for value in element.attrib.values():
            refs.update(_STANDOFF_REFERENCE.findall(value))
    return {x for x in refs if not x.startswith("http")}


def rename_ids(
    root: etree._Element,
    resource_ids: Mapping[str, str],
    permission_ids: Mapping[str, str],
    authorship_ids: Mapping[str, str],
) -> None:
    """Renames ids and all references to them in place. Ids not in a mapping stay unchanged."""
    for element in root.iter():
        if not is_element(element):
            continue
        tag = localname(element)
        id_mapping = _get_id_mapping(tag, resource_ids, permission_ids, authorship_ids)
        for attr, value in element.attrib.items():
            if attr == "id":
                element.attrib[attr] = id_mapping.get(value, value)
            elif attr == "permissions":
                element.attrib[attr] = permission_ids.get(value, value)
            elif attr == "authorship-id":
                element.attrib[attr] = authorship_ids.get(value, value)
            else:
                element.attrib[attr] = _rename_standoff_references(value, resource_ids)
        if tag in _REFERENCE_TEXT_TAGS and element.text:
            ref = element.text.strip()
            element.text = resource_ids.get(ref, ref)


def _get_id_mapping(
    tag: str,
    resource_ids: Mapping[str, str],
    permission_ids: Mapping[str, str],
    authorship_ids: Mapping[str, str],
) -> Mapping[str, str]:
    if tag == "permissions":
        return permission_ids
    if tag == "authorship":
        return authorship_ids
    return resource_ids


def _rename_standoff_references(value: str, resource_ids: Mapping[str, str]) -> str:
    return _STANDOFF_REFERENCE.sub(lambda m: f"IRI:{resource_ids.get(m.group(1), m.group(1))}:IRI", value)


def make_files_unique(resource: etree._Element, suffix: str) -> None:
    """Adds the suffix to the file name of each bitstream and to the identifier of each IIIF URI."""
    for element in resource.iter():
        if not is_element(element) or not element.text or not element.text.strip():
            continue
        match localname(element):
            case "bitstream":
                path = PurePosixPath(element.text.strip())
                element.text = str(path.with_name(f"{path.stem}{suffix}{path.suffix}"))
            case "iiif-uri":
                uri = element.text.strip()
                element.text = _IIIF_IDENTIFIER.sub(
                    lambda m: f"/{m.group(1)}{suffix}{m.group(2) or ''}{m.group(3)}", uri, count=1
                )
