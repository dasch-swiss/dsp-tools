import copy
import math
from collections.abc import Mapping

from lxml import etree

from scripts.bulk_memory_testdata.xml_ids import copy_non_resource_children
from scripts.bulk_memory_testdata.xml_ids import get_resources
from scripts.bulk_memory_testdata.xml_ids import make_files_unique
from scripts.bulk_memory_testdata.xml_ids import rename_ids


def multiply_resources(root: etree._Element, target_count: int) -> etree._Element:
    """Repeats the resources of the root until it has exactly target_count resources."""
    multiplied = etree.Element(root.tag, attrib=dict(root.attrib), nsmap=root.nsmap)
    multiplied.extend(copy_non_resource_children(root))
    multiplied.extend(make_copies(get_resources(root), target_count, "c"))
    return multiplied


def make_copies(resources: list[etree._Element], target_count: int, marker: str) -> list[etree._Element]:
    """
    Copy n gets the id suffix __{marker}{n}. Each base resource occurs floor or ceil times.
    References inside a full copy point to the same copy.
    The last copy is incomplete: its references to left-out resources point to the first copy.

    Raises:
        ValueError: if target_count is smaller than the number of base resources
    """
    if target_count < len(resources):
        raise ValueError(f"The target count must be at least the number of base resources ({len(resources)})")
    first_copy = _suffix_mapping(resources, f"__{marker}{0:06d}")
    copies: list[etree._Element] = []
    for number in range(math.ceil(target_count / len(resources))):
        included = resources[: target_count - len(copies)]
        suffix = f"__{marker}{number:06d}"
        copies.extend(copy_resources(included, suffix, fallback_ids=first_copy))
    return copies


def copy_resources(
    resources: list[etree._Element], suffix: str, fallback_ids: Mapping[str, str] | None = None
) -> list[etree._Element]:
    """References to ids outside the resources go to fallback_ids, if given."""
    id_mapping = {**(fallback_ids or {}), **_suffix_mapping(resources, suffix)}
    copies = [copy.deepcopy(x) for x in resources]
    for res in copies:
        rename_ids(res, id_mapping, {}, {})
        make_files_unique(res, suffix.replace("__", "_"))
    return copies


def _suffix_mapping(resources: list[etree._Element], suffix: str) -> dict[str, str]:
    return {x.attrib["id"]: f"{x.attrib['id']}{suffix}" for x in resources}
