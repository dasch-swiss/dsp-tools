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
from dsp_tools.commands.validate_data.models.input_problems import OntologyValidationProblem
from dsp_tools.commands.validate_data.models.input_problems import SortedProblems
from dsp_tools.commands.validate_data.models.input_problems import UnknownClassesInData
from dsp_tools.commands.validate_data.models.input_problems import ValidateDataResult
from dsp_tools.commands.validate_data.models.validation import RDFGraphs
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs
from dsp_tools.commands.validate_data.prepare_data.prepare_data import get_info_and_parsed_resources_from_file
from dsp_tools.commands.validate_data.prepare_data.prepare_data import prepare_data_for_validation_from_parsed_resource
from dsp_tools.commands.validate_data.process_validation_report.get_user_validation_message import get_user_message
from dsp_tools.commands.validate_data.process_validation_report.get_user_validation_message import sort_user_problems
from dsp_tools.commands.validate_data.process_validation_report.query_validation_result import reformat_validation_graph
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator
from dsp_tools.commands.validate_data.validation.check_duplicate_files import check_for_duplicate_files
from dsp_tools.commands.validate_data.validation.check_for_unknown_classes import check_for_unknown_resource_classes
from dsp_tools.commands.validate_data.validation.check_for_unknown_classes import get_msg_str_unknown_classes_in_data
from dsp_tools.commands.validate_data.validation.get_validation_report import get_validation_report
from dsp_tools.commands.validate_data.validation.validate_ontology import get_msg_str_ontology_validation_violation
from dsp_tools.commands.validate_data.validation.validate_ontology import validate_ontology
from dsp_tools.error.exceptions import BaseError
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

VALIDATION_ERRORS_FOUND_MSG = BACKGROUND_BOLD_RED + "\n   Validation errors found!   " + RESET_TO_DEFAULT
NO_VALIDATION_ERRORS_FOUND_MSG = BACKGROUND_BOLD_GREEN + "\n   No validation errors found!   " + RESET_TO_DEFAULT


def validate_data(
    filepath: Path,
    creds: ServerCredentials,
    ignore_duplicate_files_warning: bool,
    save_graphs: bool,
    skip_ontology_validation: bool,
) -> bool:
    """
    Takes a file and project information and validates it against the ontologies on the server.

    Args:
        filepath: path to the xml data file
        creds: server credentials for authentication
        ignore_duplicate_files_warning: ignore the shape that checks for duplicate files
        save_graphs: if this flag is set, all the graphs will be saved in a folder
        skip_ontology_validation: skip the ontology validation

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
    rdf_graphs, used_iris = prepare_data_for_validation_from_parsed_resource(
        parsed_resources=parsed_resources,
        authorship_lookup=authorship_lookup,
        permission_ids=permission_ids,
        auth=auth,
        shortcode=shortcode,
    )
    validation_result = _validate_data(rdf_graphs, used_iris, parsed_resources, config)
    if validation_result.no_problems:
        logger.debug("No validation errors found.")
        print(NO_VALIDATION_ERRORS_FOUND_MSG)
        return True
    if isinstance(validation_result.problems, UnknownClassesInData):
        msg = get_msg_str_unknown_classes_in_data(validation_result.problems)
        logger.error(msg)
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(msg)
        # if unknown classes are found, we cannot validate all the data in the file
        return False
    if isinstance(validation_result.problems, OntologyValidationProblem):
        msg = get_msg_str_ontology_validation_violation(validation_result.problems)
        logger.error(msg)
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(msg)
        # if the ontology itself has errors, we will not validate the data
        return False
    if isinstance(validation_result.problems, SortedProblems):
        _print_shacl_validation_violation_message(validation_result.problems, validation_result.report_graphs, config)
        return _get_validation_status(validation_result.problems, config.is_on_prod_server)
    else:
        raise BaseError(f"Unknown validate data problems: {validation_result.problems!s}")


def _validate_data(
    graphs: RDFGraphs,
    used_iris: set[str],
    parsed_resources: list[ParsedResource],
    config: ValidateDataConfig,
) -> ValidateDataResult:
    logger.debug(f"Validate-data called with the following config: {vars(config)}")
    # Check if unknown classes are used
    if unknown_classes := check_for_unknown_resource_classes(graphs, used_iris):
        return ValidateDataResult(False, unknown_classes, None)
    shacl_validator = ShaclCliValidator()
    if not config.skip_ontology_validation:
        # Validation of the ontology
        onto_validation_result = validate_ontology(graphs.ontos, shacl_validator, config)
        if onto_validation_result:
            return ValidateDataResult(False, onto_validation_result, None)
    # Validation of the data
    duplicate_file_warnings = None
    if not config.ignore_duplicate_files_warning:
        duplicate_file_warnings = check_for_duplicate_files(parsed_resources)
    report = get_validation_report(graphs, shacl_validator, config.save_graph_dir)
    if report.conforms:
        if not duplicate_file_warnings:
            return ValidateDataResult(True, None, None)
        else:
            sorted_problems = SortedProblems(
                unique_violations=[],
                user_warnings=duplicate_file_warnings.problems,
                user_info=[],
                unexpected_shacl_validation_components=[],
            )
            return ValidateDataResult(False, sorted_problems, report)
    reformatted = reformat_validation_graph(report)
    sorted_problems = sort_user_problems(reformatted, duplicate_file_warnings)
    return ValidateDataResult(False, sorted_problems, report)


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
        print(VALIDATION_ERRORS_FOUND_MSG)
        print(BOLD_RED, messages.violations.message_header, RESET_TO_DEFAULT)
        v_body = messages.violations.message_body
        if messages.violations.message_df is not None:
            v_body = _save_message_df_get_message_body(messages.violations.message_df, "error", config.xml_file)
        print(v_body)
        logger.error(messages.violations.message_header, v_body)
    else:
        logger.debug("No validation errors found.")
        print(NO_VALIDATION_ERRORS_FOUND_MSG)
    if messages.warnings and config.severity.value <= 2:
        print(BACKGROUND_BOLD_YELLOW + "\n    Warning!    " + RESET_TO_DEFAULT)
        print(BOLD_YELLOW, messages.warnings.message_header, RESET_TO_DEFAULT)
        w_body = messages.warnings.message_body
        if messages.warnings.message_df is not None:
            w_body = _save_message_df_get_message_body(messages.warnings.message_df, "warning", config.xml_file)
        print(w_body)
        logger.warning(messages.warnings.message_header, w_body)
    if messages.infos and config.severity.value == 1:
        print(BACKGROUND_BOLD_CYAN + "\n    Potential Problems Found    " + RESET_TO_DEFAULT)
        print(BOLD_CYAN, messages.infos.message_header, RESET_TO_DEFAULT)
        i_body = messages.infos.message_body
        if messages.infos.message_df is not None:
            i_body = _save_message_df_get_message_body(messages.infos.message_df, "info", config.xml_file)
        print(i_body)
        logger.info(messages.infos.message_header, i_body)
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
            report_graph = cast(ValidationReportGraphs, report)
            _save_unexpected_results_and_inform_user(report_graph, config.xml_file)


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
