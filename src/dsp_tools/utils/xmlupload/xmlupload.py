"""
This module handles the import of XML data into the DSP platform.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Union

from lxml import etree

from dsp_tools.models.connection import Connection
from dsp_tools.models.exceptions import BaseError, UserError
from dsp_tools.models.permission import Permissions
from dsp_tools.models.projectContext import ProjectContext
from dsp_tools.models.resource import KnoraStandoffXmlEncoder, ResourceInstance, ResourceInstanceFactory
from dsp_tools.models.sipi import Sipi
from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlpermission import XmlPermission
from dsp_tools.models.xmlproperty import XMLProperty
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import login, try_network_action
from dsp_tools.utils.xmlupload.ark2iri import convert_ark_v0_to_resource_iri
from dsp_tools.utils.xmlupload.read_validate_xml_file import (
    check_consistency_with_ontology,
    validate_and_parse_xml_file,
)
from dsp_tools.utils.xmlupload.resource_multimedia import (
    calculate_multimedia_file_size,
    get_sipi_multimedia_information,
)
from dsp_tools.utils.xmlupload.stash_circular_references import remove_circular_references
from dsp_tools.utils.xmlupload.upload_stashed_resptr_props import (
    purge_stashed_resptr_props,
    upload_stashed_resptr_props,
)
from dsp_tools.utils.xmlupload.upload_stashed_xml_texts import purge_stashed_xml_texts, upload_stashed_xml_texts
from dsp_tools.utils.xmlupload.write_diagnostic_info import (
    MetricRecord,
    determine_save_location_of_diagnostic_info,
    write_id2iri_mapping_and_metrics,
)

logger = get_logger(__name__)


def xmlupload(
    input_file: Union[str, Path, etree._ElementTree[Any]],
    server: str,
    user: str,
    password: str,
    imgdir: str,
    sipi: str,
    verbose: bool = False,
    dump: bool = False,
    save_metrics: bool = False,
    preprocessing_done: bool = False,
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
        verbose: verbose option for the command, if used more output is given to the user
        dump: if true, dumps the XML file to the current working directory
        save_metrics: if true, saves time measurements into a "metrics" folder in the current working directory
        preprocessing_done: if set, all multimedia files referenced in the XML file must already be on the server

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
        preprocessing_done=preprocessing_done,
    )

    # determine save location that will be used for diagnostic info if the xmlupload is interrupted
    save_location, server_as_foldername, timestamp_str = determine_save_location_of_diagnostic_info(
        server=server,
        proj_shortcode=shortcode,
        onto_name=default_ontology,
    )
    logger.info(f"save_location='{save_location}'")

    # start metrics
    metrics: list[MetricRecord] = []
    preparation_start = datetime.now()

    # establish connection to DSP server
    con = login(server=server, user=user, password=password, dump=dump)
    sipi_server = Sipi(sipi, con.get_token())

    proj_context = _get_project_context_from_server(connection=con)

    # make Python object representations of the XML file
    permissions, resources = _extract_resources_and_permissions_from_xml(
        root=root,
        default_ontology=default_ontology,
        proj_context=proj_context,
    )

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

    # temporarily remove circular references
    resources, stashed_xml_texts, stashed_resptr_props = remove_circular_references(resources, verbose=verbose)

    preparation_duration = datetime.now() - preparation_start
    preparation_duration_ms = preparation_duration.seconds * 1000 + int(preparation_duration.microseconds / 1000)
    metrics.append(MetricRecord("", "", "", "xml upload preparation", preparation_duration_ms, ""))

    # upload all resources, then update the resources with the stashed XML texts and resptrs
    id2iri_mapping: dict[str, str] = {}
    failed_uploads: list[str] = []
    nonapplied_resptr_props = {}
    nonapplied_xml_texts = {}
    try:
        id2iri_mapping, failed_uploads, metrics = _upload_resources(
            resources=resources,
            imgdir=imgdir,
            sipi_server=sipi_server,
            permissions_lookup=permissions_lookup,
            resclass_name_2_type=resclass_name_2_type,
            id2iri_mapping=id2iri_mapping,
            con=con,
            failed_uploads=failed_uploads,
            metrics=metrics,
            preprocessing_done=preprocessing_done,
        )
        if stashed_xml_texts:
            nonapplied_xml_texts = upload_stashed_xml_texts(
                verbose=verbose,
                id2iri_mapping=id2iri_mapping,
                con=con,
                stashed_xml_texts=stashed_xml_texts,
            )
        if stashed_resptr_props:
            nonapplied_resptr_props = upload_stashed_resptr_props(
                verbose=verbose,
                id2iri_mapping=id2iri_mapping,
                con=con,
                stashed_resptr_props=stashed_resptr_props,
            )
        if nonapplied_resptr_props or nonapplied_xml_texts:
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
            stashed_xml_texts=nonapplied_xml_texts or stashed_xml_texts,
            stashed_resptr_props=nonapplied_resptr_props or stashed_resptr_props,
            save_location=save_location,
            timestamp_str=timestamp_str,
        )

    # write id2iri mapping, metrics, and print some final info
    success = write_id2iri_mapping_and_metrics(
        id2iri_mapping=id2iri_mapping,
        failed_uploads=failed_uploads,
        metrics=metrics if save_metrics else None,
        input_file=input_file,
        timestamp_str=timestamp_str,
        server_as_foldername=server_as_foldername,
    )
    if success:
        print("All resources have successfully been uploaded.")
        logger.info("All resources have successfully been uploaded.")
    return success


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
        res_inst_factory = try_network_action(
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


def _extract_resources_and_permissions_from_xml(
    root: etree._Element,
    proj_context: ProjectContext,
    default_ontology: str,
) -> tuple[dict[str, XmlPermission], list[XMLResource]]:
    """
    This function takes the root of the tree, the project context on the server and the name of the default ontology.
    From the root it separates the resource permissions.
    It returns a collection of corresponding Python objects.

    Args:
        root: root of the parsed XML file
        proj_context: Project context retrieved from server
        default_ontology: name of the default ontology as specified in the XML file

    Returns:
        A dictionary with the permission name and the permission object
        A list with the XML resource Python objects
    """
    # make Python object representations of the XML file
    resources: list[XMLResource] = []
    permissions: dict[str, XmlPermission] = {}
    for child in root:
        if child.tag == "permissions":
            permission = XmlPermission(child, proj_context)
            permissions[permission.id] = permission
        elif child.tag == "resource":
            resources.append(XMLResource(child, default_ontology))
    return permissions, resources


def _upload_resources(
    resources: list[XMLResource],
    imgdir: str,
    sipi_server: Sipi,
    permissions_lookup: dict[str, Permissions],
    resclass_name_2_type: dict[str, type],
    id2iri_mapping: dict[str, str],
    con: Connection,
    failed_uploads: list[str],
    metrics: list[MetricRecord],
    preprocessing_done: bool,
) -> tuple[dict[str, str], list[str], list[MetricRecord]]:
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
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP (initially empty, gets filled during the upload)
        con: connection to DSP
        failed_uploads: ids of resources that could not be uploaded (initially empty, gets filled during the upload)
        metrics: list with the metric records collected until now (gets filled during the upload)
        preprocessing_done: if set, all multimedia files referenced in the XML file must already be on the server

    Returns:
        id2iri_mapping, failed_uploads, metrics
    """

    bitstream_all_sizes_mb, bitstream_size_total_mb = calculate_multimedia_file_size(
        resources=resources,
        imgdir=imgdir,
        preprocessing_done=preprocessing_done,
    )
    bitstream_size_uploaded_mb = 0.0

    for i, resource in enumerate(resources):
        resource_start = datetime.now()
        filetype = ""
        filesize = round(bitstream_all_sizes_mb[i], 1)
        bitstream_duration_ms = None

        resource_iri = resource.iri
        if resource.ark:
            resource_iri = convert_ark_v0_to_resource_iri(resource.ark)

        if resource.bitstream:
            try:
                resource_bitstream = get_sipi_multimedia_information(
                    resource=resource,
                    sipi_server=sipi_server,
                    imgdir=imgdir,
                    filesize=filesize,
                    permissions_lookup=permissions_lookup,
                    metrics=metrics,
                    preprocessing_done=preprocessing_done,
                )
                bitstream_size_uploaded_mb += filesize
            except BaseError as err:
                pth = resource.bitstream.value
                err_msg = err.orig_err_msg_from_api or err.message
                msg = f"Unable to upload file '{pth}' of resource '{resource.label}' ({resource.id})"
                print(f"WARNING: {msg}: {err_msg}")
                logger.warning(msg, exc_info=True)
                msg = f"Uploaded file '{pth}' ({bitstream_size_uploaded_mb:.1f} MB / {bitstream_size_total_mb} MB)"
                print(msg)
                logger.info(msg)
                continue
        else:
            resource_bitstream = None

        # create the resource in DSP
        resclass_type = resclass_name_2_type[resource.restype]
        properties = resource.get_propvals(id2iri_mapping, permissions_lookup)
        try:
            resource_instance: ResourceInstance = resclass_type(
                con=con,
                label=resource.label,
                iri=resource_iri,
                permissions=permissions_lookup.get(str(resource.permissions)),
                creation_date=resource.creation_date,
                bitstream=resource_bitstream,
                values=properties,
            )
            resource_creation_start = datetime.now()
            created_resource: ResourceInstance = try_network_action(resource_instance.create)
            resource_creation_duration = datetime.now() - resource_creation_start
            resource_creation_duration_ms = resource_creation_duration.seconds * 1000 + int(
                resource_creation_duration.microseconds / 1000
            )
            metrics.append(
                MetricRecord(resource.id, filetype, filesize, "resource creation", resource_creation_duration_ms, "")
            )
        except BaseError as err:
            err_msg = err.orig_err_msg_from_api or err.message
            print(f"WARNING: Unable to create resource '{resource.label}' ({resource.id}): {err_msg}")
            log_msg = (
                f"Unable to create resource '{resource.label}' ({resource.id})\n"
                f"Resource details:\n{vars(resource)}\n"
                f"Property details:\n" + "\n".join([str(vars(prop)) for prop in resource.properties])
            )
            logger.warning(log_msg, exc_info=True)
            failed_uploads.append(resource.id)
            continue
        id2iri_mapping[resource.id] = created_resource.iri

        resource_designation = f"'{created_resource.label}' (ID: '{resource.id}', IRI: '{created_resource.iri}')"
        print(f"Created resource {i+1}/{len(resources)}: {resource_designation}")
        logger.info(f"Created resource {i+1}/{len(resources)}: {resource_designation}")

        resource_duration = datetime.now() - resource_start
        resource_duration_ms = resource_duration.seconds * 1000 + int(resource_duration.microseconds / 1000)
        looping_overhead_ms = resource_duration_ms - resource_creation_duration_ms - (bitstream_duration_ms or 0)
        metrics.append(MetricRecord(resource.id, filetype, filesize, "looping overhead", looping_overhead_ms, ""))

    return id2iri_mapping, failed_uploads, metrics


