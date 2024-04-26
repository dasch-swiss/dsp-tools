from __future__ import annotations

import pickle
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any

from loguru import logger
from lxml import etree

from dsp_tools.commands.xmlupload.check_consistency_with_ontology import do_xml_consistency_check_with_ontology
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.list_client import ListClient
from dsp_tools.commands.xmlupload.list_client import ListClientLive
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.sipi import Sipi
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.models.xmlpermission import XmlPermission
from dsp_tools.commands.xmlupload.models.xmlresource import BitstreamInfo
from dsp_tools.commands.xmlupload.models.xmlresource import XMLResource
from dsp_tools.commands.xmlupload.ontology_client import OntologyClientLive
from dsp_tools.commands.xmlupload.project_client import ProjectClient
from dsp_tools.commands.xmlupload.project_client import ProjectClientLive
from dsp_tools.commands.xmlupload.read_validate_xml_file import validate_and_parse_xml_file
from dsp_tools.commands.xmlupload.resource_create_client import ResourceCreateClient
from dsp_tools.commands.xmlupload.resource_multimedia import handle_media_info
from dsp_tools.commands.xmlupload.stash.stash_circular_references import identify_circular_references
from dsp_tools.commands.xmlupload.stash.stash_circular_references import stash_circular_references
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.commands.xmlupload.stash.upload_stashed_resptr_props import upload_stashed_resptr_props
from dsp_tools.commands.xmlupload.stash.upload_stashed_xml_texts import upload_stashed_xml_texts
from dsp_tools.commands.xmlupload.upload_config import UploadConfig
from dsp_tools.commands.xmlupload.write_diagnostic_info import write_id2iri_mapping
from dsp_tools.models.custom_warnings import GeneralDspToolsWarning
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import PermanentTimeOutError
from dsp_tools.models.exceptions import UserError
from dsp_tools.models.exceptions import XmlUploadInterruptedError
from dsp_tools.models.projectContext import ProjectContext
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive
from dsp_tools.utils.json_ld_util import get_json_ld_context_for_project
from dsp_tools.utils.logger_config import logger_savepath


def xmlupload(
    input_file: str | Path | etree._ElementTree[Any],
    server: str,
    user: str,
    password: str,
    imgdir: str,
    sipi: str,
    config: UploadConfig = UploadConfig(),
) -> bool:
    """
    This function reads an XML file and imports the data described in it onto the DSP server.

    Args:
        input_file: path to XML file containing the resources, or the XML tree itself
        server: the DSP server where the data should be imported
        user: the user (e-mail) with which the data should be imported
        password: the password of the user with which the data should be imported
        imgdir: the image directory
        sipi: the sipi instance to be used
        config: the upload configuration

    Raises:
        BaseError: in case of permanent network or software failure
        UserError: in case of permanent network or software failure, or if the XML file is invalid
        InputError: in case of permanent network or software failure, or if the XML file is invalid

    Returns:
        True if all resources could be uploaded without errors; False if one of the resources could not be
        uploaded because there is an error in it
    """

    con = ConnectionLive(server)
    con.login(user, password)
    sipi_con = ConnectionLive(sipi, token=con.get_token())
    sipi_server = Sipi(sipi_con)

    default_ontology, root, shortcode = validate_and_parse_xml_file(
        input_file=input_file,
        imgdir=imgdir,
        preprocessing_done=config.media_previously_uploaded,
    )

    config = config.with_server_info(
        server=server,
        shortcode=shortcode,
    )

    ontology_client = OntologyClientLive(
        con=con,
        shortcode=shortcode,
        default_ontology=default_ontology,
    )
    do_xml_consistency_check_with_ontology(onto_client=ontology_client, root=root)

    resources, permissions_lookup, stash = _prepare_upload(
        root=root,
        con=con,
        default_ontology=default_ontology,
    )

    project_client: ProjectClient = ProjectClientLive(con, config.shortcode)
    list_client: ListClient = ListClientLive(con, project_client.get_project_iri())
    upload_state = UploadState(resources, [], IriResolver(), stash, config, permissions_lookup)

    nonapplied_stash = upload_resources(
        upload_state=upload_state,
        imgdir=imgdir,
        sipi_server=sipi_server,
        project_client=project_client,
        list_client=list_client,
    )

    return cleanup_upload(upload_state.iri_resolver, config, upload_state.failed_uploads, nonapplied_stash)


