import json
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from pyld import jsonld
from rdflib import RDF
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")


@dataclass(frozen=True)
class ValueRDF(ABC):
    resource_bn: BNode
    prop_name: URIRef
    value: Literal | URIRef
    permissions: Literal | None
    comment: Literal | None

    def serialise(self) -> dict[str, Any]:
        jsonld = self._make_jsonld()
        return self._frame_property(jsonld)

    @abstractmethod
    def _as_graph(self) -> Graph:
        """Creates the value as rdflib graph"""

    def _get_generic_graph(self, val_bn: BNode) -> Graph:
        g = Graph()
        g.add((self.resource_bn, self.prop_name, val_bn))
        if self.permissions:
            g.add((val_bn, KNORA_API.hasPermissions, self.permissions))
        if self.comment:
            g.add((val_bn, KNORA_API.valueHasComment, self.comment))
        return g

    def _make_jsonld(self) -> list[dict[str, Any]]:
        g = self._as_graph()
        graph_bytes = g.serialize(format="json-ld", encoding="utf-8")
        json_graph: list[dict[str, Any]] = json.loads(graph_bytes)
        return json_graph

    def _frame_property(self, serialised_json: list[dict[str, Any]]) -> dict[str, Any]:
        json_frame: dict[str, Any] = {
            str(self.prop_name): {},
        }
        framed: dict[str, Any] = jsonld.frame(serialised_json, json_frame)
        return framed


class BooleanValueRDF(ValueRDF):
    value: Literal

    def _as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.BooleanValue))
        g.add((val_bn, KNORA_API.booleanValueAsBoolean, self.value))
        return g


class IntValueRDF(ValueRDF):
    value: Literal

    def _as_graph(self) -> Graph:
        val_bn = BNode()
        g = self._get_generic_graph(val_bn)
        g.add((val_bn, RDF.type, KNORA_API.IntValue))
        g.add((val_bn, KNORA_API.intValueAsInt, self.value))
        return g
