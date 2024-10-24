from copy import deepcopy
from pathlib import Path

from lxml import etree
from rdflib import Graph
from termcolor import cprint

from dsp_tools.commands.validate_data.api_connection import OntologyConnection
from dsp_tools.commands.validate_data.api_connection import ShaclValidator
from dsp_tools.commands.validate_data.deserialise_input import deserialise_xml
from dsp_tools.commands.validate_data.make_data_rdf import make_data_rdf
from dsp_tools.commands.validate_data.models.data_deserialised import ProjectDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import XMLProject
from dsp_tools.commands.validate_data.models.data_rdf import DataRDF
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.reformat_validaton_result import reformat_validation_graph
from dsp_tools.commands.validate_data.sparql.construct_shacl import construct_shapes_graph
from dsp_tools.models.exceptions import InputError
from dsp_tools.utils.xml_utils import parse_xml_file
from dsp_tools.utils.xml_utils import remove_comments_from_element_tree
from dsp_tools.utils.xml_utils import transform_into_localnames
from dsp_tools.utils.xml_validation import validate_xml

LIST_SEPARATOR = "\n    - "
KNORA_API = "http://api.knora.org/ontology/knora-api/v2#"


def validate_data(filepath: Path, api_url: str, dev_route: bool, save_graphs: bool) -> bool:  # noqa: ARG001 (unused argument)
    """
    Takes a file and project information and validates it against the ontologies on the server.

    Args:
        filepath: path to the xml data file
        api_url: url of the api host
        dev_route: if this flag is set features that are still in development will be used
        save_graphs: if this flag is set, all the graphs will be saved in a folder

    Returns:
        true unless it crashed
    """
    _inform_about_experimental_feature()
    report = _get_validation_result(api_url, filepath, save_graphs)
    if report.conforms:
        cprint("\n   Validation passed!   ", color="green", attrs=["bold", "reverse"])
    else:
        reformatted = reformat_validation_graph(report)
        problem_msg = reformatted.get_msg(filepath)
        cprint("\n   Validation errors found!   ", color="light_red", attrs=["bold", "reverse"])
        print(problem_msg)
        if reformatted.unexpected_results:
            if save_graphs:
                cprint(
                    "\n   Unexpected violations were found! Consult the saved graphs for details.   ",
                    color="yellow",
                    attrs=["bold", "reverse"],
                )
                return True
            reformatted.unexpected_results.save_inform_user(
                results_graph=report.validation_graph,
                shacl=report.shacl_graph,
                data=report.data_graph,
            )
    return True


def _get_validation_result(api_url: str, filepath: Path, save_graphs: bool) -> ValidationReportGraphs:
    data_rdf, shortcode = _get_data_info_from_file(filepath, api_url)
    onto_con = OntologyConnection(api_url, shortcode)
    rdf_graphs = _create_graphs(onto_con, data_rdf)
    generic_filepath = Path()
    if save_graphs:
        generic_filepath = _save_graphs(filepath, rdf_graphs)
    val = ShaclValidator(api_url)
    report = _validate(val, rdf_graphs)
    if save_graphs:
        report.validation_graph.serialize(f"{generic_filepath}_VALIDATION_REPORT.ttl")
    return report


def _inform_about_experimental_feature() -> None:
    what_is_validated = [
        "This is an experimental feature, it will change and be extended continuously. "
        "The following information of your data is being validated:",
        "Cardinalities",
        "If the value type used matches the ontology",
    ]
    cprint(LIST_SEPARATOR.join(what_is_validated), color="magenta", attrs=["bold"])


def _create_graphs(onto_con: OntologyConnection, data_rdf: DataRDF) -> RDFGraphs:
    ontologies = _get_project_ontos(onto_con)
    knora_ttl = onto_con.get_knora_api()
    knora_api = Graph()
    knora_api.parse(data=knora_ttl, format="ttl")
    onto_for_construction = deepcopy(ontologies) + knora_api
    shapes_graph = construct_shapes_graph(onto_for_construction)
    api_shapes = Graph()
    api_shapes.parse("src/dsp_tools/resources/validate_data/api-shapes.ttl")
    shapes_graph += api_shapes
    data = data_rdf.make_graph()
    return RDFGraphs(
        data=data,
        ontos=ontologies,
        shapes=shapes_graph,
        knora_api=knora_api,
    )


