from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import TypeAlias
from typing import Union

from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.permission import Permissions

OutputTypes: TypeAlias = Union[str, FormattedTextValue, bool, float, int]


@dataclass
class ResourceTransformationProblems:
    res_id: str
    problems: list[str]


@dataclass
class PermissionsNotFound(Exception):
    permission_str: str


@dataclass
class CollectedProblems:
    problems: list[str]


@dataclass
class ResolvingInformationProblem:
    problem: str


@dataclass
class TransformationSteps:
    intermediary_value: Callable[[str, Any, str | None, Permissions | None], IntermediaryValue]
    transformer: Callable[[Any], OutputTypes]


@dataclass
class IntermediaryResource:
    res_id: str
    res_type: str
    values: list[IntermediaryValue]
    permissions: Permissions | None
    file_value: AbstractFileValue | None


@dataclass
class IntermediaryValue:
    prop_name: str
    value: bool | str | int | float | FormattedTextValue
    comment: str | None
    permissions: Permissions | None


@dataclass
class IntermediaryBoolean:
    value: bool


@dataclass
class IntermediaryRichtext:
    value: FormattedTextValue


@dataclass
class IntermediarySimpleText:
    value: str


@dataclass
class AbstractFileValue:
    value: str
    permissions: Permissions | None


@dataclass
class ValueTypeTripleInfo:
    rdf_type: URIRef
    d_type: URIRef
    prop_name: URIRef


@dataclass
class RDFResource:
    res_id: str  # This is for the mapping at the moment and communication with the user
    res_bn: BNode  # This is for the mapping
    triples: list[RDFTriple]

    def to_graph(self) -> Graph:
        g = Graph()
        for val in self.triples:
            g.add(val.to_triple())
        return g


@dataclass
class RDFTriple:
    rdf_subject: URIRef | BNode
    rdf_property: URIRef
    rdf_object: URIRef | Literal | BNode

    def to_triple(self) -> tuple[BNode, URIRef, URIRef | Literal | BNode]:
        return self.rdf_subject, self.rdf_property, self.rdf_object
