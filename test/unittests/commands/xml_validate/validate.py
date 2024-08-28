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


dat = parse_ttl_file("testdata/xml-validate/invalid-data.ttl")

onto_shapes = parse_ttl_file("testdata/xml-validate/onto-shapes.ttl")
onto = parse_ttl_file("testdata/xml-validate/from_api/onto.ttl")
shapes = parse_ttl_file("testdata/xml-validate/validation_shapes.ttl")
shps = onto_shapes + onto + shapes

_, g, txt = validate_graph(shps, dat)

g.serialize("testdata/xml-validate/result.ttl")

print(txt)
