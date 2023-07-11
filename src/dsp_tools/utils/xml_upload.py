"""
This module handles the import of XML data into the DSP platform.
"""
from __future__ import annotations

import base64
import copy
import json
import os
import re
import sys
import uuid
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union, cast
from urllib.parse import quote_plus

import pandas as pd
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
from dsp_tools.utils.logging import get_logger
from dsp_tools.utils.shared import login, try_network_action, validate_xml_against_schema

MetricRecord = namedtuple("MetricRecord", ["res_id", "filetype", "filesize_mb", "event", "duration_ms", "mb_per_sec"])

logger = get_logger(__name__)


def _transform_server_url_to_foldername(server: str) -> str:
    """
    Take the server URL and transform it so that it can be used as foldername.

    Args:
        server: server, e.g. "https://api.test.dasch.swiss/" or "http://0.0.0.0:3333"

    Returns:
        simplified version, e.g. "test.dasch.swiss" or "localhost"
    """
    server_substitutions = {
        r"https?://": "",
        r"^api\.": "",
        r":\d{2,5}/?$": "",
        r"/$": "",
        r"0.0.0.0": "localhost",
    }
    for pattern, repl in server_substitutions.items():
        server = re.sub(pattern, repl, server)
    return server


def _determine_save_location_of_diagnostic_info(
    server: str,
    proj_shortcode: str,
    onto_name: str,
) -> tuple[Path, str, str]:
    """
    Determine the save location for diagnostic info that will be used if the xmlupload is interrupted.
    They are going to be stored in ~/.dsp-tools/xmluploads/server/shortcode/ontoname.
    This path is computed and created.

    Args:
        server: URL of the DSP server where the data is uploaded to
        proj_shortcode: 4-digit hexadecimal shortcode of the project
        onto_name: name of the ontology that the data belongs to

    Returns:
        a tuple consisting of the absolute full path to the storage location,
        a version of the server URL that can be used as foldername,
        and the timestamp string that can be used as component of file names
        (so that different diagnostic files of the same xmlupload have the same timestamp)
    """
    server_as_foldername = _transform_server_url_to_foldername(server)
    timestamp_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    save_location = Path.home() / Path(".dsp-tools") / "xmluploads" / server_as_foldername / proj_shortcode / onto_name
    save_location.mkdir(parents=True, exist_ok=True)
    return save_location, server_as_foldername, timestamp_str


def _write_id2iri_mapping_and_metrics(
    id2iri_mapping: dict[str, str],
    metrics: Optional[list[MetricRecord]],
    failed_uploads: list[str],
    input_file: Union[str, Path, etree._ElementTree[Any]],
    timestamp_str: str,
    server_as_foldername: str,
) -> bool:
    """
    Writes the id2iri mapping and the metrics into the current working directory,
    and prints the failed uploads (if applicable).

    Args:
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP (initially empty, gets filled during the upload)
        metrics: list with the metric records collected until now (gets filled during the upload)
        failed_uploads: ids of resources that could not be uploaded (initially empty, gets filled during the upload)
        input_file: path to the XML file or parsed ElementTree
        timestamp_str: timestamp for the name of the log files
        server_as_foldername: simplified version of the server URL that can be used as folder name

    Returns:
        True if there are no failed_uploads, False otherwise
    """
    # determine names of files
    if isinstance(input_file, (str, Path)):
        id2iri_filename = f"{Path(input_file).stem}_id2iri_mapping_{timestamp_str}.json"
        metrics_filename = f"{timestamp_str}_metrics_{server_as_foldername}_{Path(input_file).stem}.csv"
    else:
        id2iri_filename = f"{timestamp_str}_id2iri_mapping.json"
        metrics_filename = f"{timestamp_str}_metrics_{server_as_foldername}.csv"

    # write files and print info
    success = True
    with open(id2iri_filename, "x", encoding="utf-8") as f:
        json.dump(id2iri_mapping, f, ensure_ascii=False, indent=4)
        print(f"The mapping of internal IDs to IRIs was written to {id2iri_filename}")
        logger.info(f"The mapping of internal IDs to IRIs was written to {id2iri_filename}")
    if failed_uploads:
        print(f"\nWARNING: Could not upload the following resources: {failed_uploads}\n")
        logger.warning(f"Could not upload the following resources: {failed_uploads}")
        success = False
    if metrics:
        os.makedirs("metrics", exist_ok=True)
        df = pd.DataFrame(metrics)
        df.to_csv(f"metrics/{metrics_filename}")
        print(f"Total time of xmlupload: {sum(int(record.duration_ms) for record in metrics) / 1000:.1f} seconds")

    return success


