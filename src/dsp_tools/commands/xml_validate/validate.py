from pyshacl import validate
from rdflib import Graph


def parse_ttl_file(ttl_path: str) -> Graph:
    onto = Graph()
    onto.parse(ttl_path)
    return onto


def validate_graph_no_inference(data: Graph, shapes: Graph) -> [bool, Graph, str]:
    conforms, results_graph, results_text = validate(data_graph=data, shacl_graph=shapes)
    return conforms, results_graph, results_text


def validate_graph_rdfs_inference(data: Graph, shapes: Graph) -> [bool, Graph, str]:
    conforms, results_graph, results_text = validate(data_graph=data, shacl_graph=shapes, inference="rdfs")
    return conforms, results_graph, results_text


def validate_all(data: Graph) -> None:
    onto = parse_ttl_file("testdata/xml-validate/onto.ttl")
    val_onto = parse_ttl_file("testdata/xml-validate/validation-onto.ttl")
    print("*" * 20, "Validate Cardinalities", "*" * 20)
    card_shapes = parse_ttl_file("testdata/xml-validate/cardinality-shapes.ttl")
    card_data = onto + data
    _, _, txt = validate_graph_no_inference(card_data, card_shapes)
    print(txt)

    print("*" * 20, "Validate Values", "*" * 20)
    prop_shapes = parse_ttl_file("testdata/xml-validate/property-shapes.ttl")
    prop_data = onto + data + val_onto
    _, _, txt = validate_graph_rdfs_inference(prop_data, prop_shapes)
    print(txt)


good_data = parse_ttl_file("testdata/xml-validate/data/valid-data.ttl")

bad_data = parse_ttl_file("testdata/xml-validate/data/invalid-data.ttl")


validate_all(bad_data)
