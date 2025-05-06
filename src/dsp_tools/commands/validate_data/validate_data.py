import importlib.resources
from pathlib import Path

from loguru import logger
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.validate_data.api_clients import ListClient
from dsp_tools.commands.validate_data.api_clients import OntologyClient
from dsp_tools.commands.validate_data.api_clients import ShaclValidator
from dsp_tools.commands.validate_data.get_rdf_like_data import get_rdf_like_data
from dsp_tools.commands.validate_data.get_user_validation_message import get_user_message
from dsp_tools.commands.validate_data.get_user_validation_message import sort_user_problems
from dsp_tools.commands.validate_data.make_data_graph import make_data_graph
from dsp_tools.commands.validate_data.models.input_problems import UnexpectedResults
from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.sparql.construct_shacl import construct_shapes_graphs
from dsp_tools.commands.validate_data.validate_ontology import validate_ontology
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_GREEN
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_MAGENTA
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_YELLOW
from dsp_tools.utils.ansi_colors import BOLD_CYAN
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.get_parsed_resources import get_parsed_resources
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file

LIST_SEPARATOR = "\n    - "


VALIDATION_ERRORS_FOUND_MSG = BACKGROUND_BOLD_MAGENTA + "\n   Validation errors found!   " + RESET_TO_DEFAULT


def validate_data(filepath: Path, api_url: str, save_graphs: bool) -> bool:
    """
    Takes a file and project information and validates it against the ontologies on the server.

    Args:
        filepath: path to the xml data file
        api_url: url of the api host
        save_graphs: if this flag is set, all the graphs will be saved in a folder

    Returns:
        true unless it crashed
    """

    graphs, used_iris = _get_parsed_graphs(api_url, filepath)

    if unknown_classes := _check_for_unknown_resource_classes(graphs, used_iris):
        msg = unknown_classes.get_msg()
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(msg)
        # if unknown classes are found, we cannot validate all the data in the file
        return True

    shacl_validator = ShaclValidator(api_url)
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
        logger.info("Validation passed.")
        print(BACKGROUND_BOLD_GREEN + "\n   Validation passed!   " + RESET_TO_DEFAULT)
    else:
        _inform_user_about_problems(report, filepath, save_graphs)
    return True


def _inform_user_about_problems(report: ValidationReportGraphs, filepath: Path, save_graphs: bool) -> None:
    reformatted = reformat_validation_graph(report)
    sorted_problems = sort_user_problems(reformatted)
    messages = get_user_message(sorted_problems, filepath)
    if messages.referenced_absolute_iris:
        print(
            BACKGROUND_BOLD_YELLOW + "\nYour data references absolute IRIs of resources. "
            "If these resources do not exist in the database or are not of the expected resource type then"
            "the xmlupload will fail. Below you find a list of the references."
            + RESET_TO_DEFAULT
            + f"{messages.referenced_absolute_iris}"
        )
    if messages.problems:
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(messages.problems)
    if sorted_problems.unexpected_shacl_validation_components:
        if save_graphs:
            print(
                BACKGROUND_BOLD_YELLOW + "\nUnexpected violations were found! "
                "Consult the saved graphs for details.   " + RESET_TO_DEFAULT
            )
        else:
            UnexpectedResults(sorted_problems.unexpected_shacl_validation_components).save_inform_user(
                results_graph=report.validation_graph,
                shacl=report.shacl_graph,
                data=report.data_graph,
            )


def _get_parsed_graphs(api_url: str, filepath: Path) -> tuple[RDFGraphs, set[str]]:
    parsed_resources, shortcode = _get_info_from_xml(filepath, api_url)
    used_iris = {x.res_type for x in parsed_resources}
    data_rdf = _make_data_graph_from_parsed_resources(parsed_resources)
    onto_client = OntologyClient(api_url, shortcode)
    list_client = ListClient(api_url, shortcode)
    rdf_graphs = _create_graphs(onto_client, list_client, data_rdf)
    return rdf_graphs, used_iris


def _get_info_from_xml(file: Path, api_url: str) -> tuple[list[ParsedResource], str]:
    root = parse_and_clean_xml_file(file)
    shortcode = root.attrib["shortcode"]
    parsed_resources = get_parsed_resources(root, api_url)
    return parsed_resources, shortcode


def _make_data_graph_from_parsed_resources(parsed_resources: list[ParsedResource]) -> Graph:
    rdf_like_data = get_rdf_like_data(parsed_resources)
    rdf_data = make_data_graph(rdf_like_data)
    return rdf_data


def _check_for_unknown_resource_classes(
    rdf_graphs: RDFGraphs, used_resource_iris: set[str]
) -> UnknownClassesInData | None:
    res_cls = _get_all_onto_classes(rdf_graphs)
    if extra_cls := used_resource_iris - res_cls:
        return UnknownClassesInData(unknown_classes=extra_cls, defined_classes=res_cls)
    return None


def _get_all_onto_classes(rdf_graphs: RDFGraphs) -> set[str]:
    ontos = rdf_graphs.ontos + rdf_graphs.knora_api
    is_resource_iri = URIRef(KNORA_API_STR + "isResourceClass")
    resource_classes = set(ontos.subjects(is_resource_iri, Literal(True)))
    is_usable = URIRef(KNORA_API_STR + "canBeInstantiated")
    usable_resource_classes = set(ontos.subjects(is_usable, Literal(True)))
    user_facing = usable_resource_classes.intersection(resource_classes)
    return {str(x) for x in user_facing}


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
    logger.info("Create all graphs.")
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
    logger.info("Get project ontologies from server.")
    all_ontos = onto_client.get_ontologies()
    onto_g = Graph()
    for onto in all_ontos:
        og = Graph()
        og.parse(data=onto, format="ttl")
        onto_g += og
    return onto_g


def _validate(validator: ShaclValidator, rdf_graphs: RDFGraphs) -> ValidationReportGraphs:
    logger.info("Validate with API.")
    validation_results = validator.validate(rdf_graphs)
    return ValidationReportGraphs(
        conforms=validation_results.conforms,
        validation_graph=validation_results.validation_graph,
        shacl_graph=rdf_graphs.cardinality_shapes + rdf_graphs.content_shapes,
        onto_graph=rdf_graphs.ontos + rdf_graphs.knora_api,
        data_graph=rdf_graphs.data,
    )


def _get_save_directory(filepath: Path) -> Path:
    parent_directory = filepath.parent
    new_directory = parent_directory / "graphs"
    new_directory.mkdir(exist_ok=True)
    save_path = new_directory / filepath.stem
    print(BOLD_CYAN + f"\n   Saving graphs to {save_path}   " + RESET_TO_DEFAULT)
    return save_path
