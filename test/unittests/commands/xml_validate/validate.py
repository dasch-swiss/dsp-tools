from rdflib import Graph
from pyshacl import validate


def parse_ttl_file(ttl_path: str) -> Graph:
    onto = Graph()
    onto.parse(ttl_path)
    return onto


def validate_graph(shapes: Graph, data: Graph) -> [bool, Graph, str]:
    conforms, results_graph, results_text = validate(
        data_graph=data, shacl_graph=shapes, advanced=True, inference="rdfs"
    )
    return conforms, results_graph, results_text


dat = parse_ttl_file("testdata/xml-validate/invalid-data.ttl")
shapes = parse_ttl_file("testdata/xml-validate/validation_shapes.ttl")

_, _, txt = validate_graph(shapes, dat)
print(txt)