def _remove_circular_references(
    resources: list[XMLResource],
    verbose: bool,
) -> tuple[
    list[XMLResource],
    dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    dict[XMLResource, dict[XMLProperty, list[str]]],
]:
    """
    Temporarily removes problematic resource-references from a list of resources. A reference is problematic if
    it creates a circle (circular references).

    Args:
        resources: list of resources that possibly contain circular references
        verbose: verbose output if True

    Raises:
        BaseError

    Returns:
        list: list of cleaned resources
        stashed_xml_texts: dict with the stashed XML texts
        stashed_resptr_props: dict with the stashed resptr-props
    """

    if verbose:
        print("Checking resources for unresolvable references...")
        logger.info("Checking resources for unresolvable references...")

    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]] = {}
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]] = {}

    # sort the resources according to outgoing resptrs
    ok_resources: list[XMLResource] = []
    nok_resources: list[XMLResource] = []
    ok_res_ids: list[str] = []
    cnt = 0
    nok_len = 9999999
    while len(resources) > 0 and cnt < 10000:
        for resource in resources:
            resptrs = resource.get_resptrs()
            if len(resptrs) == 0:
                ok_resources.append(resource)
                ok_res_ids.append(resource.id)
            else:
                ok = True
                for resptr in resptrs:
                    if resptr not in ok_res_ids:
                        ok = False
                if ok:
                    ok_resources.append(resource)
                    ok_res_ids.append(resource.id)
                else:
                    nok_resources.append(resource)
        resources = nok_resources
        if len(nok_resources) == nok_len:
            # there are circular references. go through all problematic resources, and stash the problematic references.
            (
                nok_resources,
                ok_res_ids,
                ok_resources,
                stashed_xml_texts,
                stashed_resptr_props,
            ) = _stash_circular_references(
                nok_resources=nok_resources,
                ok_res_ids=ok_res_ids,
                ok_resources=ok_resources,
                stashed_xml_texts=stashed_xml_texts,
                stashed_resptr_props=stashed_resptr_props,
            )
        nok_len = len(nok_resources)
        nok_resources = []
        cnt += 1
        if verbose:
            print(f"{cnt}. ordering pass finished.")
            logger.info(f"{cnt}. ordering pass finished.")
    return ok_resources, stashed_xml_texts, stashed_resptr_props


def _stash_circular_references(
    nok_resources: list[XMLResource],
    ok_res_ids: list[str],
    ok_resources: list[XMLResource],
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]],
) -> tuple[
    list[XMLResource],
    list[str],
    list[XMLResource],
    dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    dict[XMLResource, dict[XMLProperty, list[str]]],
]:
    """
    Raises:
        BaseError
    """
    for res in nok_resources.copy():
        for link_prop in res.get_props_with_links():
            if link_prop.valtype == "text":
                for value in link_prop.values:
                    if value.resrefs and not all(_id in ok_res_ids for _id in value.resrefs):
                        # stash this XML text, replace it by its hash, and remove the
                        # problematic resrefs from the XMLValue's resrefs list
                        value_hash = str(hash(f"{value.value}{datetime.now()}"))
                        if res not in stashed_xml_texts:
                            stashed_xml_texts[res] = {link_prop: {value_hash: cast(KnoraStandoffXml, value.value)}}
                        elif link_prop not in stashed_xml_texts[res]:
                            stashed_xml_texts[res][link_prop] = {value_hash: cast(KnoraStandoffXml, value.value)}
                        else:
                            stashed_xml_texts[res][link_prop][value_hash] = cast(KnoraStandoffXml, value.value)
                        value.value = KnoraStandoffXml(value_hash)
                        value.resrefs = [_id for _id in value.resrefs if _id in ok_res_ids]
            elif link_prop.valtype == "resptr":
                for value in link_prop.values.copy():
                    if value.value not in ok_res_ids:
                        # value.value is the id of the target resource. stash it, then delete it
                        if res not in stashed_resptr_props:
                            stashed_resptr_props[res] = {}
                            stashed_resptr_props[res][link_prop] = [str(value.value)]
                        else:
                            if link_prop not in stashed_resptr_props[res]:
                                stashed_resptr_props[res][link_prop] = [str(value.value)]
                            else:
                                stashed_resptr_props[res][link_prop].append(str(value.value))
                        link_prop.values.remove(value)
            else:
                logger.error("ERROR in remove_circular_references(): link_prop.valtype is neither text nor resptr.")
                raise BaseError("ERROR in remove_circular_references(): link_prop.valtype is neither text nor resptr.")

            if len(link_prop.values) == 0:
                # if all values of a link property have been stashed, the property needs to be removed
                res.properties.remove(link_prop)

        ok_resources.append(res)
        ok_res_ids.append(res.id)
        nok_resources.remove(res)

    return nok_resources, ok_res_ids, ok_resources, stashed_xml_texts, stashed_resptr_props