def cleanup_upload(
    iri_resolver: IriResolver,
    config: UploadConfig,
    failed_uploads: list[str],
    nonapplied_stash: Stash | None,
) -> bool:
    """
    Write the id2iri mapping to a file and print a message to the console.

    Args:
        iri_resolver: mapping from internal IDs to IRIs
        config: the upload configuration
        failed_uploads: resources that caused an error when uploading to DSP
        nonapplied_stash: the stash items that could not be reapplied

    Returns:
        success status (deduced from failed_uploads)
    """
    write_id2iri_mapping(iri_resolver.lookup, config.diagnostics)
    if not failed_uploads and not nonapplied_stash:
        success = True
        print(f"{datetime.now()}: All resources have successfully been uploaded.")
        logger.info("All resources have successfully been uploaded.")
    else:
        success = False
        if failed_uploads:
            print(f"\n{datetime.now()}: WARNING: Could not upload the following resources: {failed_uploads}\n")
            print(f"For more information, see the log file: {logger_savepath}\n")
            logger.warning(f"Could not upload the following resources: {failed_uploads}")
        if nonapplied_stash:
            print(f"\n{datetime.now()}: WARNING: Could not reapply the following stash items: {nonapplied_stash}\n")
            print(f"For more information, see the log file: {logger_savepath}\n")
            logger.warning(f"Could not reapply the following stash items: {nonapplied_stash}")

    config.diagnostics.save_location.unlink(missing_ok=True)
    return success


def _prepare_upload(
    root: etree._Element,
    con: Connection,
    default_ontology: str,
) -> tuple[list[XMLResource], dict[str, Permissions], Stash | None]:
    logger.info("Checking resources for circular references...")
    print(f"{datetime.now()}: Checking resources for circular references...")
    stash_lookup, upload_order = identify_circular_references(root)
    logger.info("Get data from XML...")
    resources, permissions_lookup = _get_data_from_xml(
        con=con,
        root=root,
        default_ontology=default_ontology,
    )
    sorting_lookup = {res.res_id: res for res in resources}
    resources = [sorting_lookup[res_id] for res_id in upload_order]
    logger.info("Stashing circular references...")
    print(f"{datetime.now()}: Stashing circular references...")
    stash = stash_circular_references(resources, stash_lookup, permissions_lookup)
    return resources, permissions_lookup, stash


def upload_resources(
    upload_state: UploadState,
    imgdir: str,
    sipi_server: Sipi,
    project_client: ProjectClient,
    list_client: ListClient,
) -> Stash | None:
    """
    Actual upload of all resources to DSP.

    Args:
        upload_state: the current state of the upload
        imgdir: folder containing the multimedia files
        sipi_server: Sipi instance
        project_client: a client for HTTP communication with the DSP-API
        list_client: a client for HTTP communication with the DSP-API

    Returns:
        the stash items that could not be reapplied.
    """
    try:
        _upload_resources(
            upload_state=upload_state,
            imgdir=imgdir,
            sipi_server=sipi_server,
            project_client=project_client,
            list_client=list_client,
        )
        if not upload_state.pending_stash:
            return None
        return _upload_stash(
            stash=upload_state.pending_stash,
            iri_resolver=upload_state.iri_resolver,
            project_client=project_client,
        )
    except BaseException as err:  # noqa: BLE001 (blind-except)
        # The forseeable errors are already handled by failed_uploads
        # Here we catch the unforseeable exceptions, incl. keyboard interrupt.
        _handle_upload_error(err, upload_state)
        return None


def _get_data_from_xml(
    con: Connection,
    root: etree._Element,
    default_ontology: str,
) -> tuple[list[XMLResource], dict[str, Permissions]]:
    proj_context = _get_project_context_from_server(connection=con)
    permissions = _extract_permissions_from_xml(root, proj_context)
    resources = _extract_resources_from_xml(root, default_ontology)
    permissions_lookup = {name: perm.get_permission_instance() for name, perm in permissions.items()}
    return resources, permissions_lookup


def _upload_stash(
    stash: Stash,
    iri_resolver: IriResolver,
    project_client: ProjectClient,
) -> Stash | None:
    if stash.standoff_stash:
        nonapplied_standoff = upload_stashed_xml_texts(
            iri_resolver=iri_resolver,
            con=project_client.con,
            stashed_xml_texts=stash.standoff_stash,
        )
    else:
        nonapplied_standoff = None
    context = get_json_ld_context_for_project(project_client.get_ontology_name_dict())
    if stash.link_value_stash:
        nonapplied_resptr_props = upload_stashed_resptr_props(
            iri_resolver=iri_resolver,
            con=project_client.con,
            stashed_resptr_props=stash.link_value_stash,
            context=context,
        )
    else:
        nonapplied_resptr_props = None
    return Stash.make(nonapplied_standoff, nonapplied_resptr_props)


