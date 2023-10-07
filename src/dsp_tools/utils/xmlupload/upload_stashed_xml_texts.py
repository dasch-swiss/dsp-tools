from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote_plus

import regex

from dsp_tools.models.connection import Connection
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.resource import KnoraStandoffXmlEncoder
from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlproperty import XMLProperty
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action
from dsp_tools.utils.xmlupload.stash.stash_models import StandoffStash, StandoffStashItem

logger = get_logger(__name__)


def _log_unable_to_retrieve_resource(
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
    stashed_resource_id: str,
    prop_name: str,
) -> None:
    """
    This function logs if it is not possible to upload a xml resource.

    Args:
        received_error: Error received
        stashed_resource: resource that is stashed
        all_link_props: all the link properties from that resource
    """
    # print the message to keep track of the cause for the failure
    # apart from that; no action is necessary:
    # this resource will remain in nonapplied_xml_texts, which will be handled by the caller
    orig_err_msg = received_error.orig_err_msg_from_api or received_error.message
    err_msg = f"Unable to upload the xml text of '{prop_name}' of resource '{stashed_resource_id}'."
    print(f"    WARNING: {err_msg} Original error message: {orig_err_msg}")
    logger.warning(err_msg, exc_info=True)


def _log_iri_does_not_exist_error(
    received_error: KeyError,
    stashed_resource: XMLResource,
    all_link_props: XMLProperty,
) -> None:
    """
    This function logs if it is not possible to upload an XML resource
    if a linked resource does not have an IRI in the triplestore.

    Args:
        received_error: Error received
        stashed_resource: resource that is stashed
        all_link_props: all the link properties from that resource
    """
    err_msg = (
        f"Unable to upload the xml text of '{all_link_props.name}' of resource '{stashed_resource.id}'"
        f"because the resource with the internal id '{received_error.args[0]}' does not exist in the triplestore."
    )
    print(f"    WARNING: {err_msg}")
    logger.warning(err_msg, exc_info=True)


def _get_text_hash_value(old_xmltext: str) -> str:
    """
    This function extracts the hash values in the text

    Args:
        old_xmltext: Text with hash values.

    Returns:
        hash values
    """
    return regex.sub(r"(<\?xml.+>\s*)?<text>\s*(.+)\s*<\/text>", r"\2", old_xmltext)


def _replace_internal_ids_with_iris(
    id2iri_mapping: dict[str, str],
    xml_with_id: KnoraStandoffXml,
    id_set: set[str],
) -> KnoraStandoffXml:
    """
    This function takes an XML string and a set with internal ids that are referenced in salsah-links in that string.
    It replaces all internal ids of that set with the corresponding iri according to the mapping dictionary.

    Args:
        id2iri_mapping: dictionary with id to iri mapping
        xml_with_id: KnoraStandoffXml with the string that should have replacements
        id_set: set of ids that are in the string

    Returns:
        the xml value with the old ids replaced
    """
    for internal_id in id_set:
        xml_with_id.replace_one_id_with_iri_in_salsah_link(
            internal_id=internal_id,
            iri=id2iri_mapping[internal_id],
        )
    return xml_with_id


def _create_XMLResource_json_object_to_update(
    res_iri: str,
    rey_type: str,
    link_prop_name: str,
    value_iri: str,
    new_xmltext: KnoraStandoffXml,
    context: dict[str, str],
) -> str:
    """
    This function creates a JSON object that can be sent as update request to DSP-API.

    Args:
        res_iri: the iri of the resource
        resource_in_triplestore: the resource existing in the triplestore
        stashed_resource: the same resource from the stash
        link_prop_in_triplestore: the link property in the triplestore
        new_xmltext: The KnoraStandOffXml with replaced ids
        link_prop_name: the name of the link property

    Returns:
        json string
    """
    jsonobj = {
        "@id": res_iri,
        "@type": rey_type,
        link_prop_name: {
            "@id": value_iri,
            "@type": "knora-api:TextValue",
            "knora-api:textValueAsXml": new_xmltext,
            "knora-api:textValueHasMapping": {"@id": "http://rdfh.ch/standoff/mappings/StandardMapping"},
        },
        "@context": context,
    }
    return json.dumps(jsonobj, indent=4, separators=(",", ": "), cls=KnoraStandoffXmlEncoder)


def upload_stashed_xml_texts(
    verbose: bool,
    id2iri_mapping: dict[str, str],
    con: Connection,
    stashed_xml_texts: StandoffStash,
) -> StandoffStash | None:
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
    not_uploaded: list[tuple[XMLResource, StandoffStashItem]] = []
    for res_id, stash_items in stashed_xml_texts.res_2_stash_items.items():
        res_iri = id2iri_mapping.get(res_id)
        if not res_iri:
            # resource could not be uploaded to DSP, so the stash cannot be uploaded either
            # no action necessary: this resource will remain in nonapplied_xml_texts,
            # which will be handled by the caller
            continue
        xmlres: XMLResource = stashed_xml_texts.res_2_xmlres[res_id]
        try:
            resource_in_triplestore = try_network_action(con.get, route=f"/v2/resources/{quote_plus(res_iri)}")
        except BaseError as err:
            _log_unable_to_retrieve_resource(resource=xmlres, received_error=err)
            continue
        if verbose:
            print(f'  Upload XML text(s) of resource "{res_id}"...')
        logger.debug(f'  Upload XML text(s) of resource "{res_id}"...')
        for stash_item in stash_items:
            success = _upload_stash_item(
                stash_item=stash_item,
                res_iri=res_iri,
                res_type=xmlres.restype,
                res_id=res_id,
                resource_in_triplestore=resource_in_triplestore,
                id2iri_mapping=id2iri_mapping,
                verbose=verbose,
                con=con,
            )
            if not success:
                not_uploaded.append((xmlres, stash_item))
    return StandoffStash.make(not_uploaded)


def _upload_stash_item(
    stash_item: StandoffStashItem,
    res_iri: str,
    res_type: str,
    res_id: str,
    resource_in_triplestore: dict[str, Any],
    id2iri_mapping: dict[str, str],
    verbose: bool,
    con: Connection,
) -> bool:
    """..."""
    values_on_server = resource_in_triplestore.get(stash_item.link_prop.name)
    if not isinstance(values_on_server, list):
        values_on_server = [values_on_server]

    # get the IRI of the value that contains the UUID in its text
    text_and_iris = ((v["knora-api:textValueAsXml"], v["@id"]) for v in values_on_server)
    value_iri = next((iri for text, iri in text_and_iris if stash_item.uuid in text), None)
    assert value_iri  # TODO: handle this case properly # pylint: disable=fixme
    adjusted_text_value = _replace_internal_ids_with_iris(
        id2iri_mapping, stash_item.value, stash_item.value.find_ids_referenced_in_salsah_links()
    )

    jsondata = _create_XMLResource_json_object_to_update(
        res_iri,
        res_type,
        stash_item.link_prop.name,
        value_iri,
        adjusted_text_value,
        resource_in_triplestore["@context"],
    )
    try:
        try_network_action(con.put, route="/v2/values", jsondata=jsondata)
    except BaseError as err:
        _log_unable_to_upload_xml_resource(err, res_id, stash_item.link_prop.name)
        return False
    if verbose:
        print(f'  Successfully uploaded xml text of "{stash_item.link_prop.name}"\n')
    logger.debug(f'  Successfully uploaded xml text of "{stash_item.link_prop.name}"\n')
    return True


def purge_stashed_xml_texts(
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
