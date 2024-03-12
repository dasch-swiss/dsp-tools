from __future__ import annotations

import pickle
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

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
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.exceptions import UserError
from dsp_tools.models.exceptions import XmlUploadInterruptedError
from dsp_tools.models.projectContext import ProjectContext
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive
from dsp_tools.utils.create_logger import get_log_filename_str
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.json_ld_util import get_json_ld_context_for_project

logger = get_logger(__name__)


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
    iri_resolver = IriResolver()

    iri_resolver, failed_uploads, nonapplied_stash = upload_resources(
        resources=resources,
        failed_uploads=[],
        imgdir=imgdir,
        sipi_server=sipi_server,
        permissions_lookup=permissions_lookup,
        con=con,
        stash=stash,
        config=config,
        project_client=project_client,
        list_client=list_client,
        iri_resolver=iri_resolver,
    )

    return cleanup_upload(iri_resolver, config, failed_uploads, nonapplied_stash)


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
        logfiles = get_log_filename_str(logger)
        if failed_uploads:
            print(f"\n{datetime.now()}: WARNING: Could not upload the following resources: {failed_uploads}\n")
            print(f"For more information, see the log file: {logfiles}\n")
            logger.warning(f"Could not upload the following resources: {failed_uploads}")
        if nonapplied_stash:
            print(f"\n{datetime.now()}: WARNING: Could not reapply the following stash items: {nonapplied_stash}\n")
            print(f"For more information, see the log file: {logfiles}\n")
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
    resources: list[XMLResource],
    failed_uploads: list[str],
    imgdir: str,
    sipi_server: Sipi,
    permissions_lookup: dict[str, Permissions],
    con: Connection,
    stash: Stash | None,
    config: UploadConfig,
    project_client: ProjectClient,
    list_client: ListClient,
    iri_resolver: IriResolver,
) -> tuple[IriResolver, list[str], Stash | None]:
    """
    Actual upload of all resources to DSP.

    Args:
        resources: list of XMLResources to upload to DSP
        failed_uploads: resources that caused an error in a previous upload
        imgdir: folder containing the multimedia files
        sipi_server: Sipi instance
        permissions_lookup: dictionary that contains the permission name as string and the corresponding Python object
        con: connection to the DSP server
        stash: an object that contains all stashed links that could not be reapplied to their resources
        config: the upload configuration
        project_client: a client for HTTP communication with the DSP-API
        list_client: a client for HTTP communication with the DSP-API
        iri_resolver: mapping from internal IDs to IRIs

    Returns:
        the id2iri mapping of the uploaded resources,
        a list of resources that could not be uploaded,
        and the stash items that could not be reapplied.
    """
    try:
        iri_resolver, failed_uploads = _upload_resources(
            resources=resources,
            failed_uploads=failed_uploads,
            imgdir=imgdir,
            sipi_server=sipi_server,
            permissions_lookup=permissions_lookup,
            con=con,
            config=config,
            project_client=project_client,
            list_client=list_client,
            iri_resolver=iri_resolver,
        )
    except BaseException as err:  # noqa: BLE001 (blind-except)
        # The forseeable errors are already handled by failed_uploads
        # Here we catch the unforseeable exceptions, incl. keyboard interrupt.
        _handle_upload_error(
            err=err,
            iri_resolver=iri_resolver,
            pending_resources=resources,
            failed_uploads=failed_uploads,
            pending_stash=stash,
            config=config,
            permissions_lookup=permissions_lookup,
        )

    nonapplied_stash = None
    try:
        nonapplied_stash = (
            _upload_stash(
                stash=stash,
                iri_resolver=iri_resolver,
                con=con,
                project_client=project_client,
            )
            if stash
            else None
        )
    except BaseException as err:  # noqa: BLE001 (blind-except)
        # The forseeable errors are already handled by failed_uploads and nonapplied_stash.
        # Here we catch the unforseeable exceptions, incl. keyboard interrupt.
        _handle_upload_error(
            err=err,
            iri_resolver=iri_resolver,
            pending_resources=resources,
            failed_uploads=failed_uploads,
            pending_stash=stash,
            config=config,
            permissions_lookup=permissions_lookup,
        )
    return iri_resolver, failed_uploads, nonapplied_stash


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
    con: Connection,
    project_client: ProjectClient,
) -> Stash | None:
    if stash.standoff_stash:
        nonapplied_standoff = upload_stashed_xml_texts(
            iri_resolver=iri_resolver,
            con=con,
            stashed_xml_texts=stash.standoff_stash,
        )
    else:
        nonapplied_standoff = None
    context = get_json_ld_context_for_project(project_client.get_ontology_name_dict())
    if stash.link_value_stash:
        nonapplied_resptr_props = upload_stashed_resptr_props(
            iri_resolver=iri_resolver,
            con=con,
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
        logger.error(
            "Unable to retrieve project context from DSP server",
            exc_info=True,
        )
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
    resources: list[XMLResource],
    failed_uploads: list[str],
    imgdir: str,
    sipi_server: Sipi,
    permissions_lookup: dict[str, Permissions],
    con: Connection,
    config: UploadConfig,
    project_client: ProjectClient,
    list_client: ListClient,
    iri_resolver: IriResolver,
) -> tuple[IriResolver, list[str]]:
    """
    Iterates through all resources and tries to upload them to DSP.
    If a temporary exception occurs, the action is repeated until success,
    and if a permanent exception occurs, the resource is skipped.

    Args:
        resources: list of XMLResources to upload to DSP
        failed_uploads: resources that caused an error in a previous upload
        imgdir: folder containing the multimedia files
        sipi_server: Sipi instance
        permissions_lookup: maps permission strings to Permission objects
        con: connection to DSP
        config: the upload configuration
        project_client: a client for HTTP communication with the DSP-API
        list_client: a client for HTTP communication with the DSP-API
        iri_resolver: mapping from internal IDs to IRIs

    Raises:
        BaseException: in case of an unhandled exception during resource creation
        XmlUploadInterruptedError: if the number of resources created is equal to the interrupt_after value

    Returns:
        id2iri_mapping, failed_uploads
    """
    project_iri = project_client.get_project_iri()
    json_ld_context = get_json_ld_context_for_project(project_client.get_ontology_name_dict())
    listnode_lookup = list_client.get_list_node_id_to_iri_lookup()

    resource_create_client = ResourceCreateClient(
        con=con,
        project_iri=project_iri,
        iri_resolver=iri_resolver,
        json_ld_context=json_ld_context,
        permissions_lookup=permissions_lookup,
        listnode_lookup=listnode_lookup,
        media_previously_ingested=config.media_previously_uploaded,
    )

    total_res = len(resources) + len(iri_resolver.lookup)
    previous_successful = len(iri_resolver.lookup)
    previous_failed = len(failed_uploads)
    previous_total = previous_successful + previous_failed
    # if the interrupt_after value is not set, the upload will not be interrupted
    interrupt_after = config.interrupt_after or total_res + 1

    for i, resource in enumerate(resources.copy()):
        current_res = i + 1 + previous_total
        if i >= interrupt_after:
            raise XmlUploadInterruptedError(f"Interrupted: Maximum number of resources was reached ({interrupt_after})")
        success, media_info = handle_media_info(
            resource, config.media_previously_uploaded, sipi_server, imgdir, permissions_lookup
        )
        if not success:
            failed_uploads.append(resource.res_id)
            continue

        res = None
        try:
            res = _create_resource(resource, media_info, resource_create_client)
            if res == (None, None):
                # resource creation failed gracefully: register it as failed, then continue
                failed_uploads.append(resource.res_id)
                continue
            else:
                # resource creation succeeded: update the iri_resolver and remove the resource from the list
                iri, label = res
                _tidy_up_resource_creation(iri, label, iri_resolver, resource, current_res, total_res)  # type: ignore[arg-type]
        except BaseException as err:
            if res and res[0]:
                # creation succeeded, but during tidy up, a Keyboard Interrupt occurred. tidy up again before escalating
                iri, label = res
                _tidy_up_resource_creation(iri, label, iri_resolver, resource, current_res, total_res)
            else:
                # unhandled exception during resource creation
                failed_uploads.append(resource.res_id)
            raise err from None
        finally:
            resources.remove(resource)

    return iri_resolver, failed_uploads