def _get_project_context_from_server(connection: Connection) -> ProjectContext:
    """
    This function retrieves the project context previously uploaded on the server (json file)

    Args:
        connection: connection to the server

    Returns:
        Project context

    Raises:
        UserError: If the project was not previously uploaded on the server
    """
    try:
        proj_context = ProjectContext(con=connection)
    except BaseError:
        logger.opt(exception=True).error("Unable to retrieve project context from DSP server")
        raise UserError("Unable to retrieve project context from DSP server") from None
    return proj_context


def _extract_permissions_from_xml(root: etree._Element, proj_context: ProjectContext) -> dict[str, XmlPermission]:
    permission_ele = list(root.iter(tag="permissions"))
    permissions = [XmlPermission(permission, proj_context) for permission in permission_ele]
    return {permission.permission_id: permission for permission in permissions}


def _extract_resources_from_xml(root: etree._Element, default_ontology: str) -> list[XMLResource]:
    resources = list(root.iter(tag="resource"))
    return [XMLResource(res, default_ontology) for res in resources]


def _upload_resources(
    upload_state: UploadState,
    imgdir: str,
    sipi_server: Sipi,
    project_client: ProjectClient,
    list_client: ListClient,
) -> None:
    """
    Iterates through all resources and tries to upload them to DSP.
    If a temporary exception occurs, the action is repeated until success,
    and if a permanent exception occurs, the resource is skipped.

    Args:
        upload_state: the current state of the upload
        imgdir: folder containing the multimedia files
        sipi_server: Sipi instance
        project_client: a client for HTTP communication with the DSP-API
        list_client: a client for HTTP communication with the DSP-API

    Raises:
        BaseException: in case of an unhandled exception during resource creation
        XmlUploadInterruptedError: if the number of resources created is equal to the interrupt_after value
    """
    project_iri = project_client.get_project_iri()
    json_ld_context = get_json_ld_context_for_project(project_client.get_ontology_name_dict())
    listnode_lookup = list_client.get_list_node_id_to_iri_lookup()

    resource_create_client = ResourceCreateClient(
        con=project_client.con,
        project_iri=project_iri,
        iri_resolver=upload_state.iri_resolver,
        json_ld_context=json_ld_context,
        permissions_lookup=upload_state.permissions_lookup,
        listnode_lookup=listnode_lookup,
        media_previously_ingested=upload_state.config.media_previously_uploaded,
    )
    previous_successful = len(upload_state.iri_resolver.lookup)
    previous_failed = len(upload_state.failed_uploads)
    upcoming = len(upload_state.pending_resources)
    total_num_of_resources = previous_successful + previous_failed + upcoming

    for creation_attempts_of_this_round, resource in enumerate(upload_state.pending_resources.copy()):
        _upload_one_resource(
            upload_state=upload_state,
            resource=resource,
            imgdir=imgdir,
            sipi_server=sipi_server,
            resource_create_client=resource_create_client,
            total_num_of_resources=total_num_of_resources,
            creation_attempts_of_this_round=creation_attempts_of_this_round,
        )


def _upload_one_resource(
    upload_state: UploadState,
    resource: XMLResource,
    imgdir: str,
    sipi_server: Sipi,
    resource_create_client: ResourceCreateClient,
    total_num_of_resources: int,
    creation_attempts_of_this_round: int,
) -> None:
    _compute_counter_info_and_interrupt(upload_state, total_num_of_resources, creation_attempts_of_this_round)
    success, media_info = handle_media_info(
        resource, upload_state.config.media_previously_uploaded, sipi_server, imgdir, upload_state.permissions_lookup
    )
    if not success:
        upload_state.failed_uploads.append(resource.res_id)
        return

    try:
        iri, label = _create_resource(resource, media_info, resource_create_client)
    except (PermanentTimeOutError, KeyboardInterrupt) as err:
        warnings.warn(GeneralDspToolsWarning(f"{type(err).__name__}: Tidying up, then exit..."))
        msg = (
            f"There was a {type(err).__name__} while trying to create resource '{resource.res_id}'.\n"
            f"It is unclear if the resource '{resource.res_id}' was created successfully or not.\n"
            f"Please check manually in the DSP-APP or DB.\n"
            f"In case of successful creation, call 'resume-xmlupload' with the flag "
            f"'--skip-first-resource' to prevent duplication.\n"
            f"If not, a normal 'resume-xmlupload' can be started."
        )
        logger.error(msg)
        raise XmlUploadInterruptedError(msg) from None

    try:
        _tidy_up_resource_creation_idempotent(
            upload_state, iri, label, resource, creation_attempts_of_this_round + 1, total_num_of_resources
        )
    except KeyboardInterrupt:
        warnings.warn(GeneralDspToolsWarning("KeyboardInterrupt: Tidying up, then exit..."))
        _tidy_up_resource_creation_idempotent(
            upload_state, iri, label, resource, creation_attempts_of_this_round + 1, total_num_of_resources
        )


