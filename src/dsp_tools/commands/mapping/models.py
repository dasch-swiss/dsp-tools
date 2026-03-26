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
class PrefixResolutionProblem:
    entity: str
    raw_value: str
    prefix: str


@dataclass
class ClassMapping:
    class_iri: str
    mapping_iris: list[str]


@dataclass
class PropertyMapping:
    property_iri: str
    mapping_iris: list[str]


@dataclass
class ParsedMappingExcel:
    classes: list[ClassMapping]
    properties: list[PropertyMapping]
