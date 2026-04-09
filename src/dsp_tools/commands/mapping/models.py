from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from dsp_tools.cli.args import ServerCredentials


@dataclass
class MappingConfig:
    shortcode: str
    ontology: str
    excel_file: Path


@dataclass
class MappingInfo:
    config: MappingConfig
    server: ServerCredentials


@dataclass
class ParsedMapping:
    name: str
    prefixed_mapping_iris: list[str]


class ParsedClassMapping(ParsedMapping): ...


class ParsedPropertyMapping(ParsedMapping): ...


@dataclass
class ParsedMappings:
    classes: list[ParsedClassMapping]
    properties: list[ParsedPropertyMapping]


class PrefixResolutionProblemType(StrEnum):
    NO_PREFIX_IN_INPUT = "There is no prefix in the mapping."
    NO_LOCAL_NAME_IN_INPUT = "The mapping only contains a prefix."
    PREFIX_NOT_FOUND = "The prefix in the mapping is not declared in the prefix sheet."


@dataclass
class PrefixResolutionProblem:
    entity_name: str
    input_value: str
    problem: PrefixResolutionProblemType


@dataclass
class ResolvedMapping:
    iri: str
    mapping_iris: list[str]


class ResolvedClassMapping(ResolvedMapping): ...


class ResolvedPropertyMapping(ResolvedMapping): ...


@dataclass
class ResolvedMappings:
    classes: list[ResolvedClassMapping]
    properties: list[ResolvedPropertyMapping]


@dataclass
class MappingUploadFailure:
    prefixed_iri: str
    mapping_iri: str | None
    message: str
