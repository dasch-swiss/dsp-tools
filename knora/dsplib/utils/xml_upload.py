"""
This module handles the import of XML data into the DSP platform.
"""
import base64
import json
import os
import re
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, cast, Tuple, Any, Callable
from urllib.parse import quote_plus
from lxml import etree
from requests import RequestException

from knora.dsplib.models.projectContext import ProjectContext
from knora.dsplib.models.connection import Connection
from knora.dsplib.models.helpers import BaseError
from knora.dsplib.models.permission import Permissions
from knora.dsplib.models.resource import ResourceInstanceFactory, ResourceInstance, KnoraStandoffXmlEncoder
from knora.dsplib.models.sipi import Sipi
from knora.dsplib.models.value import KnoraStandoffXml
from knora.dsplib.models.xmlpermission import XmlPermission
from knora.dsplib.models.xmlproperty import XMLProperty
from knora.dsplib.models.xmlresource import XMLResource


def remove_circular_references(resources: list[XMLResource], verbose: bool) -> \
        tuple[list[XMLResource],
              dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
              dict[XMLResource, dict[XMLProperty, list[str]]]
              ]:
    """
    Temporarily removes problematic resource-references from a list of resources. A reference is problematic if
    it creates a circle (circular references).

    Args:
        resources: list of resources that possibly contain circular references
        verbose: verbose output if True

    Returns:
        list: list of cleaned resources
        stashed_xml_texts: dict with the stashed XML texts
        stashed_resptr_props: dict with the stashed resptr-props
    """

    if verbose:
        print("Checking resources for unresolvable references...")

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
            nok_resources, ok_res_ids, ok_resources, stashed_xml_texts, stashed_resptr_props = stash_circular_references(
                nok_resources,
                ok_res_ids,
                ok_resources,
                stashed_xml_texts,
                stashed_resptr_props
            )
        nok_len = len(nok_resources)
        nok_resources = []
        cnt += 1
        if verbose:
            print(f'{cnt}. ordering pass finished.')
    return ok_resources, stashed_xml_texts, stashed_resptr_props


def stash_circular_references(
    nok_resources: list[XMLResource],
    ok_res_ids: list[str],
    ok_resources: list[XMLResource],
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]]
) -> Tuple[
    list[XMLResource],
    list[str],
    list[XMLResource],
    dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    dict[XMLResource, dict[XMLProperty, list[str]]]
]:
    for res in nok_resources.copy():
        for link_prop in res.get_props_with_links():
            if link_prop.valtype == 'text':
                for value in link_prop.values:
                    if value.resrefs and not all([_id in ok_res_ids for _id in value.resrefs]):
                        # stash this XML text, replace it by its hash, and remove the
                        # problematic resrefs from the XMLValue's resrefs list
                        value_hash = str(hash(f'{value.value}{datetime.now()}'))
                        if res not in stashed_xml_texts:
                            stashed_xml_texts[res] = {link_prop: {value_hash: cast(KnoraStandoffXml, value.value)}}
                        elif link_prop not in stashed_xml_texts[res]:
                            stashed_xml_texts[res][link_prop] = {value_hash: cast(KnoraStandoffXml, value.value)}
                        else:
                            stashed_xml_texts[res][link_prop][value_hash] = cast(KnoraStandoffXml, value.value)
                        value.value = KnoraStandoffXml(value_hash)
                        value.resrefs = [_id for _id in value.resrefs if _id in ok_res_ids]
            elif link_prop.valtype == 'resptr':
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
                raise BaseError(f'ERROR in remove_circular_references(): link_prop.valtype is '
                                f'neither text nor resptr.')

            if len(link_prop.values) == 0:
                # if all values of a link property have been stashed, the property needs to be removed
                res.properties.remove(link_prop)

        ok_resources.append(res)
        ok_res_ids.append(res.id)
        nok_resources.remove(res)

    return nok_resources, ok_res_ids, ok_resources, stashed_xml_texts, stashed_resptr_props


