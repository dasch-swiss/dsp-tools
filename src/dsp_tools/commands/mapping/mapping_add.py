import time
from collections.abc import Callable
from functools import partial
from http import HTTPStatus
from urllib.parse import quote_plus

from loguru import logger
from tqdm import tqdm

from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.mapping_client import MappingClient
from dsp_tools.clients.mapping_client_live import MappingClientLive
from dsp_tools.clients.ontology_get_client_live import OntologyGetClientLive
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.mapping.exceptions import OntologyReferencedNotFoundError
from dsp_tools.commands.mapping.existing_mappings import get_existing_mappings
from dsp_tools.commands.mapping.existing_mappings import select_mappings_to_delete
from dsp_tools.commands.mapping.models import MappingAction
from dsp_tools.commands.mapping.models import MappingConfig
from dsp_tools.commands.mapping.models import MappingDeletion
from dsp_tools.commands.mapping.models import MappingDeletions
from dsp_tools.commands.mapping.models import MappingInfo
from dsp_tools.commands.mapping.models import MappingUploadFailure
from dsp_tools.commands.mapping.models import PrefixResolutionProblem
from dsp_tools.commands.mapping.models import ResolvedClassMapping
from dsp_tools.commands.mapping.models import ResolvedPropertyMapping
from dsp_tools.commands.mapping.parse_excel import parse_mapping_excel
from dsp_tools.commands.mapping.resolve_parsed_mappings import resolve_parsed_mappings
from dsp_tools.error.exceptions import UnreachableCodeError
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_GREEN
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.data_formats.iri_util import from_dsp_iri_to_prefixed_iri
from dsp_tools.utils.data_formats.iri_util import make_dsp_ontology_prefix
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import should_retry_request

RETRY_SLEEP_SECONDS = 5
LIST_MESSAGE_SEPARATOR = "\n    - "

RERUN_ADVICE = (
    "This command replaces mappings: existing external mappings are deleted before the new ones are added.\n"
    "If a deletion succeeded but the subsequent addition failed, "
    "that class or property currently has no external mappings.\n"
    "The command is re-runnable: fix the problems above "
    "and run `dsp-tools mapping add` again with the same config file."
)


def mapping_add(info: MappingInfo) -> bool:
    logger.info(f"Starting `mapping add` for ontology '{info.config.ontology}' (shortcode {info.config.shortcode})")
    prefix_problems, upload_problems = _mapping_add(info)

    match prefix_problems, upload_problems:
        case None, None:
            print(f"{BACKGROUND_BOLD_GREEN}All mappings were replaced successfully.{RESET_TO_DEFAULT}")
            return True
        case list(), None:
            _communicate_parsing_problems(prefix_problems)
            return False
        case None, list():
            _communicate_upload_failures(upload_problems)
            return False
        case _:
            raise UnreachableCodeError()


def _mapping_add(info: MappingInfo) -> tuple[list[PrefixResolutionProblem] | None, list[MappingUploadFailure] | None]:
    parsed_excel, prefix_lookup = parse_mapping_excel(info.config.excel_file)
    ontology_namespace = make_dsp_ontology_prefix(info.server.server, info.config.shortcode, info.config.ontology)
    resolved_mappings, problems = resolve_parsed_mappings(parsed_excel, prefix_lookup, ontology_namespace)
    if problems:
        return problems, None

    auth = AuthenticationClientLive(
        server=info.server.server,
        email=info.server.user,
        password=info.server.password,
    )
    ontology_iri = ontology_namespace.rstrip("#")
    ontology_ttl = _check_project_and_get_ontology_ttl(auth, info.config, ontology_iri)
    existing_mappings = get_existing_mappings(ontology_ttl, ontology_namespace, auth.server)
    deletions = select_mappings_to_delete(existing_mappings, resolved_mappings)
    _communicate_planned_deletions(deletions)

    encoded_ontology_iri = quote_plus(ontology_iri)
    client = MappingClientLive(server=auth.server, encoded_ontology_iri=encoded_ontology_iri, auth=auth)

    # The add phase runs even if some deletions failed: aborting in between would leave entities
    # with fewer mappings and no replacements. All failures are collected into one report.
    failures = _delete_class_mappings(client, deletions.classes)
    failures.extend(_delete_property_mappings(client, deletions.properties))
    failures.extend(_add_classes_mappings(client, resolved_mappings.classes))
    failures.extend(_add_properties_mappings(client, resolved_mappings.properties))

    if failures:
        return None, failures
    return None, None


