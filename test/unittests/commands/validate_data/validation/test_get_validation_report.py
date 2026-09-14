import io
import logging
from pathlib import Path
from unittest.mock import Mock

import pyoxigraph as ox
import pytest
from loguru import logger
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.exceptions import ShaclValidationCliError
from dsp_tools.commands.validate_data.exceptions import ShaclValidationError
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.validation.get_validation_report import _merge_into_ox_store
from dsp_tools.commands.validate_data.validation.get_validation_report import get_validation_report

EX = "http://example.org/"


def _make_rdf_graphs() -> RDFGraphs:
    return RDFGraphs(
        data=Graph(store="Oxigraph"),
        ontos=Graph(store="Oxigraph"),
        cardinality_shapes=Graph(store="Oxigraph"),
        content_shapes=Graph(store="Oxigraph"),
        knora_api=Graph(store="Oxigraph"),
        resources_in_db_graph=Graph(store="Oxigraph"),
    )


def _raise_already_logged_docker_failure(*_args: object, **_kwargs: object) -> None:
    # simulates ShaclCliValidator.validate() itself: logs once at the origin, then raises
    logger.exception("Docker command failed with 1: stdout='stdout', stderr='stderr'")
    raise ShaclValidationCliError(1, "stdout", "stderr")


def test_already_logged_docker_failure_is_not_logged_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    shacl_validator = Mock(spec=ShaclCliValidator)
    shacl_validator.validate.side_effect = _raise_already_logged_docker_failure
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ShaclValidationCliError):
            get_validation_report(_make_rdf_graphs(), shacl_validator)
    assert len(caplog.records) == 1
    assert "Docker command failed" in caplog.text


def test_already_logged_docker_failure_still_preserves_validation_graphs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    shacl_validator = Mock(spec=ShaclCliValidator)
    shacl_validator.validate.side_effect = ShaclValidationCliError(1, "stdout", "stderr")
    with pytest.raises(ShaclValidationCliError):
        get_validation_report(_make_rdf_graphs(), shacl_validator)
    assert (tmp_path / ".dsp-tools" / "validate-data" / "validation-graphs").is_dir()


def test_fresh_failure_is_logged_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    shacl_validator = Mock(spec=ShaclCliValidator)
    shacl_validator.validate.side_effect = ShaclValidationError("SHACL file not found: shacl.ttl")
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ShaclValidationError, match="data validation"):
            get_validation_report(_make_rdf_graphs(), shacl_validator)
    assert len(caplog.records) == 1
    assert "SHACL file not found" in caplog.text


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
