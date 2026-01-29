from datetime import datetime
from pathlib import Path
from typing import cast

import pandas as pd
from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.metadata_client import ExistingResourcesRetrieved
from dsp_tools.commands.create.communicate_problems import print_msg_str_for_potential_problematic_circles
from dsp_tools.commands.create.models.create_problems import CardinalitiesThatMayCreateAProblematicCircle
from dsp_tools.commands.validate_data.models.input_problems import DuplicateFileWarning
from dsp_tools.commands.validate_data.models.input_problems import MessageComponents
from dsp_tools.commands.validate_data.models.input_problems import OntologyValidationProblem
from dsp_tools.commands.validate_data.models.input_problems import SortedProblems
from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.models.input_problems import ValidateDataResult
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.models.validation import TripleStores
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.prepare_data.prepare_data import get_info_and_parsed_resources_from_file
from dsp_tools.commands.validate_data.prepare_data.prepare_data import prepare_data_for_validation_from_parsed_resource
from dsp_tools.commands.validate_data.process_validation_report.get_user_validation_message import get_user_message
from dsp_tools.commands.validate_data.process_validation_report.get_user_validation_message import sort_user_problems
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.validation.check_for_unknown_classes import check_for_unknown_resource_classes
from dsp_tools.commands.validate_data.validation.check_for_unknown_classes import get_msg_str_unknown_classes_in_data
from dsp_tools.commands.validate_data.validation.get_validation_report import get_validation_report
from dsp_tools.commands.validate_data.validation.python_checks import check_for_cardinalities_that_may_cause_a_circle
from dsp_tools.commands.validate_data.validation.python_checks import check_for_duplicate_files
from dsp_tools.commands.validate_data.validation.validate_ontology import get_msg_str_ontology_validation_violation
from dsp_tools.commands.validate_data.validation.validate_ontology import validate_ontology
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_CYAN
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_GREEN
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_YELLOW
from dsp_tools.setup.ansi_colors import BOLD_CYAN
from dsp_tools.setup.ansi_colors import BOLD_RED
from dsp_tools.setup.ansi_colors import BOLD_YELLOW
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.data_formats.uri_util import is_prod_like_server
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource

VALIDATION_ERRORS_FOUND_MSG = BACKGROUND_BOLD_RED + "\n   Validation errors found!   " + RESET_TO_DEFAULT
NO_VALIDATION_ERRORS_FOUND_MSG = BACKGROUND_BOLD_GREEN + "\n   No validation errors found!   " + RESET_TO_DEFAULT


