from collections.abc import Callable

from dsp_tools.commands.mapping.models import ParsedMapping
from dsp_tools.commands.mapping.models import ParsedMappings
from dsp_tools.commands.mapping.models import PrefixResolutionProblem
from dsp_tools.commands.mapping.models import ResolvedClassMapping
from dsp_tools.commands.mapping.models import ResolvedMapping
from dsp_tools.commands.mapping.models import ResolvedMappings
from dsp_tools.commands.mapping.models import ResolvedPropertyMapping
from dsp_tools.utils.data_formats.uri_util import is_uri


def resolve_parsed_mappings(
    parsed_mappings: ParsedMappings, prefix_lookup: dict[str, str], ontology_namespace: str
) -> tuple[ResolvedMappings, list[PrefixResolutionProblem]]:
    all_problems: list[PrefixResolutionProblem] = []

    resolved_classes: list[ResolvedClassMapping] = []
    for cls in parsed_mappings.classes:
        resolved_cls, cls_problems = _resolve_one_mapping(cls, prefix_lookup, ontology_namespace, ResolvedClassMapping)
        resolved_classes.append(resolved_cls)
        all_problems.extend(cls_problems)

    resolved_properties: list[ResolvedPropertyMapping] = []
    for prop in parsed_mappings.properties:
        resolved_prop, prop_problems = _resolve_one_mapping(
            prop, prefix_lookup, ontology_namespace, ResolvedPropertyMapping
        )
        resolved_properties.append(resolved_prop)
        all_problems.extend(prop_problems)

    return ResolvedMappings(resolved_classes, resolved_properties), all_problems


def _resolve_one_mapping(
    parsed_mapping: ParsedMapping,
    prefix_lookup: dict[str, str],
    ontology_namespace: str,
    mapping_type: Callable[ResolvedMapping],
) -> tuple[ResolvedMapping, list[PrefixResolutionProblem]]:
    resolved: list[str] = []
    problems: list[PrefixResolutionProblem] = []
    for prefixed_iri in parsed_mapping.prefixed_mapping_iris:
        result = _resolve_prefixed_iri(prefixed_iri, prefix_lookup, parsed_mapping.name)
        if isinstance(result, PrefixResolutionProblem):
            problems.append(result)
        else:
            resolved.append(result)
    return mapping_type(f"{ontology_namespace}{parsed_mapping.name}", resolved), problems


def _resolve_prefixed_iri(
    prefixed_iri: str, prefix_lookup: dict[str, str], entity_name: str
) -> str | PrefixResolutionProblem:
    if is_uri(prefixed_iri):
        return prefixed_iri

    if ":" not in prefixed_iri:
        return PrefixResolutionProblem(
            entity_name=entity_name,
            input_value=prefixed_iri,
            problem="There is no prefix in the mapping value.",
        )

    prefix, local_name = prefixed_iri.split(":", 1)

    if not prefix:
        return PrefixResolutionProblem(
            entity_name=entity_name,
            input_value=prefixed_iri,
            problem="There is no prefix in the mapping value.",
        )
    if not local_name:
        return PrefixResolutionProblem(
            entity_name=entity_name,
            input_value=prefixed_iri,
            problem="The mapping value only contains a prefix.",
        )
    if prefix not in prefix_lookup:
        return PrefixResolutionProblem(
            entity_name=entity_name,
            input_value=prefixed_iri,
            problem="The prefix in the mapping value is not declared in the prefix sheet.",
        )
    return f"{prefix_lookup[prefix]}{local_name}"
