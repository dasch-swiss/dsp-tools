from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from urllib.parse import quote_plus

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.value import FormattedTextValue
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStash, StandoffStashItem
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action

logger = get_logger(__name__)


def _log_unable_to_retrieve_resource(
    resource: str,
    received_error: BaseError,
) -> None:
    """
    This function logs the error if it is not possible to retrieve the resource.

    Args:
        resource: the resource id
        received_error: the error
    """
    # print the message to keep track of the cause for the failure
    # apart from that; no action is necessary:
    # this resource will remain in nonapplied_xml_texts, which will be handled by the caller
    orig_err_msg = received_error.orig_err_msg_from_api or received_error.message
    err_msg = (
        f"Unable to upload XML texts of resource '{resource}', "
        "because the resource cannot be retrieved from the DSP server."
    )
    print(f"{datetime.now()}:   WARNING: {err_msg} Original error message: {orig_err_msg}")
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
        stashed_resource_id: id of the resource
        prop_name: name of the property
    """
    # print the message to keep track of the cause for the failure
    # apart from that; no action is necessary:
    # this resource will remain in nonapplied_xml_texts, which will be handled by the caller
    orig_err_msg = received_error.orig_err_msg_from_api or received_error.message
    err_msg = f"Unable to upload the xml text of '{prop_name}' of resource '{stashed_resource_id}'."
    print(f"{datetime.now()}:     WARNING: {err_msg} Original error message: {orig_err_msg}")
    logger.warning(err_msg, exc_info=True)


def _create_XMLResource_json_object_to_update(
    res_iri: str,
    res_type: str,
    link_prop_name: str,
    value_iri: str,
    new_xmltext: FormattedTextValue,
    context: dict[str, str],
) -> str:
    """
    This function creates a JSON object that can be sent as update request to DSP-API.

    Args:
        res_iri: the iri of the resource
        res_type: the type of the resource
        link_prop_name: the name of the link property
        value_iri: the iri of the value
        new_xmltext: the new xml text to be uploaded
        context: the JSON-LD context of the resource

    Returns:
        json string
    """
    jsonobj = {
        "@id": res_iri,
        "@type": res_type,
        link_prop_name: {
            "@id": value_iri,
            "@type": "knora-api:TextValue",
            "knora-api:textValueAsXml": '<?xml version="1.0" encoding="UTF-8"?>\n<text>' + str(new_xmltext) + "</text>",
            "knora-api:textValueHasMapping": {"@id": "http://rdfh.ch/standoff/mappings/StandardMapping"},
        },
        "@context": context,
    }
    return json.dumps(jsonobj, indent=4, separators=(",", ": "))


def upload_stashed_xml_texts(
    verbose: bool,
    iri_resolver: IriResolver,
    con: Connection,
    stashed_xml_texts: StandoffStash,
) -> StandoffStash | None:
    """
    After all resources are uploaded, the stashed xml texts must be applied to their resources in DSP.

    Args:
        verbose: bool
        iri_resolver: resolver to map ids from the XML file to IRIs in DSP
        con: connection to DSP
        stashed_xml_texts: all xml texts that have been stashed

    Returns:
        nonapplied_xml_texts: the xml texts that could not be uploaded
    """

    print(f"{datetime.now()}: Upload the stashed XML texts...")
    logger.info("Upload the stashed XML texts...")
    not_uploaded: list[StandoffStashItem] = []
    for res_id, stash_items in stashed_xml_texts.res_2_stash_items.items():
        res_iri = iri_resolver.get(res_id)
        if not res_iri:
            # resource could not be uploaded to DSP, so the stash cannot be uploaded either
            # no action necessary: this resource will remain in nonapplied_xml_texts,
            # which will be handled by the caller
            continue
        # xmlres: XMLResource = stashed_xml_texts.res_2_xmlres[res_id]
        try:
            resource_in_triplestore = try_network_action(con.get, route=f"/v2/resources/{quote_plus(res_iri)}")
        except BaseError as err:
            _log_unable_to_retrieve_resource(resource=res_id, received_error=err)
            continue
        if verbose:
            print(f"{datetime.now()}:   Upload XML text(s) of resource '{res_id}'...")
        logger.info(f"  Upload XML text(s) of resource '{res_id}'...")
        context = resource_in_triplestore["@context"]
        for stash_item in stash_items:
            value_iri = _get_value_iri(stash_item.prop_name, resource_in_triplestore, stash_item.uuid)
            if not value_iri:
                not_uploaded.append(stash_item)
                continue
            success = _upload_stash_item(
                stash_item=stash_item,
                res_iri=res_iri,
                res_type=stash_item.res_type,
                res_id=res_id,
                value_iri=value_iri,
                iri_resolver=iri_resolver,
                con=con,
                context=context,
            )
            if not success:
                not_uploaded.append(stash_item)
    return StandoffStash.make(not_uploaded)


def _get_value_iri(
    property_name: str,
    resource: dict[str, Any],
    uuid: str,
) -> str | None:
    values_on_server = resource.get(property_name)
    if not isinstance(values_on_server, list):
        values_on_server = [values_on_server]

    # get the IRI of the value that contains the UUID in its text
    text_and_iris = ((v["knora-api:textValueAsXml"], v["@id"]) for v in values_on_server)
    value_iri: str | None = next((iri for text, iri in text_and_iris if uuid in text), None)
    # in case that "value_iri" is None, the value that contains the UUID in its text does not exist in DSP
    # no action necessary: this resource will remain in nonapplied_xml_texts,
    # which will be handled by the caller
    return value_iri


def _upload_stash_item(
    stash_item: StandoffStashItem,
    res_iri: str,
    res_type: str,
    res_id: str,
    value_iri: str,
    iri_resolver: IriResolver,
    con: Connection,
    context: dict[str, str],
) -> bool:
    """
    Upload a single stashed xml text to DSP.

    Args:
        stash_item: the stashed text value to upload
        res_iri: the iri of the resource
        res_type: the type of the resource
        res_id: the internal id of the resource
        value_iri: the iri of the value
        iri_resolver: resolver to map ids from the XML file to IRIs in DSP
        con: connection to DSP
        context: the JSON-LD context of the resource

    Returns:
        True, if the upload was successful, False otherwise
    """
    adjusted_text_value = stash_item.value.with_iris(iri_resolver)
    jsondata = _create_XMLResource_json_object_to_update(
        res_iri,
        res_type,
        stash_item.prop_name,
        value_iri,
        adjusted_text_value,
        context,
    )
    try:
        try_network_action(con.put, route="/v2/values", jsondata=jsondata)
    except BaseError as err:
        _log_unable_to_upload_xml_resource(err, res_id, stash_item.prop_name)
        return False
    logger.debug(f'  Successfully uploaded xml text of "{stash_item.prop_name}"')
    return True
