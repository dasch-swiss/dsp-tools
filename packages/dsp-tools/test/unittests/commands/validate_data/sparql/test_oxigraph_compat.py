import pytest
from rdflib import RDF
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef
from rdflib.collection import Collection


@pytest.fixture
def oxigraph_graph() -> Graph:
    return Graph(store="Oxigraph")


def test_sparql_construct_graph_with_oxigraph_store(oxigraph_graph: Graph) -> None:
    oxigraph_graph.add((URIRef("http://a"), RDF.type, URIRef("http://B")))
    result = oxigraph_graph.query("CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }")
    assert result.graph is not None
    assert (URIRef("http://a"), RDF.type, URIRef("http://B")) in result.graph


def test_collection_with_oxigraph_store(oxigraph_graph: Graph) -> None:
    bn = BNode()
    items: list[Literal] = [Literal("a", datatype=XSD.string), Literal("b", datatype=XSD.string)]
    Collection(oxigraph_graph, bn, items)  # type: ignore[arg-type]
    # 2 rdf:first + 2 rdf:rest (last rdf:rest points to rdf:nil)
    assert len(list(oxigraph_graph)) == 4


def test_construct_with_blank_nodes_merged_into_oxigraph_store(oxigraph_graph: Graph) -> None:
    oxigraph_graph.add((URIRef("http://ex/A"), RDF.type, URIRef("http://ex/Class")))
    result = oxigraph_graph.query("""
        CONSTRUCT { ?s <http://ex/prop> [ <http://ex/val> ?t ] }
        WHERE { ?s a ?t }
    """)
    assert result.graph is not None
    target = Graph(store="Oxigraph")
    target += result.graph
    assert len(list(target)) == 2  # (A, prop, _:bn) and (_:bn, val, Class)