def _convert_ark_v0_to_resource_iri(ark: str) -> str:
    """
    Converts an ARK URL from salsah.org (ARK version 0) of the form ark:/72163/080c-779b9990a0c3f-6e to a DSP resource
    IRI of the form http://rdfh.ch/080C/Ef9heHjPWDS7dMR_gGax2Q

    This method is needed for the migration of projects from salsah.org to DSP. Resources need to be created with an
    existing ARK, so the IRI needs to be extracted from that ARK in order for the ARK URL to be still valid after the
    migration.

    Args:
        ark: an ARK version 0 of the form ark:/72163/080c-779b9990a0c3f-6e, '72163' being the Name Assigning Authority
        number, '080c' being the project shortcode, '779b9990a0c3f' being an ID derived from the object's Salsah ID and
        '6e' being check digits

    Raises:
        BaseError if the ARK is invalid

    Returns:
        Resource IRI (str) of the form http://rdfh.ch/080C/Ef9heHjPWDS7dMR_gGax2Q
    """
    # create the DaSCH namespace to create version 5 UUIDs
    generic_namespace_url = uuid.NAMESPACE_URL
    dasch_uuid_ns = uuid.uuid5(generic_namespace_url, "https://dasch.swiss")  # cace8b00-717e-50d5-bcb9-486f39d733a2

    # get the salsah resource ID from the ARK and convert it to a UUID version 5 (base64 encoded)
    if ark.count("-") != 2:
        logger.error(f"while converting ARK '{ark}'. The ARK seems to be invalid")
        raise BaseError(f"while converting ARK '{ark}'. The ARK seems to be invalid")
    project_id, resource_id, _ = ark.split("-")
    _, project_id = project_id.rsplit("/", 1)
    project_id = project_id.upper()
    if not re.match("^[0-9a-fA-F]{4}$", project_id):
        logger.error(f"while converting ARK '{ark}'. Invalid project shortcode '{project_id}'")
        raise BaseError(f"while converting ARK '{ark}'. Invalid project shortcode '{project_id}'")
    if not re.match("^[0-9A-Za-z]+$", resource_id):
        logger.error(f"while converting ARK '{ark}'. Invalid Salsah ID '{resource_id}'")
        raise BaseError(f"while converting ARK '{ark}'. Invalid Salsah ID '{resource_id}'")

    # make a UUID v5 from the namespace created above (which is a UUID itself) and the resource ID
    # and encode it to base64
    dsp_uuid = base64.urlsafe_b64encode(uuid.uuid5(dasch_uuid_ns, resource_id).bytes).decode("utf-8")
    dsp_uuid = dsp_uuid[:-2]

    # use the new UUID to create the resource IRI
    return "http://rdfh.ch/" + project_id + "/" + dsp_uuid


def _parse_xml_file(input_file: Union[str, Path, etree._ElementTree[Any]]) -> etree._Element:
    """
    Parse an XML file with DSP-conform data,
    remove namespace URI from the elements' names,
    and transform the special tags <annotation>, <region>, and <link>
    to their technically correct form
    <resource restype="Annotation">, <resource restype="Region">, and <resource restype="LinkObj">.

    Args:
        input_file: path to the XML file, or parsed ElementTree

    Returns:
        the root element of the parsed XML file
    """

    # remove comments and processing instructions (commented out properties break the XMLProperty constructor)
    if isinstance(input_file, (str, Path)):
        parser = etree.XMLParser(remove_comments=True, remove_pis=True)
        tree = etree.parse(source=input_file, parser=parser)
    else:
        tree = copy.deepcopy(input_file)
        for c in tree.xpath("//comment()"):
            c.getparent().remove(c)
        for c in tree.xpath("//processing-instruction()"):
            c.getparent().remove(c)

    # remove namespace URI from the elements' names and transform the special tags to their technically correct form
    for elem in tree.iter():
        elem.tag = etree.QName(elem).localname  # remove namespace URI in the element's name
        if elem.tag == "annotation":
            elem.attrib["restype"] = "Annotation"
            elem.tag = "resource"
        elif elem.tag == "link":
            elem.attrib["restype"] = "LinkObj"
            elem.tag = "resource"
        elif elem.tag == "region":
            elem.attrib["restype"] = "Region"
            elem.tag = "resource"

    # remove unused namespace declarations
    etree.cleanup_namespaces(tree)

    return tree.getroot()


