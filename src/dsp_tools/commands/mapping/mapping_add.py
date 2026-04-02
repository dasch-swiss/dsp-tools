import time
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
from dsp_tools.commands.mapping.models import MappingConfig
from dsp_tools.commands.mapping.models import MappingInfo
from dsp_tools.commands.mapping.models import MappingUploadFailure
from dsp_tools.commands.mapping.models import PrefixResolutionProblem
from dsp_tools.commands.mapping.models import ResolvedClassMapping
from dsp_tools.commands.mapping.models import ResolvedPropertyMapping
from dsp_tools.commands.mapping.parse_excel import parse_mapping_excel
from dsp_tools.commands.mapping.resolve_parsed_mappings import resolve_parsed_mappings
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_GREEN
from dsp_tools.setup.ansi_colors import BACKGROUND_BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.data_formats.iri_util import make_dsp_ontology_prefix
from dsp_tools.utils.request_utils import ResponseCodeAndText
from dsp_tools.utils.request_utils import should_retry_request

RETRY_SLEEP_SECONDS = 5
LIST_MESSAGE_SEPARATOR = "\n    - "


def mapping_add(info: MappingInfo) -> bool:
    logger.info(f"Starting mapping add for ontology '{info.config.ontology}' (shortcode {info.config.shortcode})")

    parsed_excel, prefix_lookup = parse_mapping_excel(info.config.excel_file)
    ontology_namespace = make_dsp_ontology_prefix(info.server.server, info.config.shortcode, info.config.ontology)
    resolved_mappings, problems = resolve_parsed_mappings(parsed_excel, prefix_lookup, ontology_namespace)

    if problems:
        _communicate_parsing_problems(problems)
        return False

    auth = AuthenticationClientLive(
        server=info.server.server,
        email=info.server.user,
        password=info.server.password,
    )
    ontology_iri = ontology_namespace.rstrip("#")
    _check_if_project_and_ontology_exists(auth, info.config, ontology_iri)

    encoded_ontology_iri = quote_plus(ontology_iri)
    client = MappingClientLive(server=auth.server, encoded_ontology_iri=encoded_ontology_iri, auth=auth)

    failures = _add_classes_mappings(client, resolved_mappings.classes)
    prop_failures = _add_properties_mappings(client, resolved_mappings.properties)
    failures.extend(prop_failures)

    if failures:
        _communicate_upload_failures(failures)
        return False

    print(f"{BACKGROUND_BOLD_GREEN}All mappings were added successfully.{RESET_TO_DEFAULT}")
    return True


def _communicate_parsing_problems(problem_list: list[PrefixResolutionProblem]) -> None:
    err_found_msg = f"{len(problem_list)} mapping properties or classes could not be correctly resolved."
    logger.error(err_found_msg)
    print(f"{BACKGROUND_BOLD_RED}{err_found_msg}{RESET_TO_DEFAULT}")
    problem_list = sorted(problem_list, key=lambda x: x.entity_name)
    problem_str_list = [
        f"Ontology class/property '{p.entity_name}' | Problematic mapping: '{p.input_value}' | Problem: {p.problem}"
        for p in problem_list
    ]
    problem_str = LIST_MESSAGE_SEPARATOR + LIST_MESSAGE_SEPARATOR.join(problem_str_list)
    logger.error(problem_str)
    print(problem_str)


def _check_if_project_and_ontology_exists(
    auth: AuthenticationClient, mapping_config: MappingConfig, ontology_iri: str
) -> None:
    logger.debug("Check if the project and ontology exists on the server.")
    project_client = ProjectClientLive(auth.server, auth)
    # If the project does not exist this will raise an error which we will let escalate,
    # this is for a more nuanced error message.
    project_client.get_project_iri(mapping_config.shortcode)

    onto_client = OntologyGetClientLive(api_url=auth.server, shortcode=mapping_config.shortcode)
    # If no ontologies are found this will raise an error which we let escalate.
    _, ontology_iris = onto_client.get_ontologies()
    if ontology_iri not in ontology_iris:
        raise OntologyReferencedNotFoundError(mapping_config.shortcode, mapping_config.ontology)


