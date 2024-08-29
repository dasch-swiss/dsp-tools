from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Protocol

from rdflib import RDF
from rdflib import RDFS
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

VAL_ONTO = Namespace("http://api.knora.org/validation-onto#")


@dataclass
class ProjectNamespaces:
    onto: Namespace
    data: Namespace


@dataclass
class DataRDF:
    resources: list[ResourceRDF]

    def make_graph(self) -> Graph:
        g = Graph()
        for r in self.resources:
            g += r.make_graph()
        return g


@dataclass
class ResourceRDF:
    res_iri: URIRef
    res_class: URIRef
    label: Literal
    values: list[ValueRDF]

    def make_graph(self) -> Graph:
        g = Graph()
        g.add((self.res_iri, RDF.type, self.res_class))
        g.add((self.res_iri, RDFS.label, self.label))
        for v in self.values:
            g += v.make_graph(self.res_iri)
        return g


@dataclass
class ValueRDF(Protocol):
    prop_name: URIRef
    object_value: Any

    def make_graph(self, res_iri: URIRef) -> Graph:
        raise NotImplementedError


@dataclass
class SimpleTextRDF(ValueRDF):
    prop_name: URIRef
    object_value: Literal

    def make_graph(self, res_iri: URIRef) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, VAL_ONTO.SimpleText))
        g.add((bn, VAL_ONTO.hasSimpleTextValue, self.object_value))
        g.add((res_iri, self.prop_name, bn))
        return g


@dataclass
class IntValueRDF(ValueRDF):
    prop_name: URIRef
    object_value: Literal

    def make_graph(self, res_iri: URIRef) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, VAL_ONTO.IntValue))
        g.add((bn, VAL_ONTO.hasIntValue, self.object_value))
        g.add((res_iri, self.prop_name, bn))
        return g


@dataclass
class ListValueRDF(ValueRDF):
    prop_name: URIRef
    object_value: Literal
    list_name: Literal

    def make_graph(self, res_iri: URIRef) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, VAL_ONTO.ListValue))
        g.add((bn, VAL_ONTO.hasListValue, self.object_value))
        g.add((bn, VAL_ONTO.hasListName, self.list_name))
        g.add((res_iri, self.prop_name, bn))
        return g


@dataclass
class LinkValueRDF(ValueRDF):
    prop_name: URIRef
    object_value: URIRef

    def make_graph(self, res_iri: URIRef) -> Graph:
        g = Graph()
        bn = BNode()
        g.add((bn, RDF.type, VAL_ONTO.LinkValue))
        g.add((bn, VAL_ONTO.hasLinkValueTarget, self.object_value))
        g.add((res_iri, self.prop_name, bn))
        return g