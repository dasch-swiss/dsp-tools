from datetime import datetime
from pathlib import Path

from loguru import logger
from rdflib import Graph

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.commands.validate_data.constants import CARDINALITY_DATA_TTL
from dsp_tools.commands.validate_data.constants import CARDINALITY_REPORT_TTL
from dsp_tools.commands.validate_data.constants import CARDINALITY_SHACL_TTL
from dsp_tools.commands.validate_data.constants import CONTENT_DATA_TTL
from dsp_tools.commands.validate_data.constants import CONTENT_REPORT_TTL
from dsp_tools.commands.validate_data.constants import CONTENT_SHACL_TTL
from dsp_tools.commands.validate_data.models.input_problems import SortedProblems
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationFilePaths
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.prepare_data.prepare_data import get_info_and_parsed_resources_from_file
from dsp_tools.commands.validate_data.prepare_data.prepare_data import prepare_data_for_validation_from_parsed_resource
from dsp_tools.commands.validate_data.process_validation_report.get_user_validation_message import get_user_message
from dsp_tools.commands.validate_data.process_validation_report.get_user_validation_message import sort_user_problems
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.utils import clean_up_temp_directory
from dsp_tools.commands.validate_data.utils import get_temp_directory
from dsp_tools.commands.validate_data.validation.check_duplicate_files import check_for_duplicate_files
from dsp_tools.commands.validate_data.validation.check_for_unknown_classes import check_for_unknown_resource_classes
from dsp_tools.commands.validate_data.validation.check_for_unknown_classes import get_msg_str_unknown_classes_in_data
from dsp_tools.commands.validate_data.validation.validate_ontology import get_msg_str_ontology_validation_violation
from dsp_tools.commands.validate_data.validation.validate_ontology import validate_ontology
from dsp_tools.error.exceptions import ShaclValidationError
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_CYAN
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_GREEN
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.utils.ansi_colors import BACKGROUND_BOLD_YELLOW
from dsp_tools.utils.ansi_colors import BOLD_CYAN
from dsp_tools.utils.ansi_colors import BOLD_RED
from dsp_tools.utils.ansi_colors import BOLD_YELLOW
from dsp_tools.utils.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.data_formats.uri_util import is_prod_like_server
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource

LIST_SEPARATOR = "\n    - "


VALIDATION_ERRORS_FOUND_MSG = BACKGROUND_BOLD_RED + "\n   Validation errors found!   " + RESET_TO_DEFAULT
NO_VALIDATION_ERRORS_FOUND_MSG = BACKGROUND_BOLD_GREEN + "\n   No validation errors found!   " + RESET_TO_DEFAULT


def validate_data(
    filepath: Path, creds: ServerCredentials, ignore_duplicate_files_warning: bool, save_graphs: bool
) -> bool:
    """
    Takes a file and project information and validates it against the ontologies on the server.

    Args:
        filepath: path to the xml data file
        creds: server credentials for authentication
        ignore_duplicate_files_warning: ignore the shape that checks for duplicate files
        save_graphs: if this flag is set, all the graphs will be saved in a folder

    Returns:
        True if no errors that impede an xmlupload were found.
        Warnings and user info do not impede an xmlupload.
    """
    graph_save_dir = None

    if save_graphs:
        graph_save_dir = _get_graph_save_dir(filepath)
    config = ValidateDataConfig(
        xml_file=filepath,
        save_graph_dir=graph_save_dir,
        severity=ValidationSeverity.INFO,
        ignore_duplicate_files_warning=ignore_duplicate_files_warning,
        is_on_prod_server=is_prod_like_server(creds.server),
    )
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)

    parsed_resources, shortcode, authorship_lookup, permission_ids = get_info_and_parsed_resources_from_file(
        file=filepath,
        api_url=auth.server,
    )
    return validate_parsed_resources(
        parsed_resources=parsed_resources,
        authorship_lookup=authorship_lookup,
        permission_ids=permission_ids,
        shortcode=shortcode,
        config=config,
        auth=auth,
    )


