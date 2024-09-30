from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from rdflib import RDF
from rdflib import RDFS
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")
API_SHAPES = Namespace("http://api.knora.org/ontology/knora-api/shapes/v2#")


@dataclass
class DataRDF:
    triples: list[RDFTriples]

    def make_graph(self) -> Graph:
        g = Graph()
        for r in self.triples:
            g += r.make_graph()
        return g


class RDFTriples(ABC):
    def make_graph(self) -> Graph:
        raise NotImplementedError


@dataclass
class ResourceRDF(RDFTriples):
    res_iri: URIRef
    res_class: URIRef
    label: Literal

    def make_graph(self) -> Graph:
        g = Graph()
        g.add((self.res_iri, RDF.type, self.res_class))
        g.add((self.res_iri, RDFS.label, self.label))
        return g


@dataclass
class ValueRDF(RDFTriples):
    prop_name: URIRef
    object_value: URIRef | Literal
    res_iri: URIRef

    def make_graph(self) -> Graph:
        raise NotImplementedError


@dataclass
class BooleanValueRDF(ValueRDF):
    object_value: Literal

    def make_graph(self) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, KNORA_API.BooleanValue))
        g.add((bn, KNORA_API.booleanValueAsBoolean, self.object_value))
        g.add((self.res_iri, self.prop_name, bn))
        return g


@dataclass
class ColorValueRDF(ValueRDF):
    object_value: Literal

    def make_graph(self) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, KNORA_API.ColorValue))
        g.add((bn, KNORA_API.colorValueAsColor, self.object_value))
        g.add((self.res_iri, self.prop_name, bn))
        return g


@dataclass
class DateValueRDF(ValueRDF):
    object_value: Literal

    def make_graph(self) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, KNORA_API.DateValue))
        g.add((bn, KNORA_API.valueAsString, self.object_value))
        g.add((self.res_iri, self.prop_name, bn))
        return g


@dataclass
class DecimalValueRDF(ValueRDF):
    object_value: Literal

    def make_graph(self) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, KNORA_API.DecimalValue))
        g.add((bn, KNORA_API.decimalValueAsDecimal, self.object_value))
        g.add((self.res_iri, self.prop_name, bn))
        return g


@dataclass
class GeonameValueRDF(ValueRDF):
    object_value: Literal

    def make_graph(self) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, KNORA_API.GeonameValue))
        g.add((bn, KNORA_API.geonameValueAsGeonameCode, self.object_value))
        g.add((self.res_iri, self.prop_name, bn))
        return g


@dataclass
class IntValueRDF(ValueRDF):
    object_value: Literal

    def make_graph(self) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, KNORA_API.IntValue))
        g.add((bn, KNORA_API.intValueAsInt, self.object_value))
        g.add((self.res_iri, self.prop_name, bn))
        return g


@dataclass
class LinkValueRDF(ValueRDF):
    object_value: URIRef

    def make_graph(self) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, KNORA_API.LinkValue))
        g.add((bn, API_SHAPES.linkValueHasTargetID, self.object_value))
        g.add((self.res_iri, self.prop_name, bn))
        return g


@dataclass
class ListValueRDF(ValueRDF):
    prop_name: URIRef
    object_value: Literal
    list_name: Literal

    def make_graph(self) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, KNORA_API.ListValue))
        g.add((bn, API_SHAPES.listNodeAsString, self.object_value))
        g.add((bn, API_SHAPES.listNameAsString, self.list_name))
        g.add((self.res_iri, self.prop_name, bn))
        return g


@dataclass
class SimpleTextRDF(ValueRDF):
    object_value: Literal

    def make_graph(self) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, KNORA_API.TextValue))
        g.add((bn, KNORA_API.valueAsString, self.object_value))
        g.add((self.res_iri, self.prop_name, bn))
        return g


@dataclass
class RichtextRDF(ValueRDF):
    object_value: Literal

    def make_graph(self) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, KNORA_API.TextValue))
        g.add((bn, KNORA_API.textValueAsXml, self.object_value))
        g.add((self.res_iri, self.prop_name, bn))
        return g


@dataclass
class TimeValueRDF(ValueRDF):
    object_value: Literal

    def make_graph(self) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, KNORA_API.TimeValue))
        g.add((bn, KNORA_API.timeValueAsTimeStamp, self.object_value))
        g.add((self.res_iri, self.prop_name, bn))
        return g


@dataclass
class UriValueRDF(ValueRDF):
    object_value: Literal

    def make_graph(self) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, KNORA_API.UriValue))
        g.add((bn, KNORA_API.uriValueAsUri, self.object_value))
        g.add((self.res_iri, self.prop_name, bn))
        return g