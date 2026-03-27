from dataclasses import dataclass
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


@dataclass
class PrefixResolutionProblem:
    entity_name: str
    input_value: str
    problem: str


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
class MappingRequestFailedProblem:
    iri: str
    mapping_iri: str
    problem: str
