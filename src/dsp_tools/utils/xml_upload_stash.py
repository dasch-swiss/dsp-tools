from __future__ import annotations

import json
from typing import Any

import regex

from dsp_tools.models.connection import Connection
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.resource import KnoraStandoffXmlEncoder
from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlproperty import XMLProperty
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action

logger = get_logger(__name__)


def log_unable_to_retrieve_resource(
    resource: XMLResource,
    received_error: BaseError,
) -> None:
    """
    This function logs the error if it is not possible to retrieve the resource.

    Args:
        resource: the resource
        received_error: the error
    """
    # print the message to keep track of the cause for the failure
    # apart from that; no action is necessary:
    # this resource will remain in nonapplied_xml_texts, which will be handled by the caller
    orig_err_msg = received_error.orig_err_msg_from_api or received_error.message
    err_msg = (
        f"Unable to upload XML texts of resource '{resource.id}', "
        "because the resource cannot be retrieved from the DSP server."
    )
    print(f"  WARNING: {err_msg} Original error message: {orig_err_msg}")
    logger.warning(err_msg, exc_info=True)


def _log_unable_to_upload_xml_resource(
    received_error: BaseError,
    stashed_resource: XMLResource,
    all_link_props: XMLProperty,
) -> None:
    """
    This function logs if it is not possible to upload a xml resource.

    Args:
        received_error: Error received
        stashed_resource: resource that is stashed
        all_link_props: all the link properties from that resource

    Returns:

    """
    # print the message to keep track of the cause for the failure
    # apart from that; no action is necessary:
    # this resource will remain in nonapplied_xml_texts, which will be handled by the caller
    orig_err_msg = received_error.orig_err_msg_from_api or received_error.message
    err_msg = f"Unable to upload the xml text of '{all_link_props.name}' of resource '{stashed_resource.id}'."
    print(f"    WARNING: {err_msg} Original error message: {orig_err_msg}")
    logger.warning(err_msg, exc_info=True)


def _get_text_hash_value(old_xmltext: str) -> str:
    """
    This function extracts the hash values in the text

    Args:
        old_xmltext: Text with has values.

    Returns:
        hash values
    """
    return regex.sub(r"(<\?xml.+>\s*)?<text>\s*(.+)\s*<\/text>", r"\2", old_xmltext)


def _replace_internal_ids_with_iris(
    pure_text: str,
    id2iri_mapping: dict[str, str],
    hash_to_value: dict[str, KnoraStandoffXml],
) -> KnoraStandoffXml:
    """
    This function replaces the internal ids with the new IRIs from the triplestore.

    Args:
        pure_text: the text with the ids
        id2iri_mapping: the dictionary that contains the mapping information
        hash_to_value: the dictionary that contains the hash of the string and the xml value

    Returns:
        the xml value with the old ids replaced
    """
    new_xmltext = hash_to_value[pure_text]
    # replace the outdated internal ids by their IRI
    for _id, _iri in id2iri_mapping.items():
        new_xmltext.regex_replace(f'href="IRI:{_id}:IRI"', f'href="{_iri}"')
    return new_xmltext


def _create_XMLResource_json_object_to_update(
    res_iri: str,
    resource_in_triplestore: Any,
    stashed_resource: XMLResource,
    link_prop_in_triplestore: dict[str, Any],
    new_xmltext: KnoraStandoffXml,
    link_prop_name: str,
) -> str:
    """
    This function creates a JSON object that can be sent as update request to DSP-API.

    Args:
        res_iri: the iri of the resource
        resource_in_triplestore: the resource existing in the triplestore
        stashed_resource: the same resource from the stash
        link_prop_in_triplestore: the link property in the triplestore
        new_xmltext: the new xml text with the IRIs
        link_prop_name: the name of the link property

    Returns:
        json string
    """
    jsonobj = {
        "@id": res_iri,
        "@type": stashed_resource.restype,
        link_prop_name: {
            "@id": link_prop_in_triplestore["@id"],
            "@type": "knora-api:TextValue",
            "knora-api:textValueAsXml": new_xmltext,
            "knora-api:textValueHasMapping": {"@id": "http://rdfh.ch/standoff/mappings/StandardMapping"},
        },
        "@context": resource_in_triplestore["@context"],
    }
    return json.dumps(jsonobj, indent=4, separators=(",", ": "), cls=KnoraStandoffXmlEncoder)