def validate_parsed_resources(
    parsed_resources: list[ParsedResource],
    authorship_lookup: dict[str, list[str]],
    permission_ids: list[str],
    shortcode: str,
    config: ValidateDataConfig,
    auth: AuthenticationClient,
) -> bool:
    ignore_duplicate_files = config.ignore_duplicate_files_warning
    if not config.ignore_duplicate_files_warning:
        duplicate_check = check_for_duplicate_files(parsed_resources, config)
        if duplicate_check.user_msg:
            logger.error(duplicate_check.user_msg)
            print(f"{BACKGROUND_BOLD_RED}   Duplicate Filepaths Found!    {RESET_TO_DEFAULT}")
            print(f"{BOLD_RED}{duplicate_check.user_msg}{RESET_TO_DEFAULT}")
        if not duplicate_check.should_continue:
            return False
        ignore_duplicate_files = duplicate_check.duplicate_files_must_be_ignored

    rdf_graphs, used_iris = prepare_data_for_validation_from_parsed_resource(
        parsed_resources=parsed_resources,
        authorship_lookup=authorship_lookup,
        permission_ids=permission_ids,
        auth=auth,
        shortcode=shortcode,
        ignore_duplicate_files_warning=ignore_duplicate_files,
    )
    return _validate_data(rdf_graphs, used_iris, config)


def _validate_data(graphs: RDFGraphs, used_iris: set[str], config: ValidateDataConfig) -> bool:
    logger.debug(f"Validate-data called with the following config: {vars(config)}")
    if unknown_classes := check_for_unknown_resource_classes(graphs, used_iris):
        msg = get_msg_str_unknown_classes_in_data(unknown_classes)
        logger.error(msg)
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(msg)
        # if unknown classes are found, we cannot validate all the data in the file
        return False
    shacl_validator = ShaclCliValidator()
    onto_validation_result = validate_ontology(graphs.ontos, shacl_validator, config)
    if onto_validation_result:
        msg = get_msg_str_ontology_validation_violation(onto_validation_result)
        logger.error(msg)
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(msg)
        # if the ontology itself has errors, we will not validate the data
        return False
    report = _get_validation_report(graphs, shacl_validator, config.save_graph_dir)
    if report.conforms:
        logger.debug("No validation errors found.")
        print(NO_VALIDATION_ERRORS_FOUND_MSG)
        return True
    reformatted = reformat_validation_graph(report)
    sorted_problems = sort_user_problems(reformatted)
    _print_shacl_validation_violation_message(sorted_problems, report, config)
    return _get_validation_status(sorted_problems, config.is_on_prod_server)


def _get_validation_report(
    rdf_graphs: RDFGraphs, shacl_validator: ShaclCliValidator, graph_save_dir: Path | None = None
) -> ValidationReportGraphs:
    tmp_dir = get_temp_directory()
    tmp_path = Path(tmp_dir.name)
    dir_to_save_graphs = graph_save_dir
    try:
        result = _call_shacl_cli(rdf_graphs, shacl_validator, tmp_path)
        return result
    except Exception as e:  # noqa: BLE001
        logger.exception(e)
        dir_to_save_graphs = tmp_path.parent / "validation-graphs"
        msg = (
            f"An error occurred during the data validation. "
            f"Please contact the dsp-tools development team "
            f"with your log files and the files in the directory: {dir_to_save_graphs}"
        )
        raise ShaclValidationError(msg) from None
    finally:
        clean_up_temp_directory(tmp_dir, dir_to_save_graphs)