def _check_consistency_with_ontology(
    resources: list[XMLResource],
    resclass_name_2_type: dict[str, type],
    shortcode: str,
    ontoname: str,
    verbose: bool = False,
) -> None:
    """
    Checks if the resource types and properties in the XML are consistent with the ontology.

    Args:
        resources: a list of parsed XMLResources
        resclass_name_2_type: infos about the resource classes that exist on the DSP server for the current ontology
        shortcode: the shortcode of the project
            as referenced in the attribute "shortcode" of the <knora> tag of the XML file
        ontoname: the name of the ontology
            as referenced in the attribute "default-ontology" of the <knora> tag of the XML file
        verbose: verbose switch

    Raises:
        UserError with a detailed error message if there is an inconsistency between the ontology and the data

    Returns:
        None if everything is okay
    """
    if verbose:
        print("Check if the resource types and properties are consistent with the ontology...")
        logger.info("Check if the resource types and properties are consistent with the ontology...")
    if not any(x.startswith(ontoname) for x in resclass_name_2_type.keys()):
        err_msg = (
            f"The <knora> tag of your XML file references the ontology '{ontoname}', "
            f"but the project {shortcode} on the DSP server doesn't contain an ontology with this name."
        )
        logger.error(err_msg)
        raise UserError(err_msg)
    knora_properties = resclass_name_2_type[resources[0].restype].knora_properties  # type: ignore[attr-defined]

    for resource in resources:
        # check that the resource type is consistent with the ontology
        if resource.restype not in resclass_name_2_type:
            res_syntaxes = [
                'DSP-API internals: <resource restype="restype">',
                'current ontology:  <resource restype=":restype">',
                'other ontology:    <resource restype="other:restype">',
            ]
            res_explanations = [
                'will be interpreted as "knora-api:restype"',
                '"restype" must be defined in the "resources" section of your ontology',
                'not yet implemented: "other" must be defined in the same JSON project file as your ontology',
            ]
            err_msg = (
                f"=========================\n"
                f"ERROR: Resource '{resource.label}' (ID: {resource.id}) "
                f"has an invalid resource type '{resource.restype}'. "
                "Is your syntax correct? Remember the rules:\n"
            )
            for res_syntax, res_explanation in zip(res_syntaxes, res_explanations):
                err_msg += f" - {res_syntax:<55} ({res_explanation})\n"
            logger.error(err_msg)
            raise UserError(err_msg)

        # check that the property types are consistent with the ontology
        resource_properties = resclass_name_2_type[resource.restype].properties.keys()  # type: ignore[attr-defined]
        for propname in [prop.name for prop in resource.properties]:
            if propname not in knora_properties and propname not in resource_properties:
                prop_syntaxes = [
                    'DSP-API internals: <text-prop name="propname">',
                    'current ontology:  <text-prop name=":propname">',
                    'other ontology:    <text-prop name="other:propname">',
                ]
                prop_explanations = [
                    'will be interpreted as "knora-api:propname"',
                    '"propname" must be defined in the "properties" section of your ontology',
                    'not yet implemented: "other" must be defined in the same JSON project file as your ontology',
                ]
                err_msg = (
                    f"=========================\n"
                    f"ERROR: Resource '{resource.label}' (ID: {resource.id}) has an invalid property '{propname}'. "
                    f"Is your syntax correct? Remember the rules:\n"
                )
                for prop_syntax, prop_explanation in zip(prop_syntaxes, prop_explanations):
                    err_msg += f" - {prop_syntax:<55} ({prop_explanation})\n"
                logger.error(err_msg)
                raise UserError(err_msg)

    print("Resource types and properties are consistent with the ontology.")
    logger.info("Resource types and properties are consistent with the ontology.")


def _check_if_bitstreams_exist(
    root: etree._Element,
    imgdir: str,
) -> None:
    """
    Make sure that all bitstreams referenced in the XML file exist in the imgdir.

    Args:
        root: parsed XML file
        imgdir: folder where the bitstreams are stored

    Raises:
        UserError: if a bitstream does not exist in the imgdir
    """
    multimedia_resources = [x for x in root if any((y.tag == "bitstream" for y in x.iter()))]
    for res in multimedia_resources:
        pth = [Path(x.text) for x in res.iter() if x.tag == "bitstream" and x.text][0]
        if not Path(imgdir / pth).is_file():
            raise UserError(
                f"Bitstream '{pth!s}' of resource '{res.attrib['label']}' does not exist in the imgdir '{imgdir}'."
            )


