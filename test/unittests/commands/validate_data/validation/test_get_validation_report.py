import io

import pyoxigraph as ox
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.validation.get_validation_report import _merge_into_ox_store

EX = "http://example.org/"


def _count_store_triples(store: ox.Store) -> int:
    return sum(1 for _ in store)


def _dump_store_to_graph(store: ox.Store) -> Graph:
    buf = io.BytesIO()
    store.dump(buf, format=ox.RdfFormat.TURTLE, from_graph=ox.DefaultGraph())
    buf.seek(0)
    g = Graph()
    g.parse(buf, format="turtle")
    return g


class TestMergeIntoOxStore:
    def test_blank_nodes_are_distinct_after_merge(self) -> None:
        g1 = Graph(store="Oxigraph")
        b1 = BNode("b0")
        g1.add((b1, URIRef(f"{EX}label"), Literal("from-g1")))

        g2 = Graph(store="Oxigraph")
        b2 = BNode("b0")
        g2.add((b2, URIRef(f"{EX}label"), Literal("from-g2")))

        store = _merge_into_ox_store(g1, g2)
        result = _dump_store_to_graph(store)

        labels = {str(o) for _, _, o in result}
        assert "from-g1" in labels
        assert "from-g2" in labels

        subjects = list(result.subjects())
        assert len(subjects) == 2
        assert subjects[0] != subjects[1]

    def test_all_triples_are_present(self) -> None:
        g1 = Graph(store="Oxigraph")
        g1.add((URIRef(f"{EX}s1"), URIRef(f"{EX}p"), Literal("v1")))

        g2 = Graph(store="Oxigraph")
        g2.add((URIRef(f"{EX}s2"), URIRef(f"{EX}p"), Literal("v2")))

        store = _merge_into_ox_store(g1, g2)

        assert _count_store_triples(store) == 2

    def test_single_graph_round_trip_preserves_content(self) -> None:
        g = Graph(store="Oxigraph")
        iri = URIRef(f"{EX}subject")
        g.add((iri, URIRef(f"{EX}type"), Literal("thing")))
        b = BNode()
        g.add((b, URIRef(f"{EX}blank"), Literal("node")))

        store = _merge_into_ox_store(g)
        result = _dump_store_to_graph(store)

        assert (iri, URIRef(f"{EX}type"), Literal("thing")) in result
        blank_literals = [str(o) for _, _, o in result.triples((None, URIRef(f"{EX}blank"), None))]
        assert blank_literals == ["node"]