def _handle_upload_error(
    err: BaseException,
    id2iri_mapping: dict[str, str],
    failed_uploads: list[str],
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]],
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
        stashed_xml_texts: all xml texts that have been stashed
        stashed_resptr_props: all resptr props that have been stashed
        save_location: path where to save the diagnostic info
        timestamp_str: timestamp for the name of the diagnostic files
    """
    print(
        f"\n==========================================\n"
        f"xmlupload must be aborted because of an error.\n"
        f"Error message: '{err}'\n"
    )
    logger.error("xmlupload must be aborted because of an error", exc_info=err)

    # only stashed properties of resources that already exist in DSP are of interest
    stashed_xml_texts = purge_stashed_xml_texts(
        stashed_xml_texts=stashed_xml_texts,
        id2iri_mapping=id2iri_mapping,
    )
    stashed_resptr_props = purge_stashed_resptr_props(
        stashed_resptr_props=stashed_resptr_props,
        id2iri_mapping=id2iri_mapping,
    )

    if id2iri_mapping:
        id2iri_mapping_file = f"{save_location}/{timestamp_str}_id2iri_mapping.json"
        with open(id2iri_mapping_file, "x", encoding="utf-8") as f:
            json.dump(id2iri_mapping, f, ensure_ascii=False, indent=4)
        print(f"The mapping of internal IDs to IRIs was written to {id2iri_mapping_file}")
        logger.info(f"The mapping of internal IDs to IRIs was written to {id2iri_mapping_file}")

    if stashed_xml_texts:
        xml_filename = save_json_stashed_text_properties(
            stashed_xml_texts=stashed_xml_texts,
            save_location=save_location,
            timestamp_str=timestamp_str,
        )
        msg = (
            f"There are stashed text properties that could not be reapplied to the resources they were stripped from. "
            f"They were saved to {xml_filename}.\n"
        )
        print(msg)
        logger.info(msg)

    if stashed_resptr_props:
        resptr_filename = save_json_stashed_resptr_properties(
            stashed_resptr_props=stashed_resptr_props,
            save_location=save_location,
            timestamp_str=timestamp_str,
        )
        msg = (
            f"There are stashed resptr properties that could not be reapplied "
            f"to the resources they were stripped from. They were saved to {resptr_filename}\n"
        )
        print(msg)
        logger.info(msg)

    # print the resources that threw an error when they were tried to be uploaded
    if failed_uploads:
        msg = f"Independently of this error, there were some resources that could not be uploaded: {failed_uploads}"
        print(msg)
        logger.info(msg)

    sys.exit(1)


def save_json_stashed_resptr_properties(
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]],
    save_location: Path,
    timestamp_str: str,
) -> str:
    """
    This function saves the stashed resptr properties in a JSON file.
    It returns the name of the file.

    Args:
        stashed_resptr_props: Dictionary with the stash
        save_location: filepath to the save location
        timestamp_str: timestamp from the beginning of the upload

    Returns:
        name of the JSON file
    """
    stashed_resptr_props_serializable = {
        resource.id: {_property.name: property_list for _property, property_list in res_dict.items()}
        for resource, res_dict in stashed_resptr_props.items()
    }
    resptr_filename = f"{save_location}/{timestamp_str}_stashed_resptr_properties.json"
    with open(resptr_filename, "x", encoding="utf-8") as f:
        json.dump(
            obj=stashed_resptr_props_serializable,
            fp=f,
            ensure_ascii=False,
            indent=4,
        )
    return resptr_filename


def save_json_stashed_text_properties(
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    save_location: Path,
    timestamp_str: str,
) -> str:
    """
    This function saves the stashed XML properties in a JSON file.
    It returns the name of the file.

    Args:
        stashed_xml_texts: Dictionary with the stash
        save_location: filepath to the save location
        timestamp_str: timestamp from the beginning of the upload

    Returns:
        name of the JSON file
    """
    stashed_xml_texts_serializable = {
        resource.id: {_property.name: xml for _property, xml in res_dict.items()}
        for resource, res_dict in stashed_xml_texts.items()
    }
    xml_filename = f"{save_location}/{timestamp_str}_stashed_text_properties.json"
    with open(xml_filename, "x", encoding="utf-8") as file:
        json.dump(
            obj=stashed_xml_texts_serializable,
            fp=file,
            ensure_ascii=False,
            indent=4,
            cls=KnoraStandoffXmlEncoder,
        )
    return xml_filename