def _tidy_up_resource_creation(
    iri: str,
    label: str,
    iri_resolver: IriResolver,
    resource: XMLResource,
    current_res: int,
    total_res: int,
) -> None:
    iri_resolver.update(resource.res_id, iri)
    resource_designation = f"'{label}' (ID: '{resource.res_id}', IRI: '{iri}')"
    print(f"{datetime.now()}: Created resource {current_res}/{total_res}: {resource_designation}")
    logger.info(f"Created resource {current_res}/{total_res}: {resource_designation}")


def _create_resource(
    resource: XMLResource,
    bitstream_information: BitstreamInfo | None,
    resource_create_client: ResourceCreateClient,
) -> tuple[str, str] | tuple[None, None]:
    try:
        return resource_create_client.create_resource(resource, bitstream_information)
    except Exception as err:
        msg = f"{datetime.now()}: WARNING: Unable to create resource '{resource.label}' ({resource.res_id})"
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


def _handle_upload_error(
    err: BaseException,
    iri_resolver: IriResolver,
    pending_resources: list[XMLResource],
    failed_uploads: list[str],
    pending_stash: Stash | None,
    config: UploadConfig,
    permissions_lookup: dict[str, Permissions],
) -> None:
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
        iri_resolver: a resolver for internal IDs to IRIs
        pending_resources: resources that were not uploaded to DSP
        failed_uploads: resources that caused an error when uploading to DSP
        pending_stash: an object that contains all stashed links that could not yet be reapplied to their resources
        config: the upload configuration
        permissions_lookup: dictionary that contains the permission name as string and the corresponding Python object
    """
    if isinstance(err, XmlUploadInterruptedError):
        msg = "\n==========================================\n" + err.message + "\n"
        exit_code = 0
    else:
        logfiles = get_log_filename_str(logger)
        msg = (
            f"\n==========================================\n"
            f"{datetime.now()}: xmlupload must be aborted because of an error.\n"
            f"Error message: '{err}'\n"
            f"For more information, see the log file: {logfiles}\n"
        )
        exit_code = 1

    upload_state = UploadState(
        pending_resources, failed_uploads, iri_resolver.lookup, pending_stash, config, permissions_lookup
    )
    msg += _save_upload_state(upload_state)

    if failed_uploads:
        msg += f"Independently from this, there were some resources that could not be uploaded: {failed_uploads}\n"

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