def _communicate_parsing_problems(problem_list: list[PrefixResolutionProblem]) -> None:
    err_found_msg = f"{len(problem_list)} mapping properties or classes could not be correctly resolved."
    logger.error(err_found_msg)
    print(f"{BACKGROUND_BOLD_RED}{err_found_msg}{RESET_TO_DEFAULT}")
    problem_list = sorted(problem_list, key=lambda x: x.entity_name)
    problem_str_list = [
        f"Ontology reference '{p.entity_name}' | Problematic mapping: '{p.input_value}' | Problem: {p.problem!s}"
        for p in problem_list
    ]
    problem_str = LIST_MESSAGE_SEPARATOR + LIST_MESSAGE_SEPARATOR.join(problem_str_list)
    logger.error(problem_str)
    print(problem_str)


def _check_project_and_get_ontology_ttl(
    auth: AuthenticationClient, mapping_config: MappingConfig, ontology_iri: str
) -> str:
    logger.debug("Check if the project and ontology exists on the server.")
    project_client = ProjectClientLive(auth.server, auth)
    # If the project does not exist this will raise an error which we will let escalate,
    # this is for a more nuanced error message.
    project_client.get_project_iri(mapping_config.shortcode)

    onto_client = OntologyGetClientLive(api_url=auth.server, shortcode=mapping_config.shortcode)
    # If no ontologies are found this will raise an error which we let escalate.
    ontologies, ontology_iris = onto_client.get_ontologies()
    for one_ontology, one_iri in zip(ontologies, ontology_iris, strict=True):
        if one_iri == ontology_iri:
            return one_ontology
    raise OntologyReferencedNotFoundError(mapping_config.shortcode, mapping_config.ontology)


def _communicate_planned_deletions(deletions: MappingDeletions) -> None:
    all_deletions = [*deletions.classes, *deletions.properties]
    if not all_deletions:
        msg = "No existing external mappings to delete."
        logger.info(msg)
        print(msg)
        return
    affected = sorted({from_dsp_iri_to_prefixed_iri(x.entity_iri) for x in all_deletions})
    msg = (
        f"{len(all_deletions)} existing external mapping(s) of {len(affected)} class(es)/property(ies) "
        f"will be deleted. The Excel file is the source of truth, so this includes classes and properties "
        f"that the Excel file does not mention:"
    )
    msg += LIST_MESSAGE_SEPARATOR + LIST_MESSAGE_SEPARATOR.join(affected)
    logger.info(msg)
    print(msg)


def _delete_class_mappings(client: MappingClient, deletions: list[MappingDeletion]) -> list[MappingUploadFailure]:
    if not deletions:
        return []
    failures: list[MappingUploadFailure] = []
    logger.debug("Deleting mapping from classes")
    for deletion in tqdm(deletions, desc="    Deleting mapping from classes", dynamic_ncols=True):
        send = partial(client.delete_class_mapping, deletion.entity_iri, deletion.mapping_iri)
        failures.extend(
            _send_one_request_with_retry(send, deletion.entity_iri, deletion.mapping_iri, MappingAction.DELETE)
        )
    return failures


def _delete_property_mappings(client: MappingClient, deletions: list[MappingDeletion]) -> list[MappingUploadFailure]:
    if not deletions:
        return []
    failures: list[MappingUploadFailure] = []
    logger.debug("Deleting mapping from properties")
    for deletion in tqdm(deletions, desc="    Deleting mapping from properties", dynamic_ncols=True):
        send = partial(client.delete_property_mapping, deletion.entity_iri, deletion.mapping_iri)
        failures.extend(
            _send_one_request_with_retry(send, deletion.entity_iri, deletion.mapping_iri, MappingAction.DELETE)
        )
    return failures


def _add_classes_mappings(
    client: MappingClient, classes_mapping: list[ResolvedClassMapping]
) -> list[MappingUploadFailure]:
    if not classes_mapping:
        return []
    failures: list[MappingUploadFailure] = []
    logger.debug("Adding mapping to classes")
    for cls in tqdm(classes_mapping, desc="    Adding mapping to classes", dynamic_ncols=True):
        send = partial(client.put_class_mapping, cls.iri, cls.mapping_iris)
        failures.extend(_send_one_request_with_retry(send, cls.iri, None, MappingAction.ADD))
    return failures