def _call_shacl_cli(
    rdf_graphs: RDFGraphs, shacl_validator: ShaclCliValidator, tmp_path: Path
) -> ValidationReportGraphs:
    _create_and_write_graphs(rdf_graphs, tmp_path)
    results_graph = Graph()
    conforms = True
    card_files = ValidationFilePaths(
        directory=tmp_path,
        data_file=CARDINALITY_DATA_TTL,
        shacl_file=CARDINALITY_SHACL_TTL,
        report_file=CARDINALITY_REPORT_TTL,
    )
    card_result = shacl_validator.validate(card_files)
    if not card_result.conforms:
        results_graph += card_result.validation_graph
        conforms = False
    content_files = ValidationFilePaths(
        directory=tmp_path,
        data_file=CONTENT_DATA_TTL,
        shacl_file=CONTENT_SHACL_TTL,
        report_file=CONTENT_REPORT_TTL,
    )
    content_result = shacl_validator.validate(content_files)
    if not content_result.conforms:
        results_graph += content_result.validation_graph
        conforms = False
    return ValidationReportGraphs(
        conforms=conforms,
        validation_graph=results_graph,
        shacl_graph=rdf_graphs.cardinality_shapes + rdf_graphs.content_shapes,
        onto_graph=rdf_graphs.ontos + rdf_graphs.knora_api,
        data_graph=rdf_graphs.data,
    )


def _create_and_write_graphs(rdf_graphs: RDFGraphs, tmp_path: Path) -> None:
    logger.debug("Serialise RDF graphs into turtle strings")
    data_str = rdf_graphs.data.serialize(format="ttl")
    ontos_str = rdf_graphs.ontos.serialize(format="ttl")
    card_shape_str = rdf_graphs.cardinality_shapes.serialize(format="ttl")
    content_shape_str = rdf_graphs.content_shapes.serialize(format="ttl")
    knora_api_str = rdf_graphs.knora_api.serialize(format="ttl")
    turtle_paths_and_graphs = [
        (tmp_path / CARDINALITY_DATA_TTL, data_str),
        (tmp_path / CARDINALITY_SHACL_TTL, card_shape_str + ontos_str + knora_api_str),
        (tmp_path / CONTENT_DATA_TTL, data_str + ontos_str + knora_api_str),
        (tmp_path / CONTENT_SHACL_TTL, content_shape_str + ontos_str + knora_api_str),
    ]
    for f_path, content in turtle_paths_and_graphs:
        with open(f_path, "w") as writer:
            writer.write(content)


def _get_graph_save_dir(filepath: Path) -> Path:
    parent_directory = filepath.parent
    new_directory = parent_directory / "graphs"
    new_directory.mkdir(exist_ok=True)
    save_file_template = new_directory / filepath.stem
    print(BOLD_CYAN + f"\n   Saving graphs to {save_file_template}   " + RESET_TO_DEFAULT)
    return save_file_template


def _get_validation_status(all_problems: SortedProblems, is_on_prod: bool) -> bool:
    violations = any(
        [
            bool(all_problems.unique_violations),
            bool(all_problems.unexpected_shacl_validation_components),
        ]
    )
    if violations:
        return False
    if is_on_prod and all_problems.user_warnings:
        return False
    return True


def _print_shacl_validation_violation_message(
    sorted_problems: SortedProblems, report: ValidationReportGraphs, config: ValidateDataConfig
) -> None:
    messages = get_user_message(sorted_problems, config.xml_file)
    if messages.violations:
        logger.error(messages.violations.message_header, messages.violations.message_body)
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(BOLD_RED, messages.violations.message_header, RESET_TO_DEFAULT)
        print(messages.violations.message_body)
    else:
        logger.debug("No validation errors found.")
        print(NO_VALIDATION_ERRORS_FOUND_MSG)
    if messages.warnings and config.severity.value <= 2:
        logger.warning(messages.warnings.message_header, messages.warnings.message_body)
        print(BACKGROUND_BOLD_YELLOW + "\n    Warning!    " + RESET_TO_DEFAULT)
        print(BOLD_YELLOW, messages.warnings.message_header, RESET_TO_DEFAULT)
        print(messages.warnings.message_body)
    if messages.infos and config.severity.value == 1:
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
        if config.save_graph_dir:
            print(
                BOLD_RED,
                messages.unexpected_violations.message_header,
                "Consult the saved graphs for details.",
                RESET_TO_DEFAULT,
            )
            print(messages.unexpected_violations.message_body)
        else:
            _save_unexpected_results_and_inform_user(report, config.xml_file)


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
