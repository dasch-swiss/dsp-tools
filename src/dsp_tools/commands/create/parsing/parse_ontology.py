from typing import Any

from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import InputProblem
from dsp_tools.commands.create.models.input_problems import ProblemType
from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import ParsedClass
from dsp_tools.commands.create.models.parsed_ontology import ParsedClassCardinalities
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality
from dsp_tools.commands.create.parsing.parsing_utils import resolve_prefixed_iri

CARDINALITY_MAPPER = {
    "0-1": Cardinality.C_0_1,
    "1": Cardinality.C_1,
    "0-n": Cardinality.C_0_N,
    "1-n": Cardinality.C_1_N,
}


def parse_ontology(ontology_json: dict[str, Any], prefixes: dict[str, str]) -> ParsedOntology | CollectedProblems:
    onto_name = ontology_json["name"]
    current_onto = prefixes[onto_name]
    fails = []
    props, prop_fails = _parse_properties(ontology_json["properties"], current_onto, prefixes)
    fails.extend(prop_fails)
    classes, cls_fail = _parse_classes(ontology_json["resources"], current_onto, prefixes)
    fails.extend(cls_fail)
    cards, card_fail = _parse_cardinalities(ontology_json["resources"], current_onto, prefixes)
    fails.extend(card_fail)
    if fails:
        return CollectedProblems(
            f"During the parsing of the ontology '{onto_name}' the following errors occurred:", fails
        )
    return ParsedOntology(
        name=onto_name,
        label=ontology_json["label"],
        comment=ontology_json["comment"],
        classes=classes,
        properties=props,
        cardinalities=cards,
    )


def _parse_properties(
    properties_list: list[dict[str, Any]], current_onto_prefix: str, prefixes: dict[str, str]
) -> tuple[list[ParsedProperty], list[InputProblem]]:
    parsed = []
    failures = []
    for prop in properties_list:
        if not (resolved := resolve_prefixed_iri(prop["name"], current_onto_prefix, prefixes)):
            failures.append(InputProblem(prop["name"], ProblemType.PREFIX_COULD_NOT_BE_RESOLVED))
        else:
            parsed.append(ParsedProperty(resolved, prop))
    return parsed, failures


def _parse_classes(
    classes_list: list[dict[str, Any]], current_onto_prefix: str, prefixes: dict[str, str]
) -> tuple[list[ParsedClass], list[InputProblem]]:
    parsed = []
    failures = []
    for cls in classes_list:
        if not (resolved := resolve_prefixed_iri(cls["name"], current_onto_prefix, prefixes)):
            failures.append(InputProblem(cls["name"], ProblemType.PREFIX_COULD_NOT_BE_RESOLVED))
        else:
            parsed.append(ParsedClass(resolved, cls))
    return parsed, failures


def _parse_cardinalities(
    classes_list: list[dict[str, str | int]], current_onto_prefix: str, prefixes: dict[str, str]
) -> tuple[list[ParsedClassCardinalities], list[InputProblem]]:
    parsed = []
    failures = []
    for c in classes_list:
        if c.get("cardinalities"):
            result = _parse_one_class_cardinality(c, current_onto_prefix, prefixes)
            if isinstance(result, ParsedClassCardinalities):
                parsed.append(result)
            else:
                failures.extend(result)
    return parsed, failures


def _parse_one_class_cardinality(
    cls_json: dict[str, str | int], current_onto_prefix: str, prefixes: dict[str, str]
) -> ParsedClassCardinalities | list[InputProblem]:
    failures = []
    parsed = []
    for c in cls_json["cardinalities"]:
        result = _parse_one_cardinality(c, current_onto_prefix, prefixes)
        if isinstance(result, ParsedPropertyCardinality):
            parsed.append(result)
        else:
            failures.append(result)
    if failures:
        return failures
    cls_iri = f"{current_onto_prefix}{cls_json['name']}"
    return ParsedClassCardinalities(cls_iri, parsed)


def _parse_one_cardinality(
    card_json: dict[str, str | int], current_onto_prefix: str, prefixes: dict[str, str]
) -> ParsedPropertyCardinality | InputProblem:
    if not (resolved := resolve_prefixed_iri(card_json["propname"], current_onto_prefix, prefixes)):
        return InputProblem(card_json["propname"], ProblemType.PREFIX_COULD_NOT_BE_RESOLVED)
    return ParsedPropertyCardinality(
        propname=resolved,
        cardinality=CARDINALITY_MAPPER[card_json["cardinality"]],
        gui_order=card_json.get("gui_order"),
    )
