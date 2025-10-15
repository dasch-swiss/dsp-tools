from typing import Any

from dsp_tools.commands.create.models.input_problems import CollectedProblems
from dsp_tools.commands.create.models.input_problems import InputProblem
from dsp_tools.commands.create.models.parsed_ontology import Cardinality
from dsp_tools.commands.create.models.parsed_ontology import ParsedClass
from dsp_tools.commands.create.models.parsed_ontology import ParsedClassCardinalities
from dsp_tools.commands.create.models.parsed_ontology import ParsedOntology
from dsp_tools.commands.create.models.parsed_ontology import ParsedProperty
from dsp_tools.commands.create.models.parsed_ontology import ParsedPropertyCardinality

CARDINALITY_MAPPER = {
    "0-1": Cardinality.C_0_1,
    "1": Cardinality.C_1,
    "0-n": Cardinality.C_0_N,
    "1-n": Cardinality.C_1_N,
}


def parse_ontology(ontology_json: dict[str, Any], prefixes: dict[str, str]) -> ParsedOntology | CollectedProblems:
    pass


def _parse_properties(properties_json: dict[str, Any]) -> tuple[list[ParsedProperty], list[InputProblem]]:
    pass


def _parse_classes(classes_json: dict[str, Any]) -> tuple[list[ParsedClass], list[InputProblem]]:
    pass


def _parse_cardinalities(
    classes_json: dict[str, Any], current_onto_prefix: str, prefixes: dict[str, str]
) -> tuple[list[ParsedClassCardinalities], list[InputProblem]]:
    pass


def _parse_one_class_cardinality(
    cls_json: dict[str, Any], current_onto_prefix: str, prefixes: dict[str, str]
) -> ParsedClassCardinalities | list[InputProblem]:
    pass


def _parse_one_cardinality(
    card_json: dict[str, str], current_onto_prefix: str, prefixes: dict[str, str]
) -> ParsedPropertyCardinality | InputProblem:
    pass