def validate_xml_against_schema(input_file: str, schema_file: str) -> bool:
    """
    Validates an XML file against an XSD schema

    Args:
        input_file: the XML file to be validated
        schema_file: the schema against which the XML file should be validated

    Returns:
        True if the XML file is valid, False otherwise
    """
    xmlschema = etree.XMLSchema(etree.parse(schema_file))
    doc = etree.parse(input_file)

    if xmlschema.validate(doc):
        return True
    else:
        print("The input data file cannot be uploaded due to the following validation error(s):")
        for error in xmlschema.error_log:
            print(f"  Line {error.line}: {error.message}")
        return False


def convert_ark_v0_to_resource_iri(ark: str) -> str:
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

    Returns:
        Resource IRI (str) of the form http://rdfh.ch/080C/Ef9heHjPWDS7dMR_gGax2Q
    """
    # create the DaSCH namespace to create version 5 UUIDs
    generic_namespace_url = uuid.NAMESPACE_URL
    dasch_uuid_ns = uuid.uuid5(generic_namespace_url, "https://dasch.swiss")  # cace8b00-717e-50d5-bcb9-486f39d733a2

    # get the salsah resource ID from the ARK and convert it to a UUID version 5 (base64 encoded)
    if ark.count("-") != 2:
        raise BaseError(f"while converting ARK '{ark}'. The ARK seems to be invalid")
    project_id, resource_id, _ = ark.split("-")
    _, project_id = project_id.rsplit("/", 1)
    project_id = project_id.upper()
    if not re.match("^[0-9a-fA-F]{4}$", project_id):
        raise BaseError(f"while converting ARK '{ark}'. Invalid project shortcode '{project_id}'")
    if not re.match("^[0-9A-Za-z]+$", resource_id):
        raise BaseError(f"while converting ARK '{ark}'. Invalid Salsah ID '{resource_id}'")

    # make a UUID v5 from the namespace created above (which is a UUID itself) and the resource ID and encode it to base64
    dsp_uuid = base64.urlsafe_b64encode(uuid.uuid5(dasch_uuid_ns, resource_id).bytes).decode("utf-8")
    dsp_uuid = dsp_uuid[:-2]

    # use the new UUID to create the resource IRI
    return "http://rdfh.ch/" + project_id + "/" + dsp_uuid


def xml_upload(input_file: str, server: str, user: str, password: str, imgdir: str, sipi: str, verbose: bool,
               validate_only: bool, incremental: bool) -> bool:
    """
    This function reads an XML file and imports the data described in it onto the DSP server.

    Args:
        input_file: the XML with the data to be imported onto the DSP server
        server: the DSP server where the data should be imported
        user: the user (e-mail) with which the data should be imported
        password: the password of the user with which the data should be imported
        imgdir: the image directory
        sipi: the sipi instance to be used
        verbose: verbose option for the command, if used more output is given to the user
        validate_only: validation option to validate the XML data without the actual import of the data
        incremental: if set, IRIs instead of internal IDs are expected as resource pointers

    Returns:
        True if all resources could be uploaded without errors; False if any resource (or part of it) could not be
        successfully uploaded
    """

    # Validate the input XML file
    current_dir = os.path.dirname(os.path.realpath(__file__))
    schema_file = os.path.join(current_dir, '../schemas/data.xsd')
    if validate_xml_against_schema(input_file, schema_file):
        print("The input data file is syntactically correct and passed validation.")
        if validate_only:
            exit(0)
    else:
        print("ERROR The input data file did not pass validation.")
        exit(1)

    # Connect to the DaSCH Service Platform API and get the project context
    con = Connection(server)
    con.login(user, password)
    proj_context = ProjectContext(con=con)
    sipi_server = Sipi(sipi, con.get_token())

    # parse the XML file
    tree = etree.parse(input_file)
    for elem in tree.getiterator():
        if not (isinstance(elem, etree._Comment) or isinstance(elem, etree._ProcessingInstruction)):
            elem.tag = etree.QName(elem).localname  # remove namespace URI in the element's name
    etree.cleanup_namespaces(tree)  # remove unused namespace declarations

    root = tree.getroot()
    default_ontology = root.attrib['default-ontology']
    shortcode = root.attrib['shortcode']

    resources: list[XMLResource] = []
    permissions: dict[str, XmlPermission] = {}
    for child in root:
        if child.tag == "permissions":
            permission = XmlPermission(child, proj_context)
            permissions[permission.id] = permission
        elif child.tag == "resource":
            resources.append(XMLResource(child, default_ontology))

    # get the project information and project ontology from the server
    project = ResourceInstanceFactory(con, shortcode)
    permissions_lookup: dict[str, Permissions] = {s: perm.get_permission_instance() for s, perm in permissions.items()}
    resclass_name_2_type: dict[str, type] = {s: project.get_resclass_type(s) for s in project.get_resclass_names()}

    # temporarily remove circular references, but only if not an incremental upload
    if not incremental:
        resources, stashed_xml_texts, stashed_resptr_props = remove_circular_references(resources, verbose)
    else:
        stashed_xml_texts = dict()
        stashed_resptr_props = dict()

    id2iri_mapping: dict[str, str] = {}
    failed_uploads: list[str] = []

    try:
        id2iri_mapping, failed_uploads = upload_resources(verbose, resources, imgdir, sipi_server, permissions_lookup,
                                                          resclass_name_2_type, id2iri_mapping, con, failed_uploads)
    except BaseException as err:
        handle_upload_error(err, input_file, id2iri_mapping, failed_uploads, stashed_xml_texts, stashed_resptr_props)

    # update the resources with the stashed XML texts
    nonapplied_xml_texts = {}
    if len(stashed_xml_texts) > 0:
        try:
            nonapplied_xml_texts = upload_stashed_xml_texts(verbose, id2iri_mapping, con, stashed_xml_texts)
        except BaseException as err:
            handle_upload_error(err, input_file, id2iri_mapping, failed_uploads, stashed_xml_texts, stashed_resptr_props)

    # update the resources with the stashed resptrs
    nonapplied_resptr_props = {}
    if len(stashed_resptr_props) > 0:
        try:
            nonapplied_resptr_props = upload_stashed_resptr_props(verbose, id2iri_mapping, con, stashed_resptr_props)
        except BaseException as err:
            handle_upload_error(err, input_file, id2iri_mapping, failed_uploads, stashed_xml_texts, stashed_resptr_props)

    # write log files
    success = True
    timestamp_str = datetime.now().strftime("%Y%m%d-%H%M%S")
    write_id2iri_mapping(input_file, id2iri_mapping, timestamp_str)
    if len(nonapplied_xml_texts) > 0:
        write_stashed_xml_texts(nonapplied_xml_texts, timestamp_str)
        success = False
    if len(nonapplied_resptr_props) > 0:
        write_stashed_resptr_props(nonapplied_resptr_props, timestamp_str)
        success = False
    if failed_uploads:
        print(f"Could not upload the following resources: {failed_uploads}")
        success = False

    return success


def upload_resources(
    verbose: bool,
    resources: list[XMLResource],
    imgdir: str,
    sipi_server: Sipi,
    permissions_lookup: dict[str, Permissions],
    resclass_name_2_type: dict[str, type],
    id2iri_mapping: dict[str, str],
    con: Connection,
    failed_uploads: list[str]
) -> tuple[dict[str, str], list[str]]:
    """
    Iterates through all resources and tries to upload them to DSP

    Args:
        verbose: bool
        resources: list of XMLResources to upload to DSP
        imgdir: folder containing the multimedia files
        sipi_server: Sipi instance
        permissions_lookup: maps permission strings to Permission objects
        resclass_name_2_type: maps resource class names to their types
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP (initially empty, gets filled during the upload)
        con: connection to DSP
        failed_uploads: ids of resources that could not be uploaded (initially empty, gets filled during the upload)

    Returns:
        id2iri_mapping, failed_uploads: These two arguments are modified during the upload
    """

    for resource in resources:
        if verbose:
            resource.print()

        resource_iri = resource.iri
        if resource.ark:
            resource_iri = convert_ark_v0_to_resource_iri(resource.ark)

        # in case of a multimedia resource: upload the multimedia file
        resource_bitstream = None
        if resource.bitstream:
            img: Optional[dict[Any, Any]] = try_network_action(
                object=sipi_server,
                method='upload_bitstream',
                kwargs={'filepath': os.path.join(imgdir, resource.bitstream.value)},
                terminal_output_on_failure=f'ERROR while trying to create resource "{resource.label}" ({resource.id}).'
            )
            if not img:
                failed_uploads.append(resource.id)
                continue
            internal_file_name_bitstream = img['uploadedFiles'][0]['internalFilename']
            resource_bitstream = resource.get_bitstream(internal_file_name_bitstream, permissions_lookup)

        # create the resource in DSP
        resclass_type = resclass_name_2_type[resource.restype]
        properties = resource.get_propvals(id2iri_mapping, permissions_lookup)
        resclass_instance: ResourceInstance = try_network_action(
            method=resclass_type,
            kwargs={
                'con': con,
                'label': resource.label,
                'iri': resource_iri,
                'permissions': permissions_lookup.get(resource.permissions),
                'bitstream': resource_bitstream,
                'values': properties
            },
            terminal_output_on_failure=f"ERROR while trying to create resource '{resource.label}' ({resource.id})."
        )
        if not resclass_instance:
            failed_uploads.append(resource.id)
            continue

        created_resource: ResourceInstance = try_network_action(
            object=resclass_instance,
            method='create',
            terminal_output_on_failure=f"ERROR while trying to create resource '{resource.label}' ({resource.id})."
        )
        if not created_resource:
            failed_uploads.append(resource.id)
            continue
        id2iri_mapping[resource.id] = created_resource.iri
        print(f"Created resource '{created_resource.label}' ({resource.id}) with IRI '{created_resource.iri}'")

    return id2iri_mapping, failed_uploads


def upload_stashed_xml_texts(
    verbose: bool,
    id2iri_mapping: dict[str, str],
    con: Connection,
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]]
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

    print('Upload the stashed XML texts...')
    for resource, link_props in stashed_xml_texts.copy().items():
        if resource.id not in id2iri_mapping:
            # resource could not be uploaded to DSP, so the stash cannot be uploaded either
            continue
        print(f'  Upload XML text(s) of resource "{resource.id}"...')
        res_iri = id2iri_mapping[resource.id]
        existing_resource = try_network_action(
            object=con,
            method='get',
            kwargs={'path': f'/v2/resources/{quote_plus(res_iri)}'},
            terminal_output_on_failure=f'ERROR while uploading the xml texts of resource "{resource.id}"'
        )
        if not existing_resource:
            continue
        for link_prop, hash_to_value in link_props.items():
            existing_values = existing_resource[link_prop.name]
            if not isinstance(existing_values, list):
                existing_values = [existing_values, ]
            for existing_value in existing_values:
                old_xmltext = existing_value.get("knora-api:textValueAsXml")
                if not old_xmltext:
                    continue

                # strip all xml tags from the old xmltext, so that the pure text itself remains
                pure_text = re.sub(r'(<\?xml.+>\s*)?<text>\s*(.+)\s*<\/text>', r'\2', old_xmltext)

                # if the pure text is a hash, the replacement must be made. This hash originates from
                # stash_circular_references(), and identifies the XML texts
                if pure_text not in hash_to_value:
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
                        "@id": existing_value['@id'],
                        "@type": "knora-api:TextValue",
                        "knora-api:textValueAsXml": new_xmltext,
                        "knora-api:textValueHasMapping": {
                            '@id': 'http://rdfh.ch/standoff/mappings/StandardMapping'
                        }
                    },
                    "@context": existing_resource['@context']
                }
                jsondata = json.dumps(jsonobj, indent=4, separators=(',', ': '), cls=KnoraStandoffXmlEncoder)

                # execute API call
                response = try_network_action(
                    object=con,
                    method='put',
                    kwargs={'path': '/v2/values', 'jsondata': jsondata},
                    terminal_output_on_failure=f'ERROR while uploading the xml text of "{link_prop.name}" '
                                               f'of resource "{resource.id}"'
                )
                if not response:
                    continue
                stashed_xml_texts[resource][link_prop].pop(pure_text)
                if verbose:
                    print(f'  Successfully uploaded xml text of "{link_prop.name}"\n')

    # make a purged version of stashed_xml_texts, without empty entries
    nonapplied_xml_texts = purge_stashed_xml_texts(stashed_xml_texts)
    return nonapplied_xml_texts


def purge_stashed_xml_texts(
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]]
) -> dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]]:
    nonapplied_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]] = {}
    for res, propdict in stashed_xml_texts.items():
        for prop, xmldict in propdict.items():
            if len(xmldict) > 0:
                if res not in nonapplied_xml_texts:
                    nonapplied_xml_texts[res] = {}
                nonapplied_xml_texts[res][prop] = xmldict
    return nonapplied_xml_texts


def upload_stashed_resptr_props(
    verbose: bool,
    id2iri_mapping: dict[str, str],
    con: Connection,
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]]
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

    print('Upload the stashed resptrs...')
    for resource, prop_2_resptrs in stashed_resptr_props.copy().items():
        if resource.id not in id2iri_mapping:
            # resource could not be uploaded to DSP, so the stash cannot be uploaded either
            continue
        print(f'  Upload resptrs of resource "{resource.id}"...')
        res_iri = id2iri_mapping[resource.id]
        existing_resource = con.get(path=f'/v2/resources/{quote_plus(res_iri)}')
        for link_prop, resptrs in prop_2_resptrs.items():
            for resptr in resptrs.copy():
                jsonobj = {
                    '@id': res_iri,
                    '@type': resource.restype,
                    f'{link_prop.name}Value': {
                        '@type': 'knora-api:LinkValue',
                        'knora-api:linkValueHasTargetIri': {
                            '@id': id2iri_mapping[resptr]
                        }
                    },
                    '@context': existing_resource['@context']
                }
                jsondata = json.dumps(jsonobj, indent=4, separators=(',', ': '))
                response = try_network_action(
                    object=con,
                    method='post',
                    kwargs={'path': '/v2/values', 'jsondata': jsondata},
                    terminal_output_on_failure=f'ERROR while uploading the resptr prop of "{link_prop.name}" '
                                               f'of resource "{resource.id}"'
                )
                if not response:
                    continue
                stashed_resptr_props[resource][link_prop].remove(resptr)
                if verbose:
                    print(f'  Successfully uploaded resptr-prop of "{link_prop.name}"\n'
                          f'    Value: {resptr}')

    # make a purged version of stashed_resptr_props, without empty entries
    nonapplied_resptr_props = purge_stashed_resptr_props(stashed_resptr_props)
    return nonapplied_resptr_props


def try_network_action(
    terminal_output_on_failure: str,
    method: Union[str, Callable[..., Any]],
    object: Optional[Any] = None,
    kwargs: Optional[dict[str, Any]] = None
) -> Any:
    """
    Helper method that tries 7 times to execute an action. Each time, it catches ConnectionError and
    requests.exceptions.RequestException, which lead to a waiting time and a retry. The waiting times are 1,
    2, 4, 8, 16, 32, 64 seconds. It also catches BaseError and Exception each time, which lead to a message being
    printed and None being returned.
    If there is still no success at the end, the message is printed and None is returned.

    Args:
        terminal_output_on_failure: message to be printed if action cannot be executed
        method: either a callable to be called on its own, or a method name (as string) to be called on object
        object: if provided, it must be a python variable/object, accompanied by a method name (as string)
        kwargs: if provided, a dict with the arguments passed to method

    Returns:
        the return value of action, or None
    """

    for i in range(7):
        try:
            if object and isinstance(method, str):
                if not kwargs:
                    return getattr(object, method)()
                else:
                    return getattr(object, method)(**kwargs)
            else:
                if not kwargs:
                    return method()
                else:
                    return method(**kwargs)
        except ConnectionError:
            print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server, next attempt in {2 ** i} seconds...')
            time.sleep(2 ** i)
            continue
        except RequestException:
            print(f'{datetime.now().isoformat()}: Try reconnecting to DSP server, next attempt in {2 ** i} seconds...')
            time.sleep(2 ** i)
            continue
        except BaseError:
            print(terminal_output_on_failure)
            return None
        except Exception:
            print(terminal_output_on_failure)
            return None
    print(terminal_output_on_failure)
    return None


def purge_stashed_resptr_props(
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]]
) -> dict[XMLResource, dict[XMLProperty, list[str]]]:
    nonapplied_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]] = {}
    for res, propdict in stashed_resptr_props.items():
        for prop, resptrs in propdict.items():
            if len(resptrs) > 0:
                if res not in nonapplied_resptr_props:
                    nonapplied_resptr_props[res] = {}
                nonapplied_resptr_props[res][prop] = resptrs
    return nonapplied_resptr_props


def handle_upload_error(
    err: BaseException,
    input_file: str,
    id2iri_mapping: dict[str, str],
    failed_uploads: list[str],
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]]
) -> None:
    """
    In case the xmlupload must be interrupted, e.g. because of an error that could not be handled, or due to keyboard
    interrupt, this method ensures that all information about what is already in DSP is written into log files.

    It then re-raises the original error.

    Args:
        err: error that was the cause of the abort
        input_file: file name of the original XML file
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP (only successful uploads appear here)
        failed_uploads: resources that caused an error when uploading to DSP
        stashed_xml_texts: all xml texts that have been stashed
        stashed_resptr_props: all resptr props that have been stashed

    Returns:
        None
    """

    print(f'\n=========================================='
          f'\nxmlupload must be aborted because of an error')
    timestamp_str = datetime.now().strftime("%Y%m%d-%H%M%S")

    # write id2iri_mapping of the resources that are already in DSP
    write_id2iri_mapping(input_file, id2iri_mapping, timestamp_str)

    # Both stashes are purged from resources that have not been uploaded yet. Only stashed properties of resources that
    # already exist in DSP are of interest.
    stashed_xml_texts_purged = purge_stashed_xml_texts(
        {res: propdict for res, propdict in stashed_xml_texts.items() if res.id in id2iri_mapping})
    if len(stashed_xml_texts_purged) > 0:
        write_stashed_xml_texts(stashed_xml_texts_purged, timestamp_str)

    stashed_resptr_props_purged = purge_stashed_resptr_props(
        {res: propdict for res, propdict in stashed_resptr_props.items() if res.id in id2iri_mapping})
    if len(stashed_resptr_props_purged) > 0:
        write_stashed_resptr_props(stashed_resptr_props_purged, timestamp_str)

    # print the resources that threw an error when they were tried to be uploaded
    if failed_uploads:
        print(f"Independently of this error, there were some resources that could not be uploaded: "
              f"{failed_uploads}")

    if isinstance(err, KeyboardInterrupt):
        exit(1)
    else:
        print('The error will now be raised again:\n'
              '==========================================\n')
        raise err


def write_id2iri_mapping(input_file: str, id2iri_mapping: dict[str, str], timestamp_str: str) -> None:
    """
    Write the id2iri mapping into a file. The timestamp must be created by the caller, so that different log files can
    have an identical timestamp.

    Args:
        input_file: the file name of the original XML file
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP
        timestamp_str: timestamp for log file identification

    Returns:
        None
    """

    id2iri_mapping_file = "id2iri_" + Path(input_file).stem + "_mapping_" + timestamp_str + ".json"
    with open(id2iri_mapping_file, "w") as outfile:
        print(f"The mapping of internal IDs to IRIs was written to {id2iri_mapping_file}")
        outfile.write(json.dumps(id2iri_mapping))


def write_stashed_xml_texts(
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    timestamp_str: str
) -> None:
    """
    Write the stashed_xml_texts into a file. The timestamp must be created by the caller, so that different log files
    can have an identical timestamp.

    Args:
        stashed_xml_texts: all xml texts that have been stashed
        timestamp_str: timestamp for log file identification

    Returns:
        None
    """

    filename = f'stashed_text_properties_{timestamp_str}.txt'
    print(f'There are stashed text properties that could not be reapplied to the resources they were stripped from. '
          f'They were saved to {filename}')
    with open(filename, 'a') as f:
        f.write('Stashed text properties that could not be reapplied\n')
        f.write('***************************************************\n')
        f.write('During the xmlupload, some text properties had to be stashed away, because the salsah-links in their '
                'XML text formed a circle. The xmlupload can only be done if these circles are broken up, by stashing '
                'away some of the chain elements of the circle. \n'
                'Some of the resources that have been stripped from some of their text properties have been created in '
                'DSP, but the stashed text properties could not be reapplied to them, because the xmlupload was '
                'unexpectedly interrupted. \n'
                'This file is a list of all text properties that are now missing in DSP. The texts have been replaced '
                'by a hash number that now stands in the text field in DSP. \n'
                '(Not listed are the stripped resources that haven\'t been created in DSP yet.) \n')
        for res, props in stashed_xml_texts.items():
            f.write(f'\n{res.id}')
            f.write('\n' + '=' * len(res.id))
            for prop, stashed_texts in props.items():
                if len(stashed_texts) > 0:
                    f.write(f'\n{prop.name}')
                    f.write('\n' + '-' * len(prop.name))
                    for hash, standoff in stashed_texts.items():
                        f.write(f'\ntext with hash {hash}:\n{str(standoff).strip()}\n')


def write_stashed_resptr_props(
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]],
    timestamp_str: str
) -> None:
    """
    Write the stashed_resptr_props into a file. The timestamp must be created by the caller, so that different log files
    can have an identical timestamp.

    Args:
        stashed_resptr_props: all resptr props that have been stashed
        timestamp_str: timestamp for log file identification

    Returns:
        None
    """

    filename = f'stashed_resptr_properties_{timestamp_str}.txt'
    print(f'There are stashed resptr properties that could not be reapplied to the resources they were stripped from. '
          f'They were saved to {filename}')
    with open(filename, 'a') as f:
        f.write('Stashed resptr properties that could not be reapplied\n')
        f.write('*****************************************************\n')
        f.write('During the xmlupload, some resptr-props had to be stashed away, because they formed a circle. The '
                'xmlupload can only be done if these circles are broken up, by stashing away some of the chain '
                'elements of the circle. \n'
                'Some of the resources that have been stripped from some of their resptr-props have been created in '
                'DSP, but the stashed resptr-props could not be reapplied to them, because the xmlupload was '
                'unexpectedly interrupted. \n'
                'This file is a list of all resptr-props that are now missing in DSP. (Not listed are the stripped '
                'resources that haven\'t been created in DSP yet. \n')
        for res, props_ in stashed_resptr_props.items():
            f.write(f'\n{res.id}\n---------\n')
            for prop, stashed_props in props_.items():
                f.write(f'{prop.name}\n\t{stashed_props}\n')