def _get_project_ontos(onto_con: OntologyConnection) -> Graph:
    all_ontos = onto_con.get_ontologies()
    onto_g = Graph()
    for onto in all_ontos:
        og = Graph()
        og.parse(data=onto, format="ttl")
        onto_g += og
    return onto_g


def _save_graphs(filepath: Path, rdf_graphs: RDFGraphs) -> Path:
    parent_directory = filepath.parent
    new_directory = parent_directory / "graphs"
    new_directory.mkdir(exist_ok=True)
    cprint(f"\n   Saving graphs to {new_directory}   ", color="light_blue", attrs=["bold", "reverse"])
    generic_filepath = new_directory / filepath.stem
    rdf_graphs.ontos.serialize(f"{generic_filepath}_ONTO.ttl")
    shacl_onto = rdf_graphs.shapes + rdf_graphs.ontos
    shacl_onto.serialize(f"{generic_filepath}_SHACL_ONTO.ttl")
    rdf_graphs.shapes.serialize(f"{generic_filepath}_SHACL.ttl")
    rdf_graphs.data.serialize(f"{generic_filepath}_DATA.ttl")
    onto_data = rdf_graphs.data + rdf_graphs.ontos
    onto_data.serialize(f"{generic_filepath}_ONTO_DATA.ttl")
    return generic_filepath


def _validate(validator: ShaclValidator, rdf_graphs: RDFGraphs) -> ValidationReportGraphs:
    shapes_str = rdf_graphs.get_shacl_and_onto_str()
    data_str = rdf_graphs.get_data_and_onto_str()
    validation_results = validator.validate(data_str, shapes_str)
    return ValidationReportGraphs(
        conforms=validation_results.conforms,
        validation_graph=validation_results.validation_graph,
        shacl_graph=rdf_graphs.shapes,
        onto_graph=rdf_graphs.ontos,
        data_graph=rdf_graphs.data,
    )


def _get_data_info_from_file(file: Path, api_url: str) -> tuple[DataRDF, str]:
    xml_project = _parse_and_clean_file(file, api_url)
    deserialised: ProjectDeserialised = deserialise_xml(xml_project.root)
    rdf_data: DataRDF = make_data_rdf(deserialised.data)
    return rdf_data, deserialised.info.shortcode


def _parse_and_clean_file(file: Path, api_url: str) -> XMLProject:
    root = parse_xml_file(file)
    root = remove_comments_from_element_tree(root)
    validate_xml(root)
    root = transform_into_localnames(root)
    return _replace_namespaces(root, api_url)


def _replace_namespaces(root: etree._Element, api_url: str) -> XMLProject:
    new_root = deepcopy(root)
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    namespace_lookup = _make_namespace_lookup(api_url, shortcode, default_ontology)
    for ele in new_root.iterdescendants():
        if (found := ele.attrib.get("restype")) or (found := ele.attrib.get("name")):
            split_found = found.split(":")
            if len(split_found) == 1:
                ele.set("restype" if "restype" in ele.attrib else "name", f"{KNORA_API}{found}")
            elif len(split_found) == 2:
                if len(split_found[0]) == 0:
                    found_namespace = namespace_lookup[default_ontology]
                elif not (namespace := namespace_lookup.get(split_found[0])):
                    found_namespace = _construct_namespace(api_url, shortcode, split_found[0])
                    namespace_lookup[split_found[0]] = found_namespace
                else:
                    found_namespace = namespace
                ele.set("restype" if "restype" in ele.attrib else "name", f"{found_namespace}{split_found[1]}")
            else:
                raise InputError(
                    f"It is not permissible to have a colon in a property or resource class name. "
                    f"Please correct the following: {found}"
                )
    return XMLProject(
        shortcode=shortcode,
        root=new_root,
        used_ontologies=set(namespace_lookup.values()),
    )


def _make_namespace_lookup(api_url: str, shortcode: str, default_onto: str) -> dict[str, str]:
    return {default_onto: _construct_namespace(api_url, shortcode, default_onto), "knora-api": KNORA_API}


def _construct_namespace(api_url: str, shortcode: str, onto_name: str) -> str:
    return f"{api_url}/ontology/{shortcode}/{onto_name}/v2#"
