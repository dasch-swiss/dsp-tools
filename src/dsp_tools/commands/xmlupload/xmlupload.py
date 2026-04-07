from __future__ import annotations

from pathlib import Path

from loguru import logger
from rdflib import URIRef
from requests import ReadTimeout
from tqdm import tqdm

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.clients.fuseki_metrics import FusekiMetrics
from dsp_tools.clients.ingest import AssetClient
from dsp_tools.clients.ingest import DspIngestClientLive
from dsp_tools.clients.legal_info_client import LegalInfoClient
from dsp_tools.clients.legal_info_client_live import LegalInfoClientLive
from dsp_tools.clients.list_client import ListGetClient
from dsp_tools.clients.list_client_live import ListGetClientLive
from dsp_tools.clients.project_client_live import ProjectClientLive
from dsp_tools.commands.validate_data.validate_data import validate_parsed_resources
from dsp_tools.commands.xmlupload.exceptions import XmlUploadInterruptedError
from dsp_tools.commands.xmlupload.execute_upload import _upload_stash
from dsp_tools.commands.xmlupload.execute_upload import cleanup_upload
from dsp_tools.commands.xmlupload.execute_upload import upload_copyright_holders
from dsp_tools.commands.xmlupload.handle_errors import handle_keyboard_interrupt
from dsp_tools.commands.xmlupload.handle_errors import handle_permanent_connection_error
from dsp_tools.commands.xmlupload.handle_errors import handle_permanent_timeout_or_keyboard_interrupt
from dsp_tools.commands.xmlupload.handle_errors import handle_upload_error
from dsp_tools.commands.xmlupload.handle_errors import inform_about_resource_creation_failure
from dsp_tools.commands.xmlupload.handle_errors import interrupt_if_indicated
from dsp_tools.commands.xmlupload.handle_errors import tidy_up_resource_creation_idempotent
from dsp_tools.commands.xmlupload.make_rdf_graph.make_resource_and_values import create_resource_with_values
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.lookup_models import XmlReferenceLookups
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import get_processed_resources
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import get_parsed_resources_and_mappers
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import get_stash_and_upload_order
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import check_if_bitstreams_exist
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import validate_iiif_uris
from dsp_tools.commands.xmlupload.resource_create_client import ResourceCreateClient
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import PermanentConnectionError
from dsp_tools.setup.ansi_colors import BOLD_RED
from dsp_tools.setup.ansi_colors import BOLD_YELLOW
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.data_formats.uri_util import is_prod_like_server
from dsp_tools.utils.fuseki_bloating import communicate_fuseki_bloating
from dsp_tools.utils.replace_id_with_iri import use_id2iri_mapping_to_replace_ids
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file


def xmlupload(
    input_file: Path,
    creds: ServerCredentials,
    imgdir: str,
    config: UploadConfig = UploadConfig(),
) -> bool:
    """
    This function reads an XML file and imports the data described in it onto the DSP server.

    Args:
        input_file: path to XML file containing the resources
        creds: the credentials to access the DSP server
        imgdir: the image directory
        config: the configuration for the upload

    Raises:
        BaseError: in case of permanent network or software failure
        InputError: in case of permanent network or software failure, or if the XML file is invalid
        InputError: in case of permanent network or software failure, or if the XML file is invalid

    Returns:
        True if all resources could be uploaded without errors; False if one of the resources could not be
        uploaded because there is an error in it
    """

    root = parse_and_clean_xml_file(input_file)
    shortcode = root.attrib["shortcode"]

    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    config = config.with_server_info(server=creds.server, shortcode=shortcode)
    clients = _get_live_clients(auth, creds, shortcode, imgdir)

    parsed_resources, lookups = get_parsed_resources_and_mappers(root, clients)
    if config.id2iri_file:
        parsed_resources = use_id2iri_mapping_to_replace_ids(parsed_resources, Path(config.id2iri_file))

    is_on_prod_like_server = is_prod_like_server(creds.server)

    validation_ok = _handle_validation(
        parsed_resources=parsed_resources,
        lookups=lookups,
        config=config,
        is_on_prod_like_server=is_on_prod_like_server,
        auth=auth,
        input_file=input_file,
    )
    if not validation_ok:
        return False

    check_if_bitstreams_exist(root, imgdir)
    if not config.skip_iiif_validation:
        validate_iiif_uris(root)

    if not is_on_prod_like_server:
        enable_unknown_license_if_any_are_missing(clients.legal_info_client, parsed_resources)

    processed_resources = get_processed_resources(parsed_resources, lookups, is_on_prod_like_server)

    sorted_resources, stash = get_stash_and_upload_order(processed_resources)
    state = UploadState(
        pending_resources=sorted_resources,
        pending_stash=stash,
        config=config,
    )

    return execute_upload(clients, state)


