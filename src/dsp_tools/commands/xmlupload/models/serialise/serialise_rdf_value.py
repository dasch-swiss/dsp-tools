from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

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
        """Serialises the value."""

    @abstractmethod
    def _as_graph(self) -> Graph:
        """Creates the value as rdflib graph"""

    def _add_optional_triples(self, val_bn: BNode) -> Graph:
        g = Graph()
        if self.permissions:
            g.add((val_bn, KNORA_API.hasPermissions, self.permissions))
        if self.comment:
            g.add((val_bn, KNORA_API.valueHasComment, self.comment))
        return g


class IntValueRDF(ValueRDF):
    value: Literal

    def _as_graph(self) -> Graph:
        g = Graph()
        val_bn = BNode()
        g.add((val_bn, RDF.type, KNORA_API.IntValue))
        g.add((val_bn, KNORA_API.intValueAsInt, self.value))
        g += self._add_optional_triples(val_bn)
        g.add((self.resource_bn, self.prop_name, val_bn))
        return g
