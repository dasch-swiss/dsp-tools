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


onto_shapes = parse_ttl_file("testdata/xml-validate/onto-shapes.ttl")
onto = parse_ttl_file("testdata/xml-validate/from_api/onto.ttl")
val_shapes = parse_ttl_file("testdata/xml-validate/validation-shapes.ttl")
val_onto = parse_ttl_file("testdata/xml-validate/validation-onto.ttl")
shapes = onto_shapes + onto + val_shapes + val_onto

# bad_data = parse_ttl_file("testdata/xml-validate/data/invalid-data.ttl")
# data = onto + bad_data + val_onto

good_data = parse_ttl_file("testdata/xml-validate/data/valid-data.ttl")
data = onto + good_data + val_onto

_, g, txt = validate_graph(shapes, data)
print(txt)
# g.serialize("testdata/xml-validate/result.ttl")
