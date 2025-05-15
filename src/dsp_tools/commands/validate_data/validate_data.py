import importlib.resources
from datetime import datetime
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
from dsp_tools.commands.validate_data.models.input_problems import OntologyResourceProblem
from dsp_tools.commands.validate_data.models.input_problems import OntologyValidationProblem
from dsp_tools.commands.validate_data.models.input_problems import SortedProblems
from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.sparql.construct_shacl import construct_shapes_graphs
from dsp_tools.commands.validate_data.utils import reformat_onto_iri
from dsp_tools.commands.validate_data.validate_ontology import validate_ontology
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_CYAN
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_GREEN
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_YELLOW
from dsp_tools.utils.ansi_colors import BOLD_CYAN
from dsp_tools.utils.ansi_colors import BOLD_RED
from dsp_tools.utils.ansi_colors import BOLD_YELLOW
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.get_lookups import get_authorship_lookup
from dsp_tools.utils.xml_parsing.get_parsed_resources import get_parsed_resources
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file

LIST_SEPARATOR = "\n    - "


VALIDATION_ERRORS_FOUND_MSG = BACKGROUND_BOLD_RED + "\n   Validation errors found!   " + RESET_TO_DEFAULT


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
    graphs, used_iris = _prepare_data_for_validation_from_file(api_url, filepath)
    return _validate_data(graphs, used_iris, api_url, filepath, save_graphs)


def validate_parsed_resources(
    parsed_resources: list[ParsedResource],
    authorship_lookup: dict[str, list[str]],
    api_url: str,
    shortcode: str,
    input_filepath: Path,
) -> bool:
    rdf_graphs, used_iris = _prepare_data_for_validation_from_parsed_resource(
        parsed_resources, authorship_lookup, api_url, shortcode
    )
    return _validate_data(rdf_graphs, used_iris, api_url, input_filepath, False)


def _validate_data(graphs: RDFGraphs, used_iris: set[str], api_url: str, filepath: Path, save_graphs: bool) -> bool:
    if unknown_classes := _check_for_unknown_resource_classes(graphs, used_iris):
        msg = _get_msg_str_unknown_classes_in_data(unknown_classes)
        logger.info(msg)
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(msg)
        # if unknown classes are found, we cannot validate all the data in the file
        return False
    shacl_validator = ShaclValidator(api_url)
    save_path = None
    if save_graphs:
        save_path = _get_save_directory(filepath)
    onto_validation_result = validate_ontology(graphs.ontos, shacl_validator, save_path)
    if onto_validation_result:
        msg = _get_msg_str_ontology_validation_violation(onto_validation_result)
        logger.info(msg)
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(msg)
        # if the ontology itself has errors, we will not validate the data
        return False
    report = _get_validation_result(graphs, shacl_validator, save_path)
    if report.conforms:
        logger.info("Validation passed.")
        print(BACKGROUND_BOLD_GREEN + "\n   Validation passed!   " + RESET_TO_DEFAULT)
        return True
    reformatted = reformat_validation_graph(report)
    sorted_problems = sort_user_problems(reformatted)
    _print_shacl_validation_violation_message(sorted_problems, report, filepath, save_graphs)
    no_problems = not any(
        [
            bool(sorted_problems.unique_violations),
            bool(sorted_problems.unexpected_shacl_validation_components),
        ]
    )
    return no_problems


def _prepare_data_for_validation_from_file(api_url: str, filepath: Path) -> tuple[RDFGraphs, set[str]]:
    parsed_resources, shortcode, authorship_lookup = _get_info_from_xml(filepath, api_url)
    return _prepare_data_for_validation_from_parsed_resource(parsed_resources, authorship_lookup, api_url, shortcode)


def _get_info_from_xml(file: Path, api_url: str) -> tuple[list[ParsedResource], str, dict[str, list[str]]]:
    root = parse_and_clean_xml_file(file)
    shortcode = root.attrib["shortcode"]
    authorship_lookup = get_authorship_lookup(root)
    parsed_resources = get_parsed_resources(root, api_url)
    return parsed_resources, shortcode, authorship_lookup


def _prepare_data_for_validation_from_parsed_resource(
    parsed_resources: list[ParsedResource], authorship_lookup: dict[str, list[str]], api_url: str, shortcode: str
) -> tuple[RDFGraphs, set[str]]:
    used_iris = {x.res_type for x in parsed_resources}
    data_rdf = _make_data_graph_from_parsed_resources(parsed_resources, authorship_lookup)
    onto_client = OntologyClient(api_url, shortcode)
    list_client = ListClient(api_url, shortcode)
    rdf_graphs = _create_graphs(onto_client, list_client, data_rdf)
    return rdf_graphs, used_iris


def _make_data_graph_from_parsed_resources(
    parsed_resources: list[ParsedResource], authorship_lookup: dict[str, list[str]]
) -> Graph:
    rdf_like_data = get_rdf_like_data(parsed_resources, authorship_lookup)
    rdf_data = make_data_graph(rdf_like_data)
    return rdf_data


