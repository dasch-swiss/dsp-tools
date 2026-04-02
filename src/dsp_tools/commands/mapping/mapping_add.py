import time
from http import HTTPStatus
from urllib.parse import quote_plus

from loguru import logger
from tqdm import tqdm

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.exceptions import FatalNonOkApiResponseCode
from dsp_tools.clients.exceptions import ProjectNotFoundError
from dsp_tools.clients.exceptions import ProjectOntologyNotFound
from dsp_tools.clients.mapping_client import MappingClient
from dsp_tools.clients.mapping_client_live import MappingClientLive
from dsp_tools.clients.ontology_get_client_live import OntologyGetClientLive
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
from dsp_tools.utils.request_utils import should_retry_on_status_code

RETRY_SLEEP_SECONDS = 5


def mapping_add(info: MappingInfo) -> bool:
    logger.info(f"Starting mapping add for ontology '{info.config.ontology}' (shortcode {info.config.shortcode})")

    parsed_excel, prefix_lookup = parse_mapping_excel(info.config.excel_file)

    ontology_namespace = make_dsp_ontology_prefix(info.server.server, info.config.shortcode, info.config.ontology)

    resolved_mappings, problems = resolve_parsed_mappings(parsed_excel, prefix_lookup, ontology_namespace)

    if problems:
        _communicate_parsing_problems(problems)
        return False

    ontology_iri = ontology_namespace.rstrip("#")
    if not _ontology_exists(info.server.server, info.config.shortcode, ontology_iri):
        print(
            f"{BACKGROUND_BOLD_RED}The ontology '{info.config.ontology}' was not found on the server.{RESET_TO_DEFAULT}"
        )
        return False

    encoded_ontology_iri = quote_plus(ontology_iri)
    auth = AuthenticationClientLive(
        server=info.server.server,
        email=info.server.user,
        password=info.server.password,
    )
    client = MappingClientLive(server=auth.server, encoded_ontology_iri=encoded_ontology_iri, auth=auth)

    failures = _add_classes_mappings(client, resolved_mappings.classes)
    prop_failures = _add_properties_mappings(client, resolved_mappings.properties)
    failures.extend(prop_failures)

    if not failures:
        print(f"{BACKGROUND_BOLD_GREEN}All mappings were added successfully.")
        return True

    _communicate_upload_failures(failures)
    return False


def _ontology_exists(server: str, shortcode: str, ontology_iri: str) -> bool:
    client = OntologyGetClientLive(api_url=server, shortcode=shortcode)
    try:
        _, ontology_iris = client.get_ontologies()
    except ProjectOntologyNotFound:
        return False
    except FatalNonOkApiResponseCode as e:
        raise ProjectNotFoundError(f"The project with shortcode '{shortcode}' could not be found on the server.") from e
    return ontology_iri in ontology_iris


def _communicate_parsing_problems(problem_list: list[PrefixResolutionProblem]) -> None:
    err_found_msg = f"{len(problem_list)} mapping properties or classes could not be correctly resolved."
    logger.error(err_found_msg)
    print(f"{BACKGROUND_BOLD_RED}{err_found_msg}{RESET_TO_DEFAULT}")
    problem_str_list = [
        f"Ontology class/property '{p.entity_name}' | Problematic mapping: '{p.input_value}' | Problem: {p.problem}"
        for p in problem_list
    ]
    problem_str = "\n    - " + "\n    - ".join(problem_str_list)
    logger.error(problem_str)
    print(problem_str)


def _add_classes_mappings(
    client: MappingClient, classes_mapping: list[ResolvedClassMapping]
) -> list[MappingUploadFailure]:
    failures: list[MappingUploadFailure] = []
    progress_bar = tqdm(classes_mapping, desc="    Adding mapping to classes", dynamic_ncols=True)
    logger.debug("Adding mapping to classes")
    for cls in progress_bar:
        response = client.put_class_mapping(cls.iri, cls.mapping_iris)
        if response is None:
            continue
        if should_retry_on_status_code(response.status_code):
            logger.debug("Retrying class mapping for '%s' after status %s", cls.iri, response.status_code)
            time.sleep(RETRY_SLEEP_SECONDS)
            response = client.put_class_mapping(cls.iri, cls.mapping_iris)
        if response is not None:
            failures.extend(_deal_with_non_ok_response(cls.iri, response))
    return failures


def _add_properties_mappings(
    client: MappingClient, properties_mapping: list[ResolvedPropertyMapping]
) -> list[MappingUploadFailure]:
    failures: list[MappingUploadFailure] = []
    progress_bar = tqdm(properties_mapping, desc="    Adding mapping to properties", dynamic_ncols=True)
    logger.debug("Adding mapping to properties")
    for prop in progress_bar:
        response = client.put_property_mapping(prop.iri, prop.mapping_iris)
        if response is None:
            continue
        if should_retry_on_status_code(response.status_code):
            logger.debug("Retrying property mapping for '%s' after status %s", prop.iri, response.status_code)
            time.sleep(RETRY_SLEEP_SECONDS)
            response = client.put_property_mapping(prop.iri, prop.mapping_iris)
        if response is not None:
            failures.extend(_deal_with_non_ok_response(prop.iri, response))
    return failures


def _deal_with_non_ok_response(iri: str, response_code_text: ResponseCodeAndText) -> list[MappingUploadFailure]:
    if response_code_text.status_code == HTTPStatus.BAD_REQUEST:
        return _deal_with_bad_request(iri, response_code_text)
    msg = f"Unexpected server response {response_code_text.status_code} for IRI '{iri}': {response_code_text.text}"
    logger.warning(msg)
    return [MappingUploadFailure(iri=iri, mapping_iri=None, message=msg)]


def _deal_with_bad_request(iri: str, response_code_text: ResponseCodeAndText) -> list[MappingUploadFailure]:
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
                logger.warning("Unknown v3 error code '%s' for IRI '%s': %s", v3_err.error_code, iri, msg)
        failures.append(MappingUploadFailure(iri=iri, mapping_iri=mapping_iri, message=msg))
    return failures


def _communicate_upload_failures(failures: list[MappingUploadFailure]) -> None:
    print(f"{BACKGROUND_BOLD_RED}Some mappings could not be uploaded.{RESET_TO_DEFAULT}")
    messages = []
    for failure in failures:
        if failure.mapping_iri:
            messages.append(f"Ontology IRI '{failure.iri}', mapping '{failure.mapping_iri}': {failure.message}")
        else:
            messages.append(f"Ontology IRI '{failure.iri}': {failure.message}")
    msg = "\n    - " + "\n    - ".join(messages)
    logger.warning(msg)
    print(msg)
