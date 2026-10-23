from pathlib import Path

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.commands.validate_data.models.input_problems import InputProblem
from dsp_tools.commands.validate_data.models.input_problems import SortedProblems
from dsp_tools.commands.validate_data.prepare_data.prepare_data import get_info_and_parsed_resources_from_file
from dsp_tools.commands.validate_data.prepare_data.prepare_data import prepare_data_for_validation_from_parsed_resource
from dsp_tools.commands.validate_data.validate_data import _validate_data


def get_problem_types(xml_file: Path, creds: ServerCredentials) -> dict[str, list[str]]:
    """
    Validates the file with validate-data and returns the problem types of the violations, for each resource id.
    Warnings and info do not count.
    A resource with two violations of one type has that type two times.

    Raises:
        ValueError: if the validation does not return sorted problems
    """
    problems = _validate(xml_file, creds)
    if problems is None:
        return {}
    if not isinstance(problems, SortedProblems):
        raise ValueError(f"Validation of {xml_file} did not reach the SHACL step: {problems}")
    return group_problems_by_resource(problems.unique_violations)


def group_problems_by_resource(problems: list[InputProblem]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    for problem in problems:
        if problem.res_id is not None:
            grouped.setdefault(problem.res_id, []).append(problem.problem_type.name)
    return grouped


def _validate(xml_file: Path, creds: ServerCredentials) -> object:
    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    parsed_resources, shortcode, authorship_lookup, permission_ids = get_info_and_parsed_resources_from_file(
        file=xml_file, api_url=auth.server, id2iri_file=None
    )
    graphs, triple_stores, used_iris, existing_resources_retrieved = prepare_data_for_validation_from_parsed_resource(
        parsed_resources=parsed_resources,
        authorship_lookup=authorship_lookup,
        permission_ids=permission_ids,
        auth=auth,
        shortcode=shortcode,
        do_not_request_resource_metadata_from_db=False,
    )
    config = ValidateDataConfig(
        xml_file=xml_file,
        save_graph_dir=None,
        severity=ValidationSeverity.INFO,
        ignore_duplicate_files_warning=False,
        is_on_prod_server=False,
        skip_ontology_validation=False,
        do_not_request_resource_metadata_from_db=False,
    )
    result = _validate_data(
        graphs, triple_stores, used_iris, parsed_resources, config, shortcode, existing_resources_retrieved
    )
    return result.problems