def xml_upload(
    input_file: Union[str, Path, etree._ElementTree[Any]],
    server: str,
    user: str,
    password: str,
    imgdir: str,
    sipi: str,
    verbose: bool,
    incremental: bool,
    save_metrics: bool,
    preprocessing_done: bool,
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
        incremental: if set, IRIs instead of internal IDs are expected as resource pointers
        save_metrics: if true, saves time measurements into a "metrics" folder in the current working directory
        preprocessing_done: if set, all multimedia files referenced in the XML file must already be on the server

    Raises:
        BaseError or UserError in case of permanent network or software failure
        UserError if the XML file is invalid

    Returns:
        True if all resources could be uploaded without errors; False if one of the resources could not be
        uploaded because there is an error in it
    """
    # parse the XML file
    validate_xml_against_schema(input_file=input_file)
    root = _parse_xml_file(input_file=input_file)
    if not preprocessing_done:
        _check_if_bitstreams_exist(root=root, imgdir=imgdir)
    shortcode = root.attrib["shortcode"]
    default_ontology = root.attrib["default-ontology"]
    logger.info(f"Validated and parsed the XML file. Shortcode='{shortcode}' and default_ontology='{default_ontology}'")

    # determine save location that will be used for diagnostic info if the xmlupload is interrupted
    save_location, server_as_foldername, timestamp_str = _determine_save_location_of_diagnostic_info(
        server=server,
        proj_shortcode=shortcode,
        onto_name=default_ontology,
    )
    logger.info(f"save_location='{save_location}'")

    # start metrics
    metrics: list[MetricRecord] = []
    preparation_start = datetime.now()

    # Connect to the DaSCH Service Platform API and get the project context
    con = login(server=server, user=user, password=password)
    try:
        proj_context = try_network_action(lambda: ProjectContext(con=con))
    except BaseError:
        logger.error("Unable to retrieve project context from DSP server", exc_info=True)
        raise UserError("Unable to retrieve project context from DSP server") from None
    sipi_server = Sipi(sipi, con.get_token())

    # make Python object representations of the XML file
    resources: list[XMLResource] = []
    permissions: dict[str, XmlPermission] = {}
    for child in root:
        if child.tag == "permissions":
            permission = XmlPermission(child, proj_context)
            permissions[permission.id] = permission
        elif child.tag == "resource":
            resources.append(XMLResource(child, default_ontology))

    # get the project information and project ontology from the server
    try:
        res_inst_factory = try_network_action(lambda: ResourceInstanceFactory(con, shortcode))
    except BaseError:
        logger.error(f"A project with shortcode {shortcode} could not be found on the DSP server", exc_info=True)
        raise UserError(f"A project with shortcode {shortcode} could not be found on the DSP server") from None
    permissions_lookup: dict[str, Permissions] = {s: perm.get_permission_instance() for s, perm in permissions.items()}
    resclass_name_2_type: dict[str, type] = {
        s: res_inst_factory.get_resclass_type(s) for s in res_inst_factory.get_resclass_names()
    }

    # check if the data in the XML is consistent with the ontology
    _check_consistency_with_ontology(
        resources=resources,
        resclass_name_2_type=resclass_name_2_type,
        shortcode=shortcode,
        ontoname=default_ontology,
        verbose=verbose,
    )

    # temporarily remove circular references, but only if not an incremental upload
    if not incremental:
        resources, stashed_xml_texts, stashed_resptr_props = _remove_circular_references(resources, verbose)
    else:
        stashed_xml_texts = dict()
        stashed_resptr_props = dict()

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
            nonapplied_xml_texts = _upload_stashed_xml_texts(
                verbose=verbose,
                id2iri_mapping=id2iri_mapping,
                con=con,
                stashed_xml_texts=stashed_xml_texts,
            )
        if stashed_resptr_props:
            nonapplied_resptr_props = _upload_stashed_resptr_props(
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
    success = _write_id2iri_mapping_and_metrics(
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

    Returns:
        id2iri_mapping, failed_uploads, metrics
    """

    # If there are multimedia files: calculate their total size
    bitstream_all_sizes_mb = [
        Path(Path(imgdir) / Path(res.bitstream.value)).stat().st_size / 1000000
        if res.bitstream and not preprocessing_done
        else 0.0
        for res in resources
    ]
    if sum(bitstream_all_sizes_mb) > 0:
        bitstream_size_total_mb = round(sum(bitstream_all_sizes_mb), 1)
        bitstream_size_uploaded_mb = 0.0
        print(f"This xmlupload contains multimedia files with a total size of {bitstream_size_total_mb} MB.")
        logger.info(f"This xmlupload contains multimedia files with a total size of {bitstream_size_total_mb} MB.")
    else:  # make Pylance happy
        bitstream_size_total_mb = 0.0
        bitstream_size_uploaded_mb = 0.0

    for i, resource in enumerate(resources):
        resource_start = datetime.now()
        filetype = ""
        filesize = round(bitstream_all_sizes_mb[i], 1)
        bitstream_duration_ms = None
        resource_iri = resource.iri
        if resource.ark:
            resource_iri = _convert_ark_v0_to_resource_iri(resource.ark)

        # in case of a multimedia resource: upload the multimedia file
        resource_bitstream = None
        if preprocessing_done and resource.bitstream:
            resource_bitstream = resource.get_bitstream(resource.bitstream.value, permissions_lookup)
        elif resource.bitstream:
            pth = resource.bitstream.value
            try:
                bitstream_start = datetime.now()
                filetype = Path(pth).suffix[1:]
                img: Optional[dict[Any, Any]] = try_network_action(
                    sipi_server.upload_bitstream,
                    filepath=str(Path(imgdir) / Path(pth)),
                )
                bitstream_duration = datetime.now() - bitstream_start
                bitstream_duration_ms = bitstream_duration.seconds * 1000 + int(bitstream_duration.microseconds / 1000)
                mb_per_sec = round((filesize / bitstream_duration_ms) * 1000, 1)
                metrics.append(
                    MetricRecord(resource.id, filetype, filesize, "bitstream upload", bitstream_duration_ms, mb_per_sec)
                )
            except BaseError as err:
                err_msg = err.orig_err_msg_from_api or err.message
                msg = f"Unable to upload file '{pth}' of resource '{resource.label}' ({resource.id})"
                print(f"WARNING: {msg}: {err_msg}")
                logger.warning(msg, exc_info=True)
                failed_uploads.append(resource.id)
                continue
            bitstream_size_uploaded_mb += bitstream_all_sizes_mb[i]
            msg = f"Uploaded file '{pth}' ({bitstream_size_uploaded_mb:.1f} MB / {bitstream_size_total_mb} MB)"
            print(msg)
            logger.info(msg)
            internal_file_name_bitstream = img["uploadedFiles"][0]["internalFilename"]  # type: ignore[index]
            resource_bitstream = resource.get_bitstream(internal_file_name_bitstream, permissions_lookup)

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
            logger.warning(f"Unable to create resource '{resource.label}' ({resource.id}).", exc_info=True)
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


def _upload_stashed_xml_texts(
    verbose: bool,
    id2iri_mapping: dict[str, str],
    con: Connection,
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
) -> dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]]:
    """
    After all resources are uploaded, the stashed xml texts must be applied to their resources in DSP.

    Args:
        verbose: bool
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP
        con: connection to DSP
        stashed_xml_texts: all xml texts that have been stashed

    Returns:
        nonapplied_xml_texts: the xml texts that could not be uploaded
    """

    print("Upload the stashed XML texts...")
    logger.info("Upload the stashed XML texts...")
    nonapplied_xml_texts = stashed_xml_texts.copy()
    for resource, link_props in stashed_xml_texts.items():
        if resource.id not in id2iri_mapping:
            # resource could not be uploaded to DSP, so the stash cannot be uploaded either
            # no action necessary: this resource will remain in nonapplied_xml_texts,
            # which will be handled by the caller
            continue
        res_iri = id2iri_mapping[resource.id]
        try:
            existing_resource = try_network_action(con.get, path=f"/v2/resources/{quote_plus(res_iri)}")
        except BaseError as err:
            # print the message to keep track of the cause for the failure. Apart from that, no action is necessary:
            # this resource will remain in nonapplied_xml_texts, which will be handled by the caller
            orig_err_msg = err.orig_err_msg_from_api or err.message
            err_msg = (
                f"Unable to upload XML texts of resource '{resource.id}', "
                "because the resource cannot be retrieved from the DSP server."
            )
            print(f"  WARNING: {err_msg} Original error message: {orig_err_msg}")
            logger.warning(err_msg, exc_info=True)
            continue
        print(f'  Upload XML text(s) of resource "{resource.id}"...')
        logger.info(f'  Upload XML text(s) of resource "{resource.id}"...')
        for link_prop, hash_to_value in link_props.items():
            existing_values = existing_resource[link_prop.name]
            if not isinstance(existing_values, list):
                existing_values = [existing_values]
            for existing_value in existing_values:
                old_xmltext = existing_value.get("knora-api:textValueAsXml")
                if not old_xmltext:
                    # no action necessary: this property will remain in nonapplied_xml_texts,
                    # which will be handled by the caller
                    continue

                # strip all xml tags from the old xmltext, so that the pure text itself remains
                pure_text = re.sub(r"(<\?xml.+>\s*)?<text>\s*(.+)\s*<\/text>", r"\2", old_xmltext)

                # if the pure text is a hash, the replacement must be made. This hash originates from
                # _stash_circular_references(), and identifies the XML texts
                if pure_text not in hash_to_value:
                    # no action necessary: this property will remain in nonapplied_xml_texts,
                    # which will be handled by the caller
                    continue
                new_xmltext = hash_to_value[pure_text]

                # replace the outdated internal ids by their IRI
                for _id, _iri in id2iri_mapping.items():
                    new_xmltext.regex_replace(f'href="IRI:{_id}:IRI"', f'href="{_iri}"')

                # prepare API call
                jsonobj = {
                    "@id": res_iri,
                    "@type": resource.restype,
                    link_prop.name: {
                        "@id": existing_value["@id"],
                        "@type": "knora-api:TextValue",
                        "knora-api:textValueAsXml": new_xmltext,
                        "knora-api:textValueHasMapping": {"@id": "http://rdfh.ch/standoff/mappings/StandardMapping"},
                    },
                    "@context": existing_resource["@context"],
                }
                jsondata = json.dumps(jsonobj, indent=4, separators=(",", ": "), cls=KnoraStandoffXmlEncoder)

                # execute API call
                try:
                    try_network_action(con.put, path="/v2/values", jsondata=jsondata)
                except BaseError as err:
                    # print the message to keep track of the cause for the failure.
                    # Apart from that, no action is necessary:
                    # this resource will remain in nonapplied_xml_texts, which will be handled by the caller
                    orig_err_msg = err.orig_err_msg_from_api or err.message
                    err_msg = f"Unable to upload the xml text of '{link_prop.name}' of resource '{resource.id}'."
                    print(f"    WARNING: {err_msg} Original error message: {orig_err_msg}")
                    logger.warning(err_msg, exc_info=True)
                    continue
                nonapplied_xml_texts[resource][link_prop].pop(pure_text)
                if verbose:
                    print(f'  Successfully uploaded xml text of "{link_prop.name}"\n')
                    logger.info(f'  Successfully uploaded xml text of "{link_prop.name}"\n')

    # make a purged version of nonapplied_xml_texts, without empty entries
    nonapplied_xml_texts = _purge_stashed_xml_texts(
        stashed_xml_texts=nonapplied_xml_texts,
        id2iri_mapping=id2iri_mapping,
    )
    return nonapplied_xml_texts


