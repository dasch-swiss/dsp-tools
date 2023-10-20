"""
This module handles the import of XML data into the DSP platform.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Union

from lxml import etree

from dsp_tools.connection.connection import Connection
from dsp_tools.models.exceptions import BaseError, UserError
from dsp_tools.models.permission import Permissions
from dsp_tools.models.projectContext import ProjectContext
from dsp_tools.models.resource import KnoraStandoffXmlEncoder, ResourceInstance, ResourceInstanceFactory
from dsp_tools.models.sipi import Sipi
from dsp_tools.models.xmlpermission import XmlPermission
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import login, try_network_action
from dsp_tools.utils.xmlupload.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.utils.xmlupload.read_validate_xml_file import (
    check_consistency_with_ontology,
    validate_and_parse_xml_file,
)
from dsp_tools.utils.xmlupload.resource_multimedia import handle_bitstream
from dsp_tools.utils.xmlupload.stash.stash_models import Stash
from dsp_tools.utils.xmlupload.stash_circular_references import remove_circular_references
from dsp_tools.utils.xmlupload.upload_config import UploadConfig
from dsp_tools.utils.xmlupload.upload_stashed_resptr_props import upload_stashed_resptr_props
from dsp_tools.utils.xmlupload.upload_stashed_xml_texts import upload_stashed_xml_texts
from dsp_tools.utils.xmlupload.write_diagnostic_info import write_id2iri_mapping

logger = get_logger(__name__)


def xmlupload(
    input_file: Union[str, Path, etree._ElementTree[Any]],
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
        input_file: path to the XML file or parsed ElementTree
        server: the DSP server where the data should be imported
        user: the user (e-mail) with which the data should be imported
        password: the password of the user with which the data should be imported
        imgdir: the image directory
        sipi: the sipi instance to be used
        config: the upload configuration

    Raises:
        BaseError: in case of permanent network or software failure
        UserError: in case of permanent network or software failure, or if the XML file is invalid

    Returns:
        True if all resources could be uploaded without errors; False if one of the resources could not be
        uploaded because there is an error in it
    """
    default_ontology, root, shortcode = validate_and_parse_xml_file(
        input_file=input_file,
        imgdir=imgdir,
        preprocessing_done=config.preprocessing_done,
    )

    config = config.with_server_info(
        server=server,
        shortcode=shortcode,
        onto_name=default_ontology,
    )

    # establish connection to DSP server
    con = login(server=server, user=user, password=password, dump=config.dump)
    sipi_server = Sipi(sipi, con.get_token())

    resources, permissions_lookup, resclass_name_2_type, stash = _prepare_upload(
        root=root,
        con=con,
        default_ontology=default_ontology,
        shortcode=shortcode,
        verbose=config.verbose,
    )

    id2iri_mapping, failed_uploads = _upload(
        resources=resources,
        imgdir=imgdir,
        sipi_server=sipi_server,
        permissions_lookup=permissions_lookup,
        resclass_name_2_type=resclass_name_2_type,
        con=con,
        stash=stash,
        config=config,
    )

    write_id2iri_mapping(id2iri_mapping, input_file, config.timestamp_str)
    success = not failed_uploads
    if success:
        print("All resources have successfully been uploaded.")
        logger.info("All resources have successfully been uploaded.")
    else:
        print(f"\nWARNING: Could not upload the following resources: {failed_uploads}\n")
        logger.warning(f"Could not upload the following resources: {failed_uploads}")
    return success


def _prepare_upload(
    root: etree._Element,
    con: Connection,
    default_ontology: str,
    shortcode: str,
    verbose: bool,
) -> tuple[list[XMLResource], dict[str, Permissions], dict[str, type], Stash | None]:
    resources, permissions_lookup, resclass_name_2_type = _get_data_from_xml(
        con=con,
        root=root,
        default_ontology=default_ontology,
        shortcode=shortcode,
        verbose=verbose,
    )
    # temporarily remove circular references
    resources, stash = remove_circular_references(resources, verbose=verbose)
    return resources, permissions_lookup, resclass_name_2_type, stash


def _upload(
    resources: list[XMLResource],
    imgdir: str,
    sipi_server: Sipi,
    permissions_lookup: dict[str, Permissions],
    resclass_name_2_type: dict[str, type],
    con: Connection,
    stash: Stash | None,
    config: UploadConfig,
) -> tuple[dict[str, str], list[str]]:
    # upload all resources, then update the resources with the stashed XML texts and resptrs
    failed_uploads: list[str] = []
    try:
        id2iri_mapping, failed_uploads = _upload_resources(
            resources=resources,
            imgdir=imgdir,
            sipi_server=sipi_server,
            permissions_lookup=permissions_lookup,
            resclass_name_2_type=resclass_name_2_type,
            con=con,
            preprocessing_done=config.preprocessing_done,
        )
        nonapplied_stash = (
            _upload_stash(
                stash=stash,
                id2iri_mapping=id2iri_mapping,
                con=con,
                context=config.json_ld_context,
                verbose=config.verbose,
            )
            if stash
            else None
        )
        if nonapplied_stash:
            msg = "Some stashed resptrs or XML texts could not be reapplied to their resources on the DSP server."
            logger.error(msg)
            raise BaseError(msg)
    except BaseException as err:  # pylint: disable=broad-except
        # The forseeable errors are already handled by the variables
        # failed_uploads, nonapplied_xml_texts, and nonapplied_resptr_props.
        # Here we catch the unforseeable exceptions, hence BaseException (=the base class of all exceptions)
        _handle_upload_error(
            err=err,
            id2iri_mapping=id2iri_mapping,
            failed_uploads=failed_uploads,
            stash=stash,
            save_location=config.save_location,
            timestamp_str=config.timestamp_str,
        )
    return id2iri_mapping, failed_uploads