def _add_properties_mappings(
    client: MappingClient, properties_mapping: list[ResolvedPropertyMapping]
) -> list[MappingUploadFailure]:
    if not properties_mapping:
        return []
    failures: list[MappingUploadFailure] = []
    logger.debug("Adding mapping to properties")
    for prop in tqdm(properties_mapping, desc="    Adding mapping to properties", dynamic_ncols=True):
        send = partial(client.put_property_mapping, prop.iri, prop.mapping_iris)
        failures.extend(_send_one_request_with_retry(send, prop.iri, None, MappingAction.ADD))
    return failures


def _send_one_request_with_retry(
    send: Callable[[], ResponseCodeAndText | None],
    entity_iri: str,
    mapping_iri: str | None,
    action: MappingAction,
) -> list[MappingUploadFailure]:
    response = send()
    # happy path
    if response is None:
        return []
    # retry if it is a retriable status code
    if should_retry_request(response):
        logger.warning(f"Retrying to {action} mapping for '{entity_iri}' in {RETRY_SLEEP_SECONDS} seconds.")
        time.sleep(RETRY_SLEEP_SECONDS)
        response = send()
        if response is None:
            return []
        logger.error(f"Unable to {action} mapping for '{entity_iri}' after retrying.")
    # non retriable error
    else:
        logger.error(f"Unable to {action} mapping for '{entity_iri}'.")
    return _get_correct_user_message_for_non_ok_response(entity_iri, response, action, mapping_iri)


def _get_correct_user_message_for_non_ok_response(
    iri: str, response_code_text: ResponseCodeAndText, action: MappingAction, mapping_iri: str | None
) -> list[MappingUploadFailure]:
    if response_code_text.status_code in (HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND):
        return _get_detailed_user_message(iri, response_code_text, action, mapping_iri)
    prefixed_iri = from_dsp_iri_to_prefixed_iri(iri)
    msg = (
        f"Unexpected error while trying to {action} the mapping for class/property '{prefixed_iri}'. "
        f"Original status code: {response_code_text.status_code}\nOriginal message: {response_code_text.text}"
    )
    return [MappingUploadFailure(prefixed_iri=prefixed_iri, mapping_iri=mapping_iri, message=msg, action=action)]


def _get_detailed_user_message(
    iri: str, response_code_text: ResponseCodeAndText, action: MappingAction, mapping_iri: str | None
) -> list[MappingUploadFailure]:
    prefixed_iri = from_dsp_iri_to_prefixed_iri(iri)
    if not response_code_text.v3_errors:
        return [
            MappingUploadFailure(
                prefixed_iri=prefixed_iri,
                mapping_iri=mapping_iri,
                message=response_code_text.text,
                action=action,
            )
        ]
    failures = []
    for v3_err in response_code_text.v3_errors:
        failed_mapping_iri = mapping_iri
        match v3_err.error_code:
            case "class_not_found":
                msg = f"The class '{prefixed_iri}' was not found in the ontology on the server."
            case "property_not_found":
                msg = f"The property '{prefixed_iri}' was not found in the ontology on the server."
            case "invalid_ontology_mapping_iri":
                failed_mapping_iri = v3_err.details.get("iri") or mapping_iri
                msg = f"The mapping IRI '{failed_mapping_iri}' is not a valid external ontology IRI."
            case _:
                details_str = ", ".join(f"{k}={v}" for k, v in v3_err.details.items()) if v3_err.details else ""
                msg = f"{v3_err.message}" + (f" ({details_str})" if details_str else "")
        failures.append(
            MappingUploadFailure(prefixed_iri=prefixed_iri, mapping_iri=failed_mapping_iri, message=msg, action=action)
        )
    return failures


def _communicate_upload_failures(failures: list[MappingUploadFailure]) -> None:
    msg_start = f"{len(failures)} mapping operation(s) failed."
    logger.error(msg_start)
    print(f"{BACKGROUND_BOLD_RED}{msg_start}{RESET_TO_DEFAULT}")
    messages = []
    failures = sorted(failures, key=lambda x: x.prefixed_iri)
    for failure in failures:
        single_line = [failure.prefixed_iri]
        if failure.mapping_iri:
            single_line.append(f"Could not {failure.action} mapping '{failure.mapping_iri}'")
        else:
            single_line.append(f"Could not {failure.action} mapping")
        single_line.append(f"Problem: {failure.message}")
        messages.append(" | ".join(single_line))
    msg = LIST_MESSAGE_SEPARATOR + LIST_MESSAGE_SEPARATOR.join(messages)
    logger.error(msg)
    print(msg)
    logger.error(RERUN_ADVICE)
    print(f"\n{RERUN_ADVICE}")