def _get_msg_str_unknown_classes_in_data(unknown: UnknownClassesInData) -> str:
    if unknown_onto_msg := _get_unknown_ontos_msg(unknown):
        return unknown_onto_msg
    unknown_classes = sorted(list(unknown.unknown_classes))
    known_classes = sorted(list(unknown.defined_classes))
    return (
        f"Your data uses resource classes that do not exist in the ontologies in the database.\n"
        f"The following classes that are used in the data are unknown: {', '.join(unknown_classes)}\n"
        f"The following classes exist in the uploaded ontologies: {', '.join(known_classes)}"
    )


def _get_unknown_ontos_msg(unknown: UnknownClassesInData) -> str | None:
    def split_prefix(relative_iri: str) -> str | None:
        if ":" not in relative_iri:
            return None
        return relative_iri.split(":")[0]

    used_ontos = set(not_knora for x in unknown.unknown_classes if (not_knora := split_prefix(x)))
    exising_ontos = set(not_knora for x in unknown.defined_classes if (not_knora := split_prefix(x)))
    if unknown_found := used_ontos - exising_ontos:
        return (
            f"Your data uses ontologies that don't exist in the database.\n"
            f"The following ontologies that are used in the data are unknown: {', '.join(unknown_found)}\n"
            f"The following ontologies are uploaded: {', '.join(exising_ontos)}"
        )
    return None


def _get_msg_str_ontology_validation_violation(onto_violations: OntologyValidationProblem) -> str:
    probs = sorted(onto_violations.problems, key=lambda x: x.res_iri)

    def get_resource_msg(res: OntologyResourceProblem) -> str:
        return f"Resource Class: {res.res_iri} | Problem: {res.msg}"

    problems = [get_resource_msg(x) for x in probs]
    return (
        "The ontology structure contains errors that prevent the validation of the data.\n"
        "Please correct the following errors and re-upload the corrected ontology.\n"
        f"Once those two steps are done, the command `validate-data` will find any problems in the data.\n"
        f"{LIST_SEPARATOR}{LIST_SEPARATOR.join(problems)}"
    )


def _print_shacl_validation_violation_message(
    sorted_problems: SortedProblems, report: ValidationReportGraphs, filepath: Path, save_graphs: bool
) -> None:
    messages = get_user_message(sorted_problems, filepath)
    if messages.violations:
        logger.error(messages.violations.message_header, messages.violations.message_body)
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(BOLD_RED, messages.violations.message_header, RESET_TO_DEFAULT)
        print(messages.violations.message_body)
    if messages.warnings:
        logger.warning(messages.warnings.message_header, messages.warnings.message_body)
        print(BACKGROUND_BOLD_YELLOW + "\n    Warning!    " + RESET_TO_DEFAULT)
        print(BOLD_YELLOW, messages.warnings.message_header, RESET_TO_DEFAULT)
        print(messages.warnings.message_body)
    if messages.infos:
        logger.info(messages.infos.message_header, messages.infos.message_body)
        print(BACKGROUND_BOLD_CYAN + "\n    Potential Problems Found    " + RESET_TO_DEFAULT)
        print(BOLD_CYAN, messages.infos.message_header, RESET_TO_DEFAULT)
        print(messages.infos.message_body)
    if messages.unexpected_violations:
        logger.error(messages.unexpected_violations.message_header, messages.unexpected_violations.message_body)
        print(
            BACKGROUND_BOLD_RED,
            "\n    Unknown violations found!   ",
            RESET_TO_DEFAULT,
        )
        if save_graphs:
            print(
                BOLD_RED,
                messages.unexpected_violations.message_header,
                "Consult the saved graphs for details.",
                RESET_TO_DEFAULT,
            )
            print(messages.unexpected_violations.message_body)
        else:
            _save_unexpected_results_and_inform_user(report, filepath)


def _save_unexpected_results_and_inform_user(report: ValidationReportGraphs, filepath: Path) -> None:
    timestamp = f"{datetime.now()!s}_"
    save_path = filepath.parent / f"{timestamp}_validation_result.ttl"
    report.validation_graph.serialize(save_path)
    shacl_p = filepath.parent / f"{timestamp}_shacl.ttl"
    report.shacl_graph.serialize(shacl_p)
    data_p = filepath.parent / f"{timestamp}_data.ttl"
    report.data_graph.serialize(data_p)
    msg = (
        f"\nPlease contact the development team with the files starting with the timestamp '{timestamp}' "
        f"in the directory '{filepath.parent}'."
    )
    print(BOLD_RED + msg + RESET_TO_DEFAULT)


def _check_for_unknown_resource_classes(
    rdf_graphs: RDFGraphs, used_resource_iris: set[str]
) -> UnknownClassesInData | None:
    res_cls = _get_all_onto_classes(rdf_graphs)
    if extra_cls := used_resource_iris - res_cls:
        unknown_classes = {reformat_onto_iri(x) for x in extra_cls}
        defined_classes = {reformat_onto_iri(x) for x in res_cls}
        return UnknownClassesInData(unknown_classes=unknown_classes, defined_classes=defined_classes)
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
