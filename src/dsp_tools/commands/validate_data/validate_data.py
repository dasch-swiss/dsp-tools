import importlib.resources
from pathlib import Path

from rdflib import RDF
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.api_clients import ListClient
from dsp_tools.commands.validate_data.api_clients import OntologyClient
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.api_connection import ApiConnection
from dsp_tools.commands.validate_data.constants import KNORA_API_STR
from dsp_tools.commands.validate_data.get_user_validation_message import get_user_message
from dsp_tools.commands.validate_data.make_data_rdf import make_data_rdf
from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.sparql.construct_shacl import construct_shapes_graphs
from dsp_tools.commands.validate_data.utils import reformat_onto_iri
from dsp_tools.commands.validate_data.validate_ontology import validate_ontology
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_GREEN
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_MAGENTA
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_YELLOW
from dsp_tools.utils.ansi_colors import BOLD_CYAN
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.xml_parsing.get_data_deserialised import get_data_deserialised
from dsp_tools.utils.xml_parsing.get_xml_project import get_xml_project

LIST_SEPARATOR = "\n    - "


VALIDATION_ERRORS_FOUND_MSG = BACKGROUND_BOLD_MAGENTA + "\n   Validation errors found!   " + RESET_TO_DEFAULT


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
    api_con = ApiConnection(api_url)
    graphs = _get_parsed_graphs(api_con, filepath)
    if unknown_classes := _check_for_unknown_resource_classes(graphs):
        msg = unknown_classes.get_msg()
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(msg)
        # if unknown classes are found, we cannot validate all the data in the file
        return True

    shacl_validator = ShaclValidator(api_con)
    save_path = None
    if save_graphs:
        save_path = _get_save_directory(filepath)

    onto_validation_result = validate_ontology(graphs.ontos, shacl_validator, save_path)
    if onto_validation_result:
        problem_msg = onto_validation_result.get_msg()
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(problem_msg)
        # if the ontology itself has errors, we will not validate the data
        return True

    report = _get_validation_result(graphs, shacl_validator, save_path)
    if report.conforms:
        print(BACKGROUND_BOLD_GREEN + "\n   Validation passed!   " + RESET_TO_DEFAULT)
    else:
        reformatted = reformat_validation_graph(report)
        problem_msg = get_user_message(reformatted.problems, filepath)
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(problem_msg)
        if reformatted.unexpected_results:
            if save_graphs:
                print(
                    BACKGROUND_BOLD_YELLOW + "\n   Unexpected violations were found! "
                    "Consult the saved graphs for details.   " + RESET_TO_DEFAULT
                )
                return True
            reformatted.unexpected_results.save_inform_user(
                results_graph=report.validation_graph,
                shacl=report.shacl_graph,
                data=report.data_graph,
            )
    return True


def _get_save_directory(filepath: Path) -> Path:
    parent_directory = filepath.parent
    new_directory = parent_directory / "graphs"
    new_directory.mkdir(exist_ok=True)
    save_path = new_directory / filepath.stem
    print(BOLD_CYAN + f"\n   Saving graphs to {save_path}   " + RESET_TO_DEFAULT)
    return save_path


def _get_parsed_graphs(api_con: ApiConnection, filepath: Path) -> RDFGraphs:
    data_rdf, shortcode = _get_data_info_from_file(filepath, api_con.api_url)
    onto_client = OntologyClient(api_con, shortcode)
    list_client = ListClient(api_con, shortcode)
    rdf_graphs = _create_graphs(onto_client, list_client, data_rdf)
    return rdf_graphs


def _check_for_unknown_resource_classes(rdf_graphs: RDFGraphs) -> UnknownClassesInData | None:
    used_cls = _get_all_used_classes(rdf_graphs.data)
    res_cls, value_cls = _get_all_onto_classes(rdf_graphs.ontos + rdf_graphs.knora_api)
    all_cls = res_cls.union(value_cls)
    if extra_cls := used_cls - all_cls:
        return UnknownClassesInData(unknown_classes=extra_cls, classes_onto=res_cls)
    return None


def _get_all_used_classes(data_graph: Graph) -> set[str]:
    types_used = set(data_graph.objects(predicate=RDF.type))
    return {reformat_onto_iri(x) for x in types_used}