def _purge_stashed_xml_texts(
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    id2iri_mapping: dict[str, str],
) -> dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]]:
    """
    Accepts a stash of XML texts and purges it of resources that could not be uploaded (=don't exist in DSP), and of
    resources that had all their XML texts reapplied. It returns a new dict with only the resources that exist in DSP,
    but whose XML texts could not all be uploaded.

    Args:
        stashed_xml_texts: the stash to purge
        id2iri_mapping: used to check if a resource could be uploaded

    Returns:
        a purged version of stashed_xml_text
    """
    # remove resources that couldn't be uploaded. If they don't exist in DSP, it's not worth caring about their xmltexts
    stashed_xml_texts = {res: propdict for res, propdict in stashed_xml_texts.items() if res.id in id2iri_mapping}

    # remove resources that don't have stashed xmltexts (=all xmltexts had been reapplied)
    nonapplied_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]] = {}
    for res, propdict in stashed_xml_texts.items():
        for prop, xmldict in propdict.items():
            if len(xmldict) > 0:
                if res not in nonapplied_xml_texts:
                    nonapplied_xml_texts[res] = {}
                nonapplied_xml_texts[res][prop] = xmldict
    return nonapplied_xml_texts


def _upload_stashed_resptr_props(
    verbose: bool,
    id2iri_mapping: dict[str, str],
    con: Connection,
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]],
) -> dict[XMLResource, dict[XMLProperty, list[str]]]:
    """
    After all resources are uploaded, the stashed resptr props must be applied to their resources in DSP.

    Args:
        verbose: bool
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP
        con: connection to DSP
        stashed_resptr_props: all resptr props that have been stashed

    Returns:
        nonapplied_resptr_props: the resptr props that could not be uploaded
    """

    print("Upload the stashed resptrs...")
    logger.info("Upload the stashed resptrs...")
    nonapplied_resptr_props = stashed_resptr_props.copy()
    for resource, prop_2_resptrs in stashed_resptr_props.items():
        if resource.id not in id2iri_mapping:
            # resource could not be uploaded to DSP, so the stash cannot be uploaded either
            # no action necessary: this resource will remain in nonapplied_resptr_props,
            # which will be handled by the caller
            continue
        res_iri = id2iri_mapping[resource.id]
        try:
            existing_resource = try_network_action(con.get, path=f"/v2/resources/{quote_plus(res_iri)}")
        except BaseError as err:
            # print the message to keep track of the cause for the failure. Apart from that, no action is necessary:
            # this resource will remain in nonapplied_resptr_props, which will be handled by the caller
            orig_err_msg = err.orig_err_msg_from_api or err.message
            err_msg = (
                f"Unable to upload resptrs of resource '{resource.id}', "
                "because the resource cannot be retrieved from the DSP server."
            )
            print(f"  WARNING: {err_msg} Original error message: {orig_err_msg}")
            logger.warning(err_msg, exc_info=True)
            continue
        print(f'  Upload resptrs of resource "{resource.id}"...')
        logger.info(f'  Upload resptrs of resource "{resource.id}"...')
        for link_prop, resptrs in prop_2_resptrs.items():
            for resptr in resptrs.copy():
                jsonobj = {
                    "@id": res_iri,
                    "@type": resource.restype,
                    f"{link_prop.name}Value": {
                        "@type": "knora-api:LinkValue",
                        "knora-api:linkValueHasTargetIri": {
                            # if target doesn't exist in DSP, send the (invalid) resource ID of target to DSP,
                            # which will produce an understandable error message
                            "@id": id2iri_mapping.get(resptr, resptr)
                        },
                    },
                    "@context": existing_resource["@context"],
                }
                jsondata = json.dumps(jsonobj, indent=4, separators=(",", ": "))
                try:
                    try_network_action(con.post, path="/v2/values", jsondata=jsondata)
                except BaseError as err:
                    # print the message to keep track of the cause for the failure.
                    # Apart from that, no action is necessary:
                    # this resource will remain in nonapplied_resptr_props, which will be handled by the caller
                    orig_err_msg = err.orig_err_msg_from_api or err.message
                    err_msg = f"Unable to upload the resptr prop of '{link_prop.name}' of resource '{resource.id}'."
                    print(f"    WARNING: {err_msg} Original error message: {orig_err_msg}")
                    logger.warning(err_msg, exc_info=True)
                    continue
                nonapplied_resptr_props[resource][link_prop].remove(resptr)
                if verbose:
                    print(f'  Successfully uploaded resptr-prop of "{link_prop.name}". Value: {resptr}')
                    logger.info(f'Successfully uploaded resptr-prop of "{link_prop.name}". Value: {resptr}')

    # make a purged version of nonapplied_resptr_props, without empty entries
    nonapplied_resptr_props = _purge_stashed_resptr_props(
        stashed_resptr_props=nonapplied_resptr_props,
        id2iri_mapping=id2iri_mapping,
    )
    return nonapplied_resptr_props


