from pathlib import Path

import pyoxigraph as ox
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.validation.get_validation_report import _append_serialised_graphs
from dsp_tools.commands.validate_data.validation.get_validation_report import _write_serialised_graphs

EX = "http://example.org/"


def _load_store_from_file(path: Path) -> ox.Store:
    store = ox.Store()
    with open(path, "rb") as f:
        store.load(f, format=ox.RdfFormat.TURTLE)
    return store


def _count_store_triples(store: ox.Store) -> int:
    return sum(1 for _ in store)


class TestWriteSerialisedGraphs:
    def test_creates_valid_turtle_file(self, tmp_path: Path) -> None:
        dest = tmp_path / "output.ttl"

        g1 = Graph(store="Oxigraph")
        g1.add((URIRef(f"{EX}s1"), URIRef(f"{EX}p"), Literal("v1")))
        b1 = BNode("b0")
        g1.add((b1, URIRef(f"{EX}label"), Literal("blank-g1")))

        g2 = Graph(store="Oxigraph")
        g2.add((URIRef(f"{EX}s2"), URIRef(f"{EX}p"), Literal("v2")))
        b2 = BNode("b0")
        g2.add((b2, URIRef(f"{EX}label"), Literal("blank-g2")))

        _write_serialised_graphs(dest, g1, g2)

        assert dest.exists()
        store = _load_store_from_file(dest)
        assert _count_store_triples(store) == 4

        label_pred = ox.NamedNode(f"{EX}label")
        labels = {triple.object for triple in store if triple.predicate == label_pred}
        assert labels == {ox.Literal("blank-g1"), ox.Literal("blank-g2")}

        subjects_with_label = [triple.subject for triple in store if triple.predicate == label_pred]
        assert subjects_with_label[0] != subjects_with_label[1]


class TestAppendSerialisedGraphs:
    def test_appends_to_existing_file(self, tmp_path: Path) -> None:
        dest = tmp_path / "output.ttl"
        dest.write_text(
            '<http://example.org/existing> <http://example.org/p> "initial" .\n',
            encoding="utf-8",
        )

        g1 = Graph(store="Oxigraph")
        g1.add((URIRef(f"{EX}s1"), URIRef(f"{EX}p"), Literal("appended-1")))

        g2 = Graph(store="Oxigraph")
        g2.add((URIRef(f"{EX}s2"), URIRef(f"{EX}p"), Literal("appended-2")))

        _append_serialised_graphs(dest, g1, g2)

        store = _load_store_from_file(dest)
        values = {triple.object for triple in store}
        assert ox.Literal("initial") in values
        assert ox.Literal("appended-1") in values
        assert ox.Literal("appended-2") in values
        assert _count_store_triples(store) == 3
