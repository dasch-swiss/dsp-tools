from __future__ import annotations

from pathlib import Path

from loguru import logger

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.clients.authentication_client import AuthenticationClient
from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.ingest import AssetClient
from dsp_tools.clients.ingest import DspIngestClientLive
from dsp_tools.clients.legal_info_client import LegalInfoClient
from dsp_tools.clients.legal_info_client_live import LegalInfoClientLive
from dsp_tools.clients.list_client import ListGetClient
from dsp_tools.clients.list_client_live import ListGetClientLive
from dsp_tools.commands.validate_data.validate_data import validate_parsed_resources
from dsp_tools.commands.xmlupload.execute_upload import enable_unknown_license_if_any_are_missing
from dsp_tools.commands.xmlupload.execute_upload import execute_upload
from dsp_tools.commands.xmlupload.models.lookup_models import XmlReferenceLookups
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import get_processed_resources
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import get_parsed_resources_and_mappers
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import get_stash_and_upload_order
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import check_if_bitstreams_exist
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import validate_iiif_uris
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.setup.ansi_colors import BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.data_formats.uri_util import is_prod_like_server
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