def _purge_stashed_resptr_props(
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]],
    id2iri_mapping: dict[str, str],
) -> dict[XMLResource, dict[XMLProperty, list[str]]]:
    """
    Accepts a stash of resptrs and purges it of resources that could not be uploaded (=don't exist in DSP), and of
    resources that had all their resptrs reapplied. It returns a new dict with only the resources that exist in DSP,
    but whose resptrs could not all be uploaded.

    Args:
        stashed_resptr_props: the stash to purge
        id2iri_mapping: used to check if a resource could be uploaded (optional)

    Returns:
        a purged version of stashed_resptr_props
    """
    # remove resources that couldn't be uploaded. If they don't exist in DSP, it's not worth caring about their resptrs
    stashed_resptr_props = {res: pdict for res, pdict in stashed_resptr_props.items() if res.id in id2iri_mapping}

    # remove resources that don't have stashed resptrs (=all resptrs had been reapplied)
    nonapplied_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]] = {}
    for res, propdict in stashed_resptr_props.items():
        for prop, resptrs in propdict.items():
            if len(resptrs) > 0:
                if res not in nonapplied_resptr_props:
                    nonapplied_resptr_props[res] = {}
                nonapplied_resptr_props[res][prop] = resptrs
    return nonapplied_resptr_props


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

    Returns:
        None
    """
    print(
        f"\n==========================================\n"
        f"xmlupload must be aborted because of an error.\n"
        f"Error message: '{err}'\n"
    )
    logger.error("xmlupload must be aborted because of an error", exc_info=err)

    # only stashed properties of resources that already exist in DSP are of interest
    stashed_xml_texts = _purge_stashed_xml_texts(
        stashed_xml_texts=stashed_xml_texts,
        id2iri_mapping=id2iri_mapping,
    )
    stashed_resptr_props = _purge_stashed_resptr_props(
        stashed_resptr_props=stashed_resptr_props,
        id2iri_mapping=id2iri_mapping,
    )

    if id2iri_mapping:
        id2iri_mapping_file = f"{save_location}/{timestamp_str}_id2iri_mapping.json\n"
        with open(id2iri_mapping_file, "x", encoding="utf-8") as f:
            json.dump(id2iri_mapping, f, ensure_ascii=False, indent=4)
        print(f"The mapping of internal IDs to IRIs was written to {id2iri_mapping_file}")
        logger.info(f"The mapping of internal IDs to IRIs was written to {id2iri_mapping_file}")

    if stashed_xml_texts:
        stashed_xml_texts_serializable = {
            r.id: {p.name: xml for p, xml in rdict.items()} for r, rdict in stashed_xml_texts.items()
        }
        xml_filename = f"{save_location}/{timestamp_str}_stashed_text_properties.json"
        with open(xml_filename, "x", encoding="utf-8") as f:
            json.dump(
                obj=stashed_xml_texts_serializable,
                fp=f,
                ensure_ascii=False,
                indent=4,
                cls=KnoraStandoffXmlEncoder,
            )
        msg = (
            f"There are stashed text properties that could not be reapplied to the resources they were stripped from. "
            f"They were saved to {xml_filename}.\n"
        )
        print(msg)
        logger.info(msg)

    if stashed_resptr_props:
        stashed_resptr_props_serializable = {
            r.id: {p.name: plist for p, plist in rdict.items()} for r, rdict in stashed_resptr_props.items()
        }
        resptr_filename = f"{save_location}/{timestamp_str}_stashed_resptr_properties.json"
        with open(resptr_filename, "x", encoding="utf-8") as f:
            json.dump(
                obj=stashed_resptr_props_serializable,
                fp=f,
                ensure_ascii=False,
                indent=4,
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