def validate_data(
    filepath: Path,
    creds: ServerCredentials,
    ignore_duplicate_files_warning: bool,
    save_graphs: bool,
    skip_ontology_validation: bool,
    id2iri_file: str | None,
    do_not_request_resource_metadata_from_db: bool,
) -> bool:
    """
    Takes a file and project information and validates it against the ontologies on the server.

    Args:
        filepath: path to the xml data file
        creds: server credentials for authentication
        ignore_duplicate_files_warning: ignore the shape that checks for duplicate files
        save_graphs: if this flag is set, all the graphs will be saved in a folder
        skip_ontology_validation: skip the ontology validation
        id2iri_file: to replace internal IDs of an XML file by IRIs provided in this mapping file
        do_not_request_resource_metadata_from_db: true if no metadata for existing resources should be requested

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
        skip_ontology_validation=skip_ontology_validation,
        do_not_request_resource_metadata_from_db=do_not_request_resource_metadata_from_db,
    )
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)

    parsed_resources, shortcode, authorship_lookup, permission_ids = get_info_and_parsed_resources_from_file(
        file=filepath,
        api_url=auth.server,
        id2iri_file=id2iri_file,
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
    msg = "Starting SHACL schema validation."
    print(msg)
    logger.debug(msg)
    rdf_graphs, triple_stores, used_iris, existing_resources_retrieved = (
        prepare_data_for_validation_from_parsed_resource(
            parsed_resources=parsed_resources,
            authorship_lookup=authorship_lookup,
            permission_ids=permission_ids,
            auth=auth,
            shortcode=shortcode,
            do_not_request_resource_metadata_from_db=config.do_not_request_resource_metadata_from_db,
        )
    )
    validation_result = _validate_data(
        rdf_graphs, triple_stores, used_iris, parsed_resources, config, shortcode, existing_resources_retrieved
    )
    if validation_result.cardinalities_with_potential_circle:
        print_msg_str_for_potential_problematic_circles(validation_result.cardinalities_with_potential_circle)

    if validation_result.no_problems:
        logger.debug(NO_VALIDATION_ERRORS_FOUND_MSG)
        print(NO_VALIDATION_ERRORS_FOUND_MSG)
        return True

    match validation_result.problems:
        case UnknownClassesInData():
            msg = get_msg_str_unknown_classes_in_data(validation_result.problems)
            logger.error(msg)
            print(VALIDATION_ERRORS_FOUND_MSG)
            print(msg + "\n")
            # if unknown classes are found, we cannot validate all the data in the file
            return False
        case OntologyValidationProblem():
            msg = get_msg_str_ontology_validation_violation(validation_result.problems)
            logger.error(msg)
            print(VALIDATION_ERRORS_FOUND_MSG)
            print(msg + "\n")
            # if the ontology itself has errors, we will not validate the data
            return False
        case SortedProblems():
            _print_shacl_validation_violation_message(
                validation_result.problems, validation_result.report_graphs, config
            )
            return _get_validation_status(validation_result.problems, config.is_on_prod_server)
        case _:
            raise UnreachableCodeError()


def _validate_data(
    graphs: RDFGraphs,
    triple_stores: TripleStores,
    used_iris: set[str],
    parsed_resources: list[ParsedResource],
    config: ValidateDataConfig,
    shortcode: str,
    existing_resources_retrieved: ExistingResourcesRetrieved,
) -> ValidateDataResult:
    logger.debug(f"Validate-data called with the following config: {vars(config)}")
    potential_circles = check_for_cardinalities_that_may_cause_a_circle(triple_stores)
    # Check if unknown classes are used
    if unknown_classes := check_for_unknown_resource_classes(graphs, used_iris):
        return ValidateDataResult(
            no_problems=False,
            problems=unknown_classes,
            cardinalities_with_potential_circle=potential_circles,
            report_graphs=None,
        )
    shacl_validator = ShaclCliValidator()
    if not config.skip_ontology_validation:
        # Validation of the ontology
        onto_validation_result = validate_ontology(graphs.ontos, shacl_validator, config)
        if onto_validation_result:
            return ValidateDataResult(
                no_problems=False,
                problems=onto_validation_result,
                cardinalities_with_potential_circle=potential_circles,
                report_graphs=None,
            )
    # Validation of the data
    duplicate_file_warnings = None
    if not config.ignore_duplicate_files_warning:
        duplicate_file_warnings = check_for_duplicate_files(parsed_resources)
    report = get_validation_report(graphs, shacl_validator, config.save_graph_dir)
    if report.conforms:
        return _handle_conforming_shacl_report(duplicate_file_warnings, potential_circles, report)

    reformatted = reformat_validation_graph(report)
    sorted_problems = sort_user_problems(reformatted, duplicate_file_warnings, shortcode, existing_resources_retrieved)
    return ValidateDataResult(
        no_problems=False,
        problems=sorted_problems,
        cardinalities_with_potential_circle=potential_circles,
        report_graphs=report,
    )


def _handle_conforming_shacl_report(
    duplicate_file_warnings: DuplicateFileWarning | None,
    potential_circles: list[CardinalitiesThatMayCreateAProblematicCircle] | None,
    report: ValidationReportGraphs,
) -> ValidateDataResult:
    if not duplicate_file_warnings:
        return ValidateDataResult(
            no_problems=True,
            problems=None,
            cardinalities_with_potential_circle=potential_circles,
            report_graphs=None,
        )
    sorted_problems = SortedProblems(
        unique_violations=[],
        user_warnings=duplicate_file_warnings.problems,
        user_info=[],
        unexpected_shacl_validation_components=[],
    )
    return ValidateDataResult(
        no_problems=False,
        problems=sorted_problems,
        cardinalities_with_potential_circle=potential_circles,
        report_graphs=report,
    )


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
    sorted_problems: SortedProblems, report: ValidationReportGraphs | None, config: ValidateDataConfig
) -> None:
    messages = get_user_message(sorted_problems, config.severity)

    if messages.violations:
        _handle_violations_user_message(messages.violations, config.xml_file)
    else:
        logger.debug(NO_VALIDATION_ERRORS_FOUND_MSG)
        print(NO_VALIDATION_ERRORS_FOUND_MSG)
    if messages.warnings:
        _handle_warnings_user_message(messages.warnings, config)
    else:
        logger.debug("No validation result level WARNING found.")
    if messages.infos:
        _handle_info_user_message(messages.infos, config)
    else:
        logger.debug("No validation result level INFO found.")
    if messages.unexpected_violations:
        report = cast(ValidationReportGraphs, report)
        _handle_unexpected_violations(messages.unexpected_violations, report, config)
    print("\n")


def _handle_violations_user_message(violations: MessageComponents, xml_file: Path) -> None:
    v_body = violations.message_body
    if violations.message_df is not None:
        v_body = _save_message_df_get_message_body(violations.message_df, "error", xml_file)
    print(VALIDATION_ERRORS_FOUND_MSG)
    print(BOLD_RED, violations.message_header, RESET_TO_DEFAULT)
    print(v_body)
    logger.error(violations.message_header, v_body)


def _handle_warnings_user_message(warnings: MessageComponents, config: ValidateDataConfig) -> None:
    w_body = warnings.message_body
    if warnings.message_df is not None:
        w_body = _save_message_df_get_message_body(warnings.message_df, "warning", config.xml_file)
    logger.warning(warnings.message_header, w_body)
    if config.severity.value <= 2:
        print(BACKGROUND_BOLD_YELLOW + "\n    Warning!    " + RESET_TO_DEFAULT)
        print(BOLD_YELLOW, warnings.message_header, RESET_TO_DEFAULT)
        print(w_body)


def _handle_info_user_message(infos: MessageComponents, config: ValidateDataConfig) -> None:
    i_body = infos.message_body
    if infos.message_df is not None:
        i_body = _save_message_df_get_message_body(infos.message_df, "info", config.xml_file)
    logger.info(infos.message_header, i_body)
    if config.severity.value == 1:
        print(BACKGROUND_BOLD_CYAN + "\n    Potential Problems Found    " + RESET_TO_DEFAULT)
        print(BOLD_CYAN, infos.message_header, RESET_TO_DEFAULT)
        print(i_body)


def _handle_unexpected_violations(
    unexpected_violations: MessageComponents, report: ValidationReportGraphs, config: ValidateDataConfig
) -> None:
    logger.error(unexpected_violations.message_header, unexpected_violations.message_body)
    print(
        BACKGROUND_BOLD_RED,
        "\n    Unknown violations found!   ",
        RESET_TO_DEFAULT,
    )
    if config.save_graph_dir:
        print(
            BOLD_RED,
            unexpected_violations.message_header,
            "Consult the saved graphs for details.",
            RESET_TO_DEFAULT,
        )
        print(unexpected_violations.message_body)
    else:
        _save_unexpected_results_and_inform_user(report, config.xml_file)


def _save_message_df_get_message_body(df: pd.DataFrame, severity: str, file_path: Path) -> str:
    out_path = file_path.parent / f"{file_path.stem}_validation_{severity}.csv"
    msg = f"Due to the large number of violations the information was saved at '{out_path}'"
    df.to_csv(out_path, index=False)
    return msg


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