def _compute_counter_info_and_interrupt(
    upload_state: UploadState, total_num_of_resources: int, creation_attempts_of_this_round: int
) -> None:
    # if the interrupt_after value is not set, the upload will not be interrupted
    interrupt_after = upload_state.config.interrupt_after or total_num_of_resources + 1
    if creation_attempts_of_this_round >= interrupt_after:
        raise XmlUploadInterruptedError(
            f"Interrupted: Maximum number of resources was reached ({upload_state.config.interrupt_after})"
        )


def _tidy_up_resource_creation_idempotent(
    upload_state: UploadState,
    iri: str | None,
    label: str | None,
    resource: XMLResource,
    current_res: int,
    total_res: int,
) -> None:
    if iri and label:
        # resource creation succeeded: update the iri_resolver
        upload_state.iri_resolver.lookup[resource.res_id] = iri
        msg = f"Created resource {current_res}/{total_res}: '{label}' (ID: '{resource.res_id}', IRI: '{iri}')"
        print(f"{datetime.now()}: {msg}")
        logger.info(msg)
    else:  # noqa: PLR5501
        # resource creation failed gracefully: register it as failed
        if resource.res_id not in upload_state.failed_uploads:
            upload_state.failed_uploads.append(resource.res_id)

    if resource in upload_state.pending_resources:
        upload_state.pending_resources.remove(resource)


def _create_resource(
    resource: XMLResource,
    bitstream_information: BitstreamInfo | None,
    resource_create_client: ResourceCreateClient,
) -> tuple[str, str] | tuple[None, None]:
    try:
        return resource_create_client.create_resource(resource, bitstream_information)
    except PermanentTimeOutError as err:
        # The following block catches all exceptions and handles them in a generic way.
        # Because the calling function needs to know that this was a PermanentTimeOutError, we need to catch and
        # raise it here.
        raise err
    except Exception as err:  # noqa: BLE001 (blind-except)
        msg = f"{datetime.now()}: WARNING: Unable to create resource '{resource.label}' (ID: '{resource.res_id}')"
        if isinstance(err, BaseError):
            msg = f"{msg}: {err.message}"
        print(msg)
        log_msg = (
            f"Unable to create resource '{resource.label}' ({resource.res_id})\n"
            f"Resource details:\n{vars(resource)}\n"
            f"Property details:\n" + "\n".join([str(vars(prop)) for prop in resource.properties])
        )
        logger.exception(log_msg)
        return None, None


def _handle_upload_error(err: BaseException, upload_state: UploadState) -> None:
    """
    In case the xmlupload must be interrupted,
    e.g. because of an error that could not be handled,
    or due to keyboard interrupt,
    this method ensures
    that all information about what is already in DSP
    is written into diagnostic files.

    It then quits the Python interpreter with exit code 1.

    Args:
        err: the error that was the cause of the abort
        upload_state: the current state of the upload
    """
    if isinstance(err, XmlUploadInterruptedError):
        msg = "\n==========================================\n" + err.message + "\n"
        exit_code = 0
    else:
        msg = (
            f"\n==========================================\n"
            f"{datetime.now()}: xmlupload must be aborted because of an error.\n"
            f"Error message: '{err}'\n"
            f"For more information, see the log file: {logger_savepath}\n"
        )
        exit_code = 1

    msg += _save_upload_state(upload_state)

    if failed := upload_state.failed_uploads:
        msg += f"Independently from this, there were some resources that could not be uploaded: {failed}\n"

    if exit_code == 1:
        logger.exception(msg)
    else:
        logger.info(msg)
    print(msg)

    sys.exit(exit_code)


def _save_upload_state(upload_state: UploadState) -> str:
    save_location = upload_state.config.diagnostics.save_location
    save_location.unlink(missing_ok=True)
    save_location.touch(exist_ok=True)
    with open(save_location, "wb") as file:
        pickle.dump(upload_state, file)
    return f"Saved the current upload state to {save_location}.\n"