def _get_data_from_xml(
    con: Connection,
    root: etree._Element,
    default_ontology: str,
    shortcode: str,
    verbose: bool,
) -> tuple[list[XMLResource], dict[str, Permissions], dict[str, type]]:
    proj_context = _get_project_context_from_server(connection=con)
    permissions = _extract_permissions_from_xml(root, proj_context)
    resources = _extract_resources_from_xml(root, default_ontology)
    permissions_lookup, resclass_name_2_type = _get_project_permissions_and_classes_from_server(
        server_connection=con,
        permissions=permissions,
        shortcode=shortcode,
    )
    check_consistency_with_ontology(
        resources=resources,
        resclass_name_2_type=resclass_name_2_type,
        shortcode=shortcode,
        ontoname=default_ontology,
        verbose=verbose,
    )
    return resources, permissions_lookup, resclass_name_2_type


def _upload_stash(
    stash: Stash,
    id2iri_mapping: dict[str, str],
    con: Connection,
    context: dict[str, str],
    verbose: bool,
) -> Stash | None:
    if stash.standoff_stash:
        nonapplied_standoff = upload_stashed_xml_texts(
            verbose=verbose,
            id2iri_mapping=id2iri_mapping,
            con=con,
            stashed_xml_texts=stash.standoff_stash,
        )
    else:
        nonapplied_standoff = None
    if stash.link_value_stash:
        nonapplied_resptr_props = upload_stashed_resptr_props(
            verbose=verbose,
            id2iri_mapping=id2iri_mapping,
            con=con,
            stashed_resptr_props=stash.link_value_stash,
            context=context,
        )
    else:
        nonapplied_resptr_props = None
    return Stash.make(nonapplied_standoff, nonapplied_resptr_props)


def _get_project_permissions_and_classes_from_server(
    server_connection: Connection,
    permissions: dict[str, XmlPermission],
    shortcode: str,
) -> tuple[dict[str, Permissions], dict[str, type]]:
    """
    This function tries to connect to the server and retrieve the project information.
    If the project is not on the server, it raises a UserError.
    From the information from the server, it creates a dictionary with the permission information,
    and a dictionary with the information about the classes.

    Args:
        server_connection: connection to the server
        permissions: the permissions extracted from the XML
        shortcode: the shortcode specified in the XML

    Returns:
        A dictionary with the name of the permission with the Python object
        And a dictionary with the class name as string and the Python type of the class

    Raises:
        UserError: If the project is not uploaded on the server
    """
    # get the project information and project ontology from the server
    try:
        res_inst_factory: ResourceInstanceFactory = try_network_action(
            lambda: ResourceInstanceFactory(con=server_connection, projident=shortcode)
        )
    except BaseError:
        logger.error(
            f"A project with shortcode {shortcode} could not be found on the DSP server",
            exc_info=True,
        )
        raise UserError(f"A project with shortcode {shortcode} could not be found on the DSP server") from None
    permissions_lookup = {
        permission_name: perm.get_permission_instance() for permission_name, perm in permissions.items()
    }
    resclass_name_2_type = {
        resource_class_name: res_inst_factory.get_resclass_type(prefixedresclass=resource_class_name)
        for resource_class_name in res_inst_factory.get_resclass_names()
    }
    return permissions_lookup, resclass_name_2_type


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
        proj_context: ProjectContext = try_network_action(lambda: ProjectContext(con=connection))
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
    return {permission.id: permission for permission in permissions}


def _extract_resources_from_xml(root: etree._Element, default_ontology: str) -> list[XMLResource]:
    resources = list(root.iter(tag="resource"))
    return [XMLResource(res, default_ontology) for res in resources]


