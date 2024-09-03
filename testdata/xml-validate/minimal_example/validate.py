from pyshacl import validate
from rdflib import Graph


def parse_ttl_file(ttl_path: str) -> Graph:
    onto = Graph()
    onto.parse(ttl_path)
    return onto


def validate_graph(shapes: Graph, data: Graph) -> [bool, Graph, str]:
    conforms, results_graph, results_text = validate(
        data_graph=data, shacl_graph=shapes, advanced=True, inference="rdfs"
    )
    return conforms, results_graph, results_text


shapes = parse_ttl_file("testdata/xml-validate/minimal_example/shapes.ttl")
onto = parse_ttl_file("testdata/xml-validate/minimal_example/onto.ttl")
data = parse_ttl_file("testdata/xml-validate/minimal_example/data.ttl")
val_shapes = parse_ttl_file("testdata/xml-validate/minimal_example/val-shapes.ttl")
val_onto = parse_ttl_file("testdata/xml-validate/minimal_example/val-onto.ttl")

to_val = data + onto + val_onto

val_with = shapes + onto + val_shapes + val_onto

_, _, txt = validate_graph(val_with, to_val)

print(txt)