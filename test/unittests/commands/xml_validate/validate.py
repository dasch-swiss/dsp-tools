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


bad_data = parse_ttl_file("testdata/xml-validate/invalid-data.ttl")

onto_shapes = parse_ttl_file("testdata/xml-validate/onto-shapes.ttl")
onto = parse_ttl_file("testdata/xml-validate/from_api/onto.ttl")
shapes = parse_ttl_file("testdata/xml-validate/validation_shapes.ttl")
shapes = onto_shapes + onto + shapes

bad_data = onto + bad_data
_, g, txt = validate_graph(shapes, bad_data)
print(txt)
#g.serialize("testdata/xml-validate/result.ttl")

# good_data = parse_ttl_file("testdata/xml-validate/valid-data.ttl")
# good_data = onto + good_data
# _, _, good_text = validate_graph(shapes, good_data)
# print(good_text)
