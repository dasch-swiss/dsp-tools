import re

from dsp_tools.commands.mapping.models import ClassMapping
from dsp_tools.commands.mapping.models import ParsedMappingExcel
from dsp_tools.commands.mapping.models import PrefixResolutionProblem
from dsp_tools.commands.mapping.models import PropertyMapping

_FULL_IRI_RE = re.compile(r"^https?://")


def resolve_all(
    excel: ParsedMappingExcel, prefix_map: dict[str, str]
) -> tuple[ParsedMappingExcel, list[PrefixResolutionProblem]]:
    problems: list[PrefixResolutionProblem] = []
    resolved_classes: list[ClassMapping] = []
    resolved_properties: list[PropertyMapping] = []

    for cm in excel.classes:
        resolved_iris, new_problems = _resolve_list(
            values=cm.mapping_iris,
            prefix_map=prefix_map,
            entity_label=f"class '{cm.class_iri}'",
        )
        problems.extend(new_problems)
        resolved_classes.append(ClassMapping(class_iri=cm.class_iri, mapping_iris=resolved_iris))

    for pm in excel.properties:
        resolved_iris, new_problems = _resolve_list(
            values=pm.mapping_iris,
            prefix_map=prefix_map,
            entity_label=f"property '{pm.property_iri}'",
        )
        problems.extend(new_problems)
        resolved_properties.append(PropertyMapping(property_iri=pm.property_iri, mapping_iris=resolved_iris))

    return ParsedMappingExcel(classes=resolved_classes, properties=resolved_properties), problems


def _resolve_list(
    values: list[str], prefix_map: dict[str, str], entity_label: str
) -> tuple[list[str], list[PrefixResolutionProblem]]:
    resolved: list[str] = []
    problems: list[PrefixResolutionProblem] = []
    for value in values:
        result = _resolve_single(value, prefix_map, entity_label)
        if isinstance(result, PrefixResolutionProblem):
            problems.append(result)
        else:
            resolved.append(result)
    return resolved, problems


def _resolve_single(value: str, prefix_map: dict[str, str], entity_label: str) -> str | PrefixResolutionProblem:
    if _FULL_IRI_RE.match(value):
        return value

    if ":" not in value:
        return PrefixResolutionProblem(
            entity=f"{entity_label}, mapping value '{value}'",
            raw_value=value,
            prefix="",
        )

    prefix, local_name = value.split(":", 1)

    if not prefix:
        return PrefixResolutionProblem(
            entity=f"{entity_label}, mapping value '{value}'",
            raw_value=value,
            prefix="",
        )

    if not local_name:
        return PrefixResolutionProblem(
            entity=f"{entity_label}, mapping value '{value}'",
            raw_value=value,
            prefix=prefix,
        )

    if prefix not in prefix_map:
        return PrefixResolutionProblem(
            entity=f"{entity_label}, mapping value '{value}'",
            raw_value=value,
            prefix=prefix,
        )

    return f"{prefix_map[prefix]}{local_name}"
