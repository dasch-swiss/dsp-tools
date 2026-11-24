from __future__ import annotations

from pathlib import Path

from loguru import logger
from lxml import etree
from rdflib import URIRef

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.cli.args import ValidateDataConfig
from dsp_tools.cli.args import ValidationSeverity
from dsp_tools.commands.ingest_xmlupload.bulk_import.mint_iris import mint_resource_iris
from dsp_tools.commands.ingest_xmlupload.bulk_import.payload_files import make_payload_files
from dsp_tools.commands.ingest_xmlupload.bulk_import.payload_files import write_minted_mapping
from dsp_tools.commands.ingest_xmlupload.bulk_import.run_import import run_import
from dsp_tools.commands.ingest_xmlupload.bulk_import.write_payload import write_payload_file
from dsp_tools.commands.ingest_xmlupload.create_resources.apply_ingest_id import get_mapping_dict_from_file
from dsp_tools.commands.ingest_xmlupload.create_resources.apply_ingest_id import replace_filepath_with_internal_filename
from dsp_tools.commands.ingest_xmlupload.exceptions import IngestIdForFileNotFoundError
from dsp_tools.commands.validate_data.validate_data import validate_parsed_resources
from dsp_tools.commands.xmlupload.execute_upload import upload_copyright_holders
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.lookup_models import XmlReferenceLookups
from dsp_tools.commands.xmlupload.models.upload_clients import BulkIngestedAssetClient
from dsp_tools.commands.xmlupload.models.upload_clients import UploadClients
from dsp_tools.commands.xmlupload.prepare_xml_input.get_processed_resources import get_processed_resources
from dsp_tools.commands.xmlupload.prepare_xml_input.prepare_xml_input import get_parsed_resources_and_mappers
from dsp_tools.commands.xmlupload.prepare_xml_input.read_validate_xml_file import validate_iiif_uris
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.xmlupload import resolve_project_default_authorship
from dsp_tools.setup.ansi_colors import BOLD_RED
from dsp_tools.setup.ansi_colors import RESET_TO_DEFAULT
from dsp_tools.utils.data_formats.uri_util import is_prod_like_server
from dsp_tools.utils.dsp_user_account_check import check_on_behalf_of_user_for_data_import
from dsp_tools.utils.interactive import prompt_until_valid_answer
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.parse_clean_validate_xml import parse_and_clean_xml_file
from dsp_vre.clients import AuthenticationClient
from dsp_vre.clients import LegalInfoClientLive
from dsp_vre.clients.authentication_client_live import AuthenticationClientLive
from dsp_vre.clients.data_import_client_live import DataImportClientLive
from dsp_vre.clients.list_client_live import ListGetClientLive
from dsp_vre.clients.project_client import ProjectClient
from dsp_vre.clients.project_client_live import ProjectClientLive


