import random
from collections import Counter
from dataclasses import dataclass
from dataclasses import field
from itertools import cycle

from lxml import etree

from scripts.bulk_memory_testdata.multiply import copy_resources
from scripts.bulk_memory_testdata.multiply import make_copies
from scripts.bulk_memory_testdata.xml_ids import copy_non_resource_children
from scripts.bulk_memory_testdata.xml_ids import get_references
from scripts.bulk_memory_testdata.xml_ids import get_resources

_SEED = 20261023


@dataclass
class MixStats:
    total_resources: int
    violating_resources: int = 0
    helper_resources: int = 0
    correct_resources: int = 0
    error_units_by_type: Counter[str] = field(default_factory=Counter)
    expected_results_by_type: Counter[str] = field(default_factory=Counter)


def mix_resources(
    correct_root: etree._Element,
    failing_root: etree._Element,
    problem_types: dict[str, list[str]],
    target_count: int,
    error_rate: float = 0.2,
) -> tuple[etree._Element, MixStats]:
    """
    Mixes correct and failing resources so that error_rate of all resources violate a shape.

    An error unit is one violating resource plus the resources it references (its helpers).
    The units go round-robin over the problem types, so each type gets the same number of units.
    Inside one type, the units go round-robin over its resources.
    Helpers that also violate count as violating resources.

    Raises:
        ValueError: if target_count is too small for one unit of each problem type
    """
    failing = {x.attrib["id"]: x for x in get_resources(failing_root)}
    budget = round(target_count * error_rate)
    if budget < len(_group_by_main_type(problem_types)):
        raise ValueError(f"{target_count} resources are too few for one error of each problem type")
    stats = MixStats(total_resources=target_count)
    units = _make_error_units(failing, problem_types, budget, stats)
    stats.correct_resources = target_count - stats.violating_resources - stats.helper_resources
    if stats.correct_resources < 0:
        raise ValueError(f"{target_count} resources are too few for the error units")
    blocks = [[x] for x in make_copies(get_resources(correct_root), stats.correct_resources, "c")] + units
    random.Random(_SEED).shuffle(blocks)  # noqa: S311 (test data, not cryptography)
    mixed = etree.Element(correct_root.tag, attrib=dict(correct_root.attrib), nsmap=correct_root.nsmap)
    mixed.extend(copy_non_resource_children(correct_root))
    mixed.extend(copy_non_resource_children(failing_root))
    mixed.extend(res for block in blocks for res in block)
    return mixed, stats


def _make_error_units(
    failing: dict[str, etree._Element],
    problem_types: dict[str, list[str]],
    budget: int,
    stats: MixStats,
) -> list[list[etree._Element]]:
    by_type = _group_by_main_type(problem_types)
    resource_cycles = {problem: cycle(res_ids) for problem, res_ids in by_type.items()}
    units: list[list[etree._Element]] = []
    for problem in cycle(sorted(by_type)):
        if stats.violating_resources >= budget:
            break
        res_id = next(resource_cycles[problem])
        unit_ids = [res_id, *sorted(_helper_ids(res_id, failing))]
        units.append(copy_resources([failing[x] for x in unit_ids], f"__e{len(units):06d}"))
        _count_unit(unit_ids, problem, problem_types, stats)
    return units


def _group_by_main_type(problem_types: dict[str, list[str]]) -> dict[str, list[str]]:
    by_type: dict[str, list[str]] = {}
    for res_id, problems in sorted(problem_types.items()):
        main_type = Counter(problems).most_common(1)[0][0]
        by_type.setdefault(main_type, []).append(res_id)
    return by_type


def _helper_ids(res_id: str, failing: dict[str, etree._Element]) -> set[str]:
    helpers: set[str] = set()
    to_visit = [res_id]
    while to_visit:
        refs = get_references(failing[to_visit.pop()]) & failing.keys()
        new = refs - helpers - {res_id}
        helpers |= new
        to_visit.extend(new)
    return helpers


def _count_unit(unit_ids: list[str], problem: str, problem_types: dict[str, list[str]], stats: MixStats) -> None:
    for unit_id in unit_ids:
        if unit_id in problem_types:
            stats.violating_resources += 1
            stats.expected_results_by_type.update(problem_types[unit_id])
        else:
            stats.helper_resources += 1
    stats.error_units_by_type[problem] += 1
