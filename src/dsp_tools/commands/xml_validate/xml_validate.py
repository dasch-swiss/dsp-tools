from pathlib import Path

from pyshacl import validate
from rdflib import Graph

from dsp_tools.commands.xml_validate.deserialise_project import create_project_rdf
from dsp_tools.commands.xml_validate.models.input_problems import AllProblems
from dsp_tools.commands.xml_validate.models.input_problems import ValidationGraphs
from dsp_tools.commands.xml_validate.prepare_input import parse_file
from dsp_tools.commands.xml_validate.reformat_validaton_result import reformat_validation_graph
from dsp_tools.models.exceptions import InputError


def xml_validate(file_path: Path) -> bool:
    """Validates an XML file without uploading data."""
    project_deserialised = parse_file(file_path)
    data_rdf = create_project_rdf(project_deserialised)
    validation_result = _validate_graph(data_rdf.make_graph())
    if not validation_result:
        print("Data validation was successful. No errors found.")
        return True
    problems = reformat_validation_graph(validation_result)
    er = AllProblems(problems)
    msg = er.get_msg()
    raise InputError(msg)


def _parse_ttl_file(ttl_path: str) -> Graph:
    g = Graph()
    g.parse(ttl_path)
    return g


def _validate_graph(data: Graph) -> ValidationGraphs | None:
    onto = _parse_ttl_file("testdata/xml-validate/onto.ttl")
    val_onto = _parse_ttl_file("testdata/xml-validate/validation-onto.ttl")

    card_data = onto + data
    card_shapes = _parse_ttl_file("testdata/xml-validate/cardinality-shapes.ttl")
    card_graph = _validate_graph_no_inference(card_data, card_shapes)

    prop_shapes = _parse_ttl_file("testdata/xml-validate/property-shapes.ttl")
    prop_data = onto + data + val_onto
    prop_graph = _validate_graph_rdfs_inference(prop_data, prop_shapes)

    if not card_graph and not prop_graph:
        return None
    return ValidationGraphs(cardinality_violations=card_graph, node_violations=prop_graph)


def _validate_graph_no_inference(data: Graph, shapes: Graph) -> Graph | None:
    conforms, results_graph, _ = validate(data_graph=data, shacl_graph=shapes)
    if conforms:
        return None
    return results_graph


def _validate_graph_rdfs_inference(data: Graph, shapes: Graph) -> Graph | None:
    conforms, results_graph, _ = validate(data_graph=data, shacl_graph=shapes, inference="rdfs")
    if conforms:
        return None
    return results_graph
