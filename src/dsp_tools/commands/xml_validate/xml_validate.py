from datetime import datetime
from pathlib import Path

from pyshacl import validate
from rdflib import Graph

from dsp_tools.commands.xml_validate.deserialise_project import create_project_rdf
from dsp_tools.commands.xml_validate.models.input_problems import AllProblems
from dsp_tools.commands.xml_validate.prepare_input import parse_file
from dsp_tools.commands.xml_validate.reformat_validaton_result import reformat_validation_graph


def xml_validate(file_path: Path) -> bool:
    """Validates an XML file without uploading data."""
    print(f"Start Parse File: {datetime.now()}")
    project_deserialised = parse_file(file_path)
    print(f"Start Create RDF: {datetime.now()}")
    data_rdf = create_project_rdf(project_deserialised)
    print(f"Start Validate Graph: {datetime.now()}")
    validation_result = _validate_graph(data_rdf.make_graph())
    if not validation_result:
        print("Data validation was successful. No errors found.")
        return True
    print(f"Start Reformat result Graph: {datetime.now()}")
    problems = reformat_validation_graph(validation_result)

    print(f"Start make message: {datetime.now()}")
    er = AllProblems(problems)
    msg = er.get_msg()
    # raise InputError(msg)


def _parse_ttl_file(ttl_path: str) -> Graph:
    g = Graph()
    g.parse(ttl_path)
    return g


def _validate_graph(data: Graph) -> Graph | None:
    print("Number of triples", len(data))
    onto = _parse_ttl_file("testdata/xml-validate/poc/onto.ttl")
    val_onto = _parse_ttl_file("testdata/xml-validate/poc/validation-onto.ttl")
    onto_shapes = _parse_ttl_file("testdata/xml-validate/poc/onto-shapes.ttl")

    data = onto + data
    shapes = onto + onto_shapes + val_onto

    return _validate_graph_no_inference(data, shapes)


def _validate_graph_no_inference(data: Graph, shapes: Graph) -> Graph | None:
    conforms, results_graph, _ = validate(data_graph=data, shacl_graph=shapes)
    if conforms:
        return None
    return results_graph