def _get_all_onto_classes(ontos: Graph) -> tuple[set[str], set[str]]:
    is_resource_iri = URIRef(KNORA_API_STR + "isResourceClass")
    resource_classes = set(ontos.subjects(is_resource_iri, Literal(True)))
    res_cls = {reformat_onto_iri(x) for x in resource_classes}
    is_value_iri = URIRef(KNORA_API_STR + "isValueClass")
    value_classes = set(ontos.subjects(is_value_iri, Literal(True)))
    value_cls = {reformat_onto_iri(x) for x in value_classes}
    return res_cls, value_cls


def _get_validation_result(
    rdf_graphs: RDFGraphs, shacl_validator: ShaclValidator, save_path: Path | None
) -> ValidationReportGraphs:
    if save_path:
        _save_graphs(save_path, rdf_graphs)
    report = _validate(shacl_validator, rdf_graphs)
    if save_path:
        report.validation_graph.serialize(f"{save_path}_VALIDATION_REPORT.ttl")
    return report


def _save_graphs(save_path: Path, rdf_graphs: RDFGraphs) -> None:
    rdf_graphs.ontos.serialize(f"{save_path}_ONTO.ttl")
    shacl_onto = rdf_graphs.content_shapes + rdf_graphs.cardinality_shapes + rdf_graphs.ontos
    shacl_onto.serialize(f"{save_path}_SHACL_ONTO.ttl")
    rdf_graphs.cardinality_shapes.serialize(f"{save_path}_SHACL_CARD.ttl")
    rdf_graphs.content_shapes.serialize(f"{save_path}_SHACL_CONTENT.ttl")
    rdf_graphs.data.serialize(f"{save_path}_DATA.ttl")
    onto_data = rdf_graphs.data + rdf_graphs.ontos
    onto_data.serialize(f"{save_path}_ONTO_DATA.ttl")


def _create_graphs(onto_client: OntologyClient, list_client: ListClient, data_rdf: Graph) -> RDFGraphs:
    ontologies = _get_project_ontos(onto_client)
    all_lists = list_client.get_lists()
    knora_ttl = onto_client.get_knora_api()
    knora_api = Graph()
    knora_api.parse(data=knora_ttl, format="ttl")
    shapes = construct_shapes_graphs(ontologies, knora_api, all_lists)
    api_shapes = Graph()
    api_shapes_path = importlib.resources.files("dsp_tools").joinpath("resources/validate_data/api-shapes.ttl")
    api_shapes.parse(str(api_shapes_path))
    api_card_shapes = Graph()
    api_card_path = importlib.resources.files("dsp_tools").joinpath(
        "resources/validate_data/api-shapes-resource-cardinalities.ttl"
    )
    api_card_shapes.parse(str(api_card_path))
    content_shapes = shapes.content + api_shapes
    card_shapes = shapes.cardinality + api_card_shapes
    return RDFGraphs(
        data=data_rdf,
        ontos=ontologies,
        cardinality_shapes=card_shapes,
        content_shapes=content_shapes,
        knora_api=knora_api,
    )


def _get_project_ontos(onto_client: OntologyClient) -> Graph:
    all_ontos = onto_client.get_ontologies()
    onto_g = Graph()
    for onto in all_ontos:
        og = Graph()
        og.parse(data=onto, format="ttl")
        onto_g += og
    return onto_g


def _validate(validator: ShaclValidator, rdf_graphs: RDFGraphs) -> ValidationReportGraphs:
    validation_results = validator.validate(rdf_graphs)
    return ValidationReportGraphs(
        conforms=validation_results.conforms,
        validation_graph=validation_results.validation_graph,
        shacl_graph=rdf_graphs.cardinality_shapes + rdf_graphs.content_shapes,
        onto_graph=rdf_graphs.ontos + rdf_graphs.knora_api,
        data_graph=rdf_graphs.data,
    )


def _get_data_info_from_file(file: Path, api_url: str) -> tuple[Graph, str]:
    xml_project = get_xml_project(file, api_url)
    shortcode, data_deserialised = get_data_deserialised(xml_project.root)
    rdf_data = make_data_rdf(data_deserialised)
    return rdf_data, shortcode