def upload_single_link_xml_property(
    link_prop_in_triplestore: Any,
    res_iri: str,
    stashed_resource: XMLResource,
    resource_in_triplestore: Any,
    link_prop: XMLProperty,
    hash_to_value: dict[str, KnoraStandoffXml],
    id2iri_mapping: dict[str, str],
    nonapplied_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    verbose: bool,
    con: Connection,
) -> dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]]:
    """
    This function uploads a single xml link property, which was previously stashed.

    Args:
        link_prop_in_triplestore: the link property from the triplestore
        res_iri: the iri of the resource
        stashed_resource: the stashed resource
        resource_in_triplestore: the resource retrieved from the triplestore
        link_prop: the name of the link property
        hash_to_value: the has value of the xml text
        id2iri_mapping: the dictionary with the internal ids and the new IRIs
        nonapplied_xml_texts: the dictionary with the stashes
        verbose: what is printed out
        con: the connection to the triplestore

    Returns:
        The stash dictionary with the newly uploaded resource removed.
        If the upload was not sucessfull it returns the dictionary as it was before.
    """
    xmltext_in_triplestore = link_prop_in_triplestore.get("knora-api:textValueAsXml")
    if not xmltext_in_triplestore:
        # no action necessary: this property will remain in nonapplied_xml_texts,
        # which will be handled by the caller
        return nonapplied_xml_texts

    # strip all xml tags from the old xmltext, so that the pure text itself remains
    text_hash_value = _get_text_hash_value(xmltext_in_triplestore)

    # if the pure text is a hash, the replacement must be made
    # this hash originates from _stash_circular_references(), and identifies the XML texts
    if text_hash_value not in hash_to_value:
        # no action necessary: this property will remain in nonapplied_xml_texts,
        # which will be handled by the caller
        return nonapplied_xml_texts

    new_xmltext = _replace_internal_ids_with_iris(
        pure_text=text_hash_value, id2iri_mapping=id2iri_mapping, hash_to_value=hash_to_value
    )

    # prepare API call
    jsondata = _create_XMLResource_json_object_to_update(
        res_iri=res_iri,
        resource_in_triplestore=resource_in_triplestore,
        stashed_resource=stashed_resource,
        link_prop_in_triplestore=link_prop_in_triplestore,
        new_xmltext=new_xmltext,
        link_prop_name=link_prop.name,
    )

    # execute API call
    try:
        try_network_action(con.put, route="/v2/values", jsondata=jsondata)
    except BaseError as err:
        _log_unable_to_upload_xml_resource(
            received_error=err, stashed_resource=stashed_resource, all_link_props=link_prop
        )
        return nonapplied_xml_texts
    if verbose:
        print(f'  Successfully uploaded xml text of "{link_prop.name}"\n')
        logger.info(f'  Successfully uploaded xml text of "{link_prop.name}"\n')
    nonapplied_xml_texts[stashed_resource][link_prop].pop(text_hash_value)
    return nonapplied_xml_texts


def upload_all_link_props_of_single_resource(
    res_iri: str,
    stashed_resource: XMLResource,
    resource_in_triplestore: dict[str, Any],
    link_prop: XMLProperty,
    hash_to_value: dict[str, KnoraStandoffXml],
    id2iri_mapping: dict[str, str],
    nonapplied_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    verbose: bool,
    con: Connection,
) -> dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]]:
    """
    This function takes one resource and extracts all the link properties of that resource.
    It sends all the resources to the DSP-API.

    Args:
        res_iri: resource IRI
        stashed_resource: the resource from the stash
        resource_in_triplestore: the resource from the triplestore
        link_prop: the link property
        hash_to_value: the dictionary which stored the hashes and their corresponding text
        id2iri_mapping: the dictionary that has the internal ids and IRIs to map
        nonapplied_xml_texts: the dictionary which contains the unprocessed resources
        verbose: how much information should be printed
        con: connection to the api

    Returns:
        the dictionary which contains the unprocessed resources
    """
    all_link_props_in_triplestore = resource_in_triplestore[link_prop.name]

    if not isinstance(all_link_props_in_triplestore, list):
        all_link_props_in_triplestore = [all_link_props_in_triplestore]

    for link_prop_in_triplestore in all_link_props_in_triplestore:
        nonapplied_xml_texts = upload_single_link_xml_property(
            link_prop_in_triplestore=link_prop_in_triplestore,
            res_iri=res_iri,
            stashed_resource=stashed_resource,
            resource_in_triplestore=resource_in_triplestore,
            link_prop=link_prop,
            hash_to_value=hash_to_value,
            id2iri_mapping=id2iri_mapping,
            nonapplied_xml_texts=nonapplied_xml_texts,
            verbose=verbose,
            con=con,
        )
    return nonapplied_xml_texts