def ingest_xmlupload(
    xml_file: Path,
    creds: ServerCredentials,
    on_behalf_of_user: str,
    skip_validation: bool = False,
    skip_ontology_validation: bool = False,
    skip_iiif_validation: bool = False,
) -> bool:
    """
    This function reads an XML file
    and imports the data described in it onto the DSP server as one bulk data import.
    Before using this function,
    the multimedia files must be ingested on the DSP server.
    A mapping file with the internal IDs of the multimedia files must also be provided.

    Args:
        xml_file: path to XML file containing the resources
        creds: credentials of a system admin to access the DSP server
        on_behalf_of_user: email or username of the user who becomes the creator of the resources
        skip_validation: skip the SHACL validation
        skip_ontology_validation: skip the ontology validation
        skip_iiif_validation: do not check if the IIIF URIs can be reached

    Returns:
        True if the bulk import completed; False if the validation failed or the import failed

    Raises:
        InputError: if any media was not uploaded or uploaded media was not referenced.
    """
    root = parse_and_clean_xml_file(xml_file)
    shortcode = root.attrib["shortcode"]
    root = _replace_filepaths_with_internal_filename_from_ingest(root, shortcode)

    auth = AuthenticationClientLive(server=creds.server, email=creds.user, password=creds.password)
    project_client: ProjectClient = ProjectClientLive(creds.server, auth)
    project_iri = project_client.get_project_iri(shortcode)
    check_on_behalf_of_user_for_data_import(
        on_behalf_of_user, project_client.get_project_shortname(shortcode), creds.server
    )
    project_default_authorship = resolve_project_default_authorship(root, project_client, shortcode)

    config = UploadConfig(
        skip_iiif_validation=skip_iiif_validation,
        skip_validation=skip_validation,
        skip_ontology_validation=skip_ontology_validation,
    ).with_server_info(server=creds.server, shortcode=shortcode)
    clients = _get_live_clients(config, auth)
    parsed_resources, lookups = get_parsed_resources_and_mappers(root, clients)

    is_on_prod_like_server = is_prod_like_server(creds.server)
    if not _validation_should_be_skipped(config, is_on_prod_like_server):
        if not _validate(parsed_resources, lookups, config, xml_file, is_on_prod_like_server, auth):
            return False
    else:
        logger.debug("SHACL validation was skipped.")

    if not config.skip_iiif_validation:
        validate_iiif_uris(root)

    processed_resources = get_processed_resources(
        parsed_resources, lookups, is_on_prod_like_server, project_default_authorship
    )
    upload_copyright_holders(processed_resources, clients.legal_info_client)

    resolver = mint_resource_iris(processed_resources, shortcode)
    files = make_payload_files(config.diagnostics.server_as_foldername, shortcode)
    write_minted_mapping(resolver.lookup, files.id2iri)
    write_payload_file(processed_resources, IRILookups(URIRef(project_iri), resolver), files.payload)

    return run_import(
        DataImportClientLive(creds.server, project_iri, auth),
        files,
        on_behalf_of_user,
        shortcode,
        resolver.lookup,
        config.diagnostics,
    )


def _validation_should_be_skipped(config: UploadConfig, is_on_prod_like_server: bool) -> bool:
    if not config.skip_validation:
        return False
    if not is_on_prod_like_server:
        return True
    msg = (
        "You set the flag '--skip-validation' to circumvent the SHACL schema validation. "
        "This means that the upload may fail due to undetected errors. "
        "Do you wish to skip the validation (yes/no)? "
    )
    resp = prompt_until_valid_answer(
        prompt=BOLD_RED + msg + RESET_TO_DEFAULT,
        valid_answers=["yes", "no"],
        non_interactive_answer="yes",
        non_interactive_notice=BOLD_RED
        + "Skipping validation as requested via '--skip-validation' (non-interactive session)."
        + RESET_TO_DEFAULT,
    )
    return resp != "no"


def _validate(
    parsed_resources: list[ParsedResource],
    lookups: XmlReferenceLookups,
    config: UploadConfig,
    xml_file: Path,
    is_on_prod_like_server: bool,
    auth: AuthenticationClient,
) -> bool:
    severity = ValidationSeverity.INFO if is_on_prod_like_server else config.validation_severity
    return validate_parsed_resources(
        parsed_resources=parsed_resources,
        authorship_lookup=lookups.authorships,
        permission_ids=list(lookups.permissions.keys()),
        shortcode=config.shortcode,
        config=ValidateDataConfig(
            xml_file,
            save_graph_dir=None,
            severity=severity,
            ignore_duplicate_files_warning=True,
            is_on_prod_server=is_on_prod_like_server,
            skip_ontology_validation=config.skip_ontology_validation,
            do_not_request_resource_metadata_from_db=True,
        ),
        auth=auth,
    )


def _replace_filepaths_with_internal_filename_from_ingest(root: etree._Element, shortcode: str) -> etree._Element:
    orig_path_2_asset_id = get_mapping_dict_from_file(shortcode)
    root, ingest_info = replace_filepath_with_internal_filename(root, orig_path_2_asset_id)
    if ok := ingest_info.ok_msg():
        print(ok)
        logger.info(ok)
    else:
        err_msg = ingest_info.execute_error_protocol()
        raise IngestIdForFileNotFoundError(err_msg)
    return root


def _get_live_clients(config: UploadConfig, auth: AuthenticationClient) -> UploadClients:
    ingest_client = BulkIngestedAssetClient()
    list_client = ListGetClientLive(auth.server, config.shortcode)
    legal_info_client = LegalInfoClientLive(config.server, config.shortcode, auth)
    return UploadClients(ingest_client, list_client, legal_info_client)