def _handle_validation(
    parsed_resources: list[ParsedResource],
    lookups: XmlReferenceLookups,
    config: UploadConfig,
    is_on_prod_like_server: bool,
    auth: AuthenticationClient,
    input_file: Path,
) -> bool:
    validation_should_be_skipped = config.skip_validation
    if is_on_prod_like_server and config.skip_validation:
        msg = (
            "You set the flag '--skip-validation' to circumvent the SHACL schema validation. "
            "This means that the upload may fail due to undetected errors. "
            "Do you wish to skip the validation (yes/no)? "
        )
        resp = ""
        while resp not in ["yes", "no"]:
            resp = input(BOLD_RED + msg + RESET_TO_DEFAULT)
        if str(resp) == "no":
            validation_should_be_skipped = False
    if not validation_should_be_skipped:
        ignore_duplicates = config.ignore_duplicate_files_warning
        if is_on_prod_like_server and ignore_duplicates:
            msg = (
                "You set the flag '--ignore-duplicate-files-warning'. "
                "This means that duplicate multimedia files will not be detected. "
                "Are you sure you want to exclude this from the validation? (yes/no)"
            )
            resp = ""
            while resp not in ["yes", "no"]:
                resp = input(BOLD_RED + msg + RESET_TO_DEFAULT)
            if str(resp) == "no":
                ignore_duplicates = False
        v_severity = config.validation_severity
        if is_on_prod_like_server:
            v_severity = ValidationSeverity.INFO
        validation_passed = validate_parsed_resources(
            parsed_resources=parsed_resources,
            authorship_lookup=lookups.authorships,
            permission_ids=list(lookups.permissions.keys()),
            shortcode=config.shortcode,
            config=ValidateDataConfig(
                input_file,
                save_graph_dir=None,
                severity=v_severity,
                ignore_duplicate_files_warning=ignore_duplicates,
                is_on_prod_server=is_on_prod_like_server,
                skip_ontology_validation=config.skip_ontology_validation,
                do_not_request_resource_metadata_from_db=config.do_not_request_resource_metadata_from_db,
            ),
            auth=auth,
        )
        if not validation_passed:
            return False
    else:
        logger.debug("SHACL validation was skipped.")
    return True


def _get_live_clients(
    auth: AuthenticationClient,
    creds: ServerCredentials,
    shortcode: str,
    imgdir: str,
) -> UploadClients:
    ingest_client: AssetClient
    ingest_client = DspIngestClientLive(creds.dsp_ingest_url, auth, shortcode, imgdir)
    list_client: ListGetClient = ListGetClientLive(auth.server, shortcode)
    legal_info_client: LegalInfoClient = LegalInfoClientLive(creds.server, shortcode, auth)
    return UploadClients(
        asset_client=ingest_client,
        list_client=list_client,
        legal_info_client=legal_info_client,
    )


def enable_unknown_license_if_any_are_missing(
    legal_info_client: LegalInfoClient, parsed_resources: list[ParsedResource]
) -> None:
    all_license_infos = [x.file_value.metadata.license_iri for x in parsed_resources if x.file_value]
    if not all(all_license_infos):
        legal_info_client.enable_unknown_license()
        msg = (
            "The files or iiif-uris in your data are missing some legal information. "
            "To facilitate an upload on a test environment we are adding dummy information.\n"
            "In order to be able to use the license 'unknown' in place of missing licenses, "
            "we are enabling it for your project."
        )
        print(BOLD_YELLOW, msg, RESET_TO_DEFAULT)