def _add_classes_mappings(
    client: MappingClient, classes_mapping: list[ResolvedClassMapping]
) -> list[MappingUploadFailure]:
    failures: list[MappingUploadFailure] = []
    progress_bar = tqdm(classes_mapping, desc="    Adding mapping to classes", dynamic_ncols=True)
    logger.debug("Adding mapping to classes")
    for cls in progress_bar:
        response = client.put_class_mapping(cls.iri, cls.mapping_iris)
        # happy path
        if response is None:
            continue
        # retry if it is a retriable status code
        if should_retry_request(response):
            logger.warning(f"Retrying to add mapping for class '{cls.iri}' in {RETRY_SLEEP_SECONDS} seconds.")
            time.sleep(RETRY_SLEEP_SECONDS)
            response = client.put_class_mapping(cls.iri, cls.mapping_iris)
            if response is not None:
                logger.error(f"Unable to add mapping for class '{cls.iri}' after retrying.")
                failures.extend(_get_correct_user_message_for_non_ok_response(cls.iri, response))
        # non retriable error
        else:
            logger.error(f"Unable to add mapping for class '{cls.iri}'.")
            failures.extend(_get_correct_user_message_for_non_ok_response(cls.iri, response))
    return failures


def _add_properties_mappings(
    client: MappingClient, properties_mapping: list[ResolvedPropertyMapping]
) -> list[MappingUploadFailure]:
    failures: list[MappingUploadFailure] = []
    progress_bar = tqdm(properties_mapping, desc="    Adding mapping to properties", dynamic_ncols=True)
    logger.debug("Adding mapping to properties")
    for prop in progress_bar:
        response = client.put_property_mapping(prop.iri, prop.mapping_iris)
        # happy path
        if response is None:
            continue
        # retry if it is a retriable status code
        if should_retry_request(response):
            logger.warning(f"Retrying to add mapping for property '{prop.iri}' in {RETRY_SLEEP_SECONDS} seconds.")
            time.sleep(RETRY_SLEEP_SECONDS)
            response = client.put_property_mapping(prop.iri, prop.mapping_iris)
            if response is not None:
                logger.error(f"Unable to add mapping for property '{prop.iri}' after retrying.")
                failures.extend(_get_correct_user_message_for_non_ok_response(prop.iri, response))
        # non retriable error
        else:
            logger.error(f"Unable to add mapping for property '{prop.iri}'.")
            failures.extend(_get_correct_user_message_for_non_ok_response(prop.iri, response))
    return failures


def _get_correct_user_message_for_non_ok_response(
    iri: str, response_code_text: ResponseCodeAndText
) -> list[MappingUploadFailure]:
    if response_code_text.status_code == HTTPStatus.BAD_REQUEST:
        return _get_correct_bad_requests_message(iri, response_code_text)
    msg = (
        f"Unexpected error while adding mapping for class/property '{iri}'. "
        f"Original status code: {response_code_text.status_code}\nOriginal message: {response_code_text.text}"
    )
    return [MappingUploadFailure(iri=iri, mapping_iri=None, message=msg)]


def _get_correct_bad_requests_message(iri: str, response_code_text: ResponseCodeAndText) -> list[MappingUploadFailure]:
    if not response_code_text.v3_errors:
        return [MappingUploadFailure(iri=iri, mapping_iri=None, message=response_code_text.text)]
    failures = []
    for v3_err in response_code_text.v3_errors:
        mapping_iri = None
        match v3_err.error_code:
            case "class_not_found":
                msg = f"The class '{iri}' was not found in the ontology on the server."
            case "property_not_found":
                msg = f"The property '{iri}' was not found in the ontology on the server."
            case "invalid_ontology_mapping_iri":
                mapping_iri = v3_err.details.get("iri")
                msg = f"The mapping IRI '{mapping_iri}' is not a valid external ontology IRI."
            case _:
                details_str = ", ".join(f"{k}={v}" for k, v in v3_err.details.items()) if v3_err.details else ""
                msg = f"{v3_err.message}" + (f" ({details_str})" if details_str else "")
        failures.append(MappingUploadFailure(iri=iri, mapping_iri=mapping_iri, message=msg))
    return failures


def _communicate_upload_failures(failures: list[MappingUploadFailure]) -> None:
    msg_start = f"{len(failures)} mapping(s) could not be added"
    logger.error(msg_start)
    print(f"{BACKGROUND_BOLD_RED}{msg_start}{RESET_TO_DEFAULT}")
    messages = []
    failures = sorted(failures, key=lambda x: x.iri)
    for failure in failures:
        single_line = [f"Ontology class/property '{failure.iri}'"]
        if failure.mapping_iri:
            single_line.append(f"Mapping '{failure.mapping_iri}'")
        single_line.append(f"Problem: {failure.message}")
        messages.append(" | ".join(single_line))
    msg = LIST_MESSAGE_SEPARATOR + LIST_MESSAGE_SEPARATOR.join(messages)
    logger.error(msg)
    print(msg)