def _upload_resources(
    resources: list[XMLResource],
    imgdir: str,
    sipi_server: Sipi,
    permissions_lookup: dict[str, Permissions],
    resclass_name_2_type: dict[str, type],
    con: Connection,
    preprocessing_done: bool,
) -> tuple[dict[str, str], list[str]]:
    """
    Iterates through all resources and tries to upload them to DSP.
    If a temporary exception occurs, the action is repeated until success,
    and if a permanent exception occurs, the resource is skipped.

    Args:
        resources: list of XMLResources to upload to DSP
        imgdir: folder containing the multimedia files
        sipi_server: Sipi instance
        permissions_lookup: maps permission strings to Permission objects
        resclass_name_2_type: maps resource class names to their types
        con: connection to DSP
        preprocessing_done: if set, all multimedia files referenced in the XML file must already be on the server

    Returns:
        id2iri_mapping, failed_uploads
    """
    id2iri_mapping: dict[str, str] = {}
    failed_uploads: list[str] = []

    for i, resource in enumerate(resources):
        resource_iri = resource.iri
        if resource.ark:
            resource_iri = convert_ark_v0_to_resource_iri(resource.ark)

        bitstream_information = None
        if bitstream := resource.bitstream:
            bitstream_information = handle_bitstream(
                resource=resource,
                bitstream=bitstream,
                preprocessing_done=preprocessing_done,
                permissions_lookup=permissions_lookup,
                sipi_server=sipi_server,
                imgdir=imgdir,
            )
            if not bitstream_information:
                # Note: previously, if the bitstream could not be uploaded, the resource was skipped without adding to
                # the failed_uploads list, which I'm not sure was as intended
                failed_uploads.append(resource.id)
                continue

        res = _create_resource(
            res_type=resclass_name_2_type[resource.restype],
            resource=resource,
            resource_iri=resource_iri,
            bitstream_information=bitstream_information,
            con=con,
            permissions_lookup=permissions_lookup,
            id2iri_mapping=id2iri_mapping,
        )
        if not res:
            failed_uploads.append(resource.id)
            continue
        iri, label = res
        id2iri_mapping[resource.id] = iri

        resource_designation = f"'{label}' (ID: '{resource.id}', IRI: '{iri}')"
        print(f"Created resource {i+1}/{len(resources)}: {resource_designation}")
        logger.info(f"Created resource {i+1}/{len(resources)}: {resource_designation}")

    return id2iri_mapping, failed_uploads


def _create_resource(
    res_type: type,
    resource: XMLResource,
    resource_iri: str | None,
    bitstream_information: dict[str, Any] | None,
    con: Connection,
    permissions_lookup: dict[str, Permissions],
    id2iri_mapping: dict[str, str],
) -> tuple[str, str] | None:
    properties = resource.get_propvals(id2iri_mapping, permissions_lookup)
    try:
        resource_instance: ResourceInstance = res_type(
            con=con,
            label=resource.label,
            iri=resource_iri,
            permissions=permissions_lookup.get(str(resource.permissions)),
            creation_date=resource.creation_date,
            bitstream=bitstream_information,
            values=properties,
        )
        created_resource: ResourceInstance = try_network_action(resource_instance.create)
        return created_resource.iri, created_resource.label
    except BaseError as err:
        err_msg = err.orig_err_msg_from_api or err.message
        print(f"WARNING: Unable to create resource '{resource.label}' ({resource.id}): {err_msg}")
        log_msg = (
            f"Unable to create resource '{resource.label}' ({resource.id})\n"
            f"Resource details:\n{vars(resource)}\n"
            f"Property details:\n" + "\n".join([str(vars(prop)) for prop in resource.properties])
        )
        logger.warning(log_msg, exc_info=True)
        return None


def _handle_upload_error(
    err: BaseException,
    id2iri_mapping: dict[str, str],
    failed_uploads: list[str],
    stash: Stash | None,
    save_location: Path,
    timestamp_str: str,
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
        err: error that was the cause of the abort
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP (only successful uploads appear here)
        failed_uploads: resources that caused an error when uploading to DSP
        stash: an object that contains all stashed links that could not be reapplied to their resources
        save_location: path where to save the diagnostic info
        timestamp_str: timestamp for the name of the diagnostic files
    """
    print(
        f"\n==========================================\n"
        f"xmlupload must be aborted because of an error.\n"
        f"Error message: '{err}'\n"
    )
    logger.error("xmlupload must be aborted because of an error", exc_info=err)

    if id2iri_mapping:
        id2iri_mapping_file = f"{save_location}/{timestamp_str}_id2iri_mapping.json"
        with open(id2iri_mapping_file, "x", encoding="utf-8") as f:
            json.dump(id2iri_mapping, f, ensure_ascii=False, indent=4)
        print(f"The mapping of internal IDs to IRIs was written to {id2iri_mapping_file}")
        logger.info(f"The mapping of internal IDs to IRIs was written to {id2iri_mapping_file}")

    if stash:
        filename = _save_stash_as_json(
            stash=stash,
            save_location=save_location,
            timestamp_str=timestamp_str,
        )
        msg = (
            f"There are stashed links that could not be reapplied to the resources they were stripped from. "
            f"They were saved to {filename}\n"
        )
        print(msg)
        logger.info(msg)

    # print the resources that threw an error when they were tried to be uploaded
    if failed_uploads:
        msg = f"Independently of this error, there were some resources that could not be uploaded: {failed_uploads}"
        print(msg)
        logger.info(msg)

    sys.exit(1)


def _save_stash_as_json(
    stash: Stash,
    save_location: Path,
    timestamp_str: str,
) -> str:
    filename = f"{save_location}/{timestamp_str}_stashed_links.json"
    with open(filename, "x", encoding="utf-8") as file:
        json.dump(
            obj=stash,
            fp=file,
            ensure_ascii=False,
            indent=4,
            cls=KnoraStandoffXmlEncoder,
        )
    return filename