def execute_upload(clients: UploadClients, upload_state: UploadState) -> bool:
    """Execute an upload from an upload state, and clean up afterwards.

    Args:
        clients: the clients needed for the upload
        upload_state: the initial state of the upload to execute

    Returns:
        True if all resources could be uploaded without errors; False if any resource could not be uploaded
    """
    logger.debug("Start uploading data")
    db_metrics = None
    if clients.legal_info_client.server == "http://0.0.0.0:3333":
        db_metrics = FusekiMetrics()
        db_metrics.try_get_start_size()
    upload_copyright_holders(upload_state.pending_resources, clients.legal_info_client)
    _upload_resources(clients, upload_state)
    if db_metrics is not None:
        db_metrics.try_get_end_size()
        communicate_fuseki_bloating(db_metrics)
    return cleanup_upload(upload_state)


def _upload_resources(clients: UploadClients, upload_state: UploadState) -> None:
    """
    Iterates through all resources and tries to upload them to DSP.
    If a temporary exception occurs, the action is repeated until success,
    and if a permanent exception occurs, the resource is skipped.

    Args:
        clients: the clients needed for the upload
        upload_state: the current state of the upload

    Raises:
        BaseException: in case of an unhandled exception during resource creation
        XmlUploadInterruptedError: if the number of resources created is equal to the interrupt_after value
    """
    project_client = ProjectClientLive(clients.legal_info_client.server, clients.legal_info_client.auth)
    project_iri = project_client.get_project_iri(upload_state.config.shortcode)

    iri_lookup = IRILookups(
        project_iri=URIRef(project_iri),
        id_to_iri=upload_state.iri_resolver,
    )

    con = ConnectionLive(clients.legal_info_client.server, clients.legal_info_client.auth)
    resource_create_client = ResourceCreateClient(
        con=con,
    )
    progress_bar = tqdm(upload_state.pending_resources.copy(), desc="Creating Resources", dynamic_ncols=True)
    try:
        for creation_attempts_of_this_round, resource in enumerate(progress_bar):
            _upload_one_resource(
                upload_state=upload_state,
                resource=resource,
                ingest_client=clients.asset_client,
                resource_create_client=resource_create_client,
                iri_lookups=iri_lookup,
                creation_attempts_of_this_round=creation_attempts_of_this_round,
            )
            progress_bar.set_description(f"Creating Resources (failed: {len(upload_state.failed_uploads)})")
        if upload_state.pending_stash:
            _upload_stash(upload_state, con)
    except XmlUploadInterruptedError as err:
        handle_upload_error(err, upload_state)


def _upload_one_resource(
    upload_state: UploadState,
    resource: ProcessedResource,
    ingest_client: AssetClient,
    resource_create_client: ResourceCreateClient,
    iri_lookups: IRILookups,
    creation_attempts_of_this_round: int,
) -> None:
    media_info = None
    if resource.file_value:
        try:
            ingest_result = ingest_client.get_bitstream_info(resource.file_value)
        except PermanentConnectionError as err:
            handle_permanent_connection_error(err)
        except KeyboardInterrupt:
            handle_keyboard_interrupt()
        if not ingest_result:
            upload_state.failed_uploads.append(resource.res_id)
            return
        media_info = ingest_result

    iri = None
    try:
        serialised_resource = create_resource_with_values(
            resource=resource, bitstream_information=media_info, lookups=iri_lookups
        )
        logger.info(f"Attempting to create resource {resource.res_id} (label: {resource.label})...")
        iri = resource_create_client.create_resource(serialised_resource, resource_has_bitstream=bool(media_info))
    except (TimeoutError, ReadTimeout, KeyboardInterrupt) as err:
        handle_permanent_timeout_or_keyboard_interrupt(err, resource.res_id)
    except PermanentConnectionError as err:
        handle_permanent_connection_error(err)
    except Exception as err:  # noqa: BLE001 (blind-except)
        err_msg = err.message if isinstance(err, BaseError) else None
        inform_about_resource_creation_failure(resource, err_msg)

    try:
        tidy_up_resource_creation_idempotent(upload_state, iri, resource)
        interrupt_if_indicated(upload_state, creation_attempts_of_this_round)
    except KeyboardInterrupt:
        tidy_up_resource_creation_idempotent(upload_state, iri, resource)
        handle_keyboard_interrupt()
