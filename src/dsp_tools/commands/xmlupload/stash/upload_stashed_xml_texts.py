from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import cast
from urllib.parse import quote_plus

from loguru import logger

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStash
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.error.exceptions import BaseError


def upload_stashed_xml_texts(upload_state: UploadState, con: Connection) -> None:
    """
    After all resources are uploaded, the stashed xml texts must be applied to their resources in DSP.
    The upload state is updated accordingly, as a side effect.

    Args:
        upload_state: the current state of the upload
        con: connection to DSP
    """

    print(f"{datetime.now()}: Upload the stashed XML texts...")
    logger.info("Upload the stashed XML texts...")
    upload_state.pending_stash = cast(Stash, upload_state.pending_stash)
    standoff_stash = cast(StandoffStash, upload_state.pending_stash.standoff_stash)
    for res_id, stash_items in standoff_stash.res_2_stash_items.copy().items():
        res_iri = upload_state.iri_resolver.get(res_id)
        if not res_iri:
            # resource could not be uploaded to DSP, so the stash cannot be uploaded either
            # no action necessary: this resource will remain in the list of not uploaded stash items,
            # which will be handled by the caller
            continue
        try:
            resource_in_triplestore = con.get(f"/v2/resources/{quote_plus(res_iri)}")
        except BaseError as err:
            _log_unable_to_retrieve_resource(resource=res_id, received_error=err)
            continue
        print(f"{datetime.now()}:   Upload XML text(s) of resource '{res_id}'...")
        logger.info(f"  Upload XML text(s) of resource '{res_id}'...")
        context = resource_in_triplestore["@context"]
        for stash_item in stash_items:
            value_iri = _get_value_iri(stash_item.prop_name, resource_in_triplestore, stash_item.uuid)
            if not value_iri:
                continue
            if _upload_stash_item(
                stash_item=stash_item,
                res_iri=res_iri,
                res_type=stash_item.res_type,
                res_id=res_id,
                value_iri=value_iri,
                iri_resolver=upload_state.iri_resolver,
                con=con,
                context=context,
            ):
                standoff_stash.res_2_stash_items[res_id].remove(stash_item)
        if not standoff_stash.res_2_stash_items[res_id]:
            standoff_stash.res_2_stash_items.pop(res_id)


def _get_value_iri(
    property_name: str,
    resource: dict[str, Any],
    uuid: str,
) -> str | None:
    prefixed_prop = _make_prefixed_prop_from_absolute_iri(property_name)
    values_on_server = resource.get(prefixed_prop)
    if not isinstance(values_on_server, list):
        values_on_server = [values_on_server]

    # get the IRI of the value that contains the UUID in its text
    text_and_iris = ((v["knora-api:textValueAsXml"], v["@id"]) for v in values_on_server)
    value_iri: str | None = next((iri for text, iri in text_and_iris if uuid in text), None)
    # in case that "value_iri" is None, the value that contains the UUID in its text does not exist in DSP
    # no action necessary: this resource will remain in nonapplied_xml_texts,
    # which will be handled by the caller
    return value_iri


def _make_prefixed_prop_from_absolute_iri(absolute_iri: str) -> str:
    _, onto, prop = absolute_iri.rsplit("/", 2)
    local_name = prop.split("#")[-1]
    return f"{onto}:{local_name}"


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
    payload = _create_XMLResource_json_object_to_update(
        res_iri,
        res_type,
        stash_item.prop_name,
        value_iri,
        adjusted_text_value,
        stash_item.comment,
        context,
    )
    try:
        con.put(route="/v2/values", data=payload)
    except BaseError as err:
        _log_unable_to_upload_xml_resource(err, res_id, stash_item.prop_name)
        return False
    logger.debug(f'  Successfully uploaded xml text of "{stash_item.prop_name}"')
    return True


def _create_XMLResource_json_object_to_update(
    res_iri: str,
    res_type: str,
    link_prop_name: str,
    value_iri: str,
    new_xmltext: FormattedTextValue,
    comment: str | None,
    context: dict[str, str],
) -> dict[str, Any]:
    prop_json = {
        "@id": value_iri,
        "@type": "knora-api:TextValue",
        "knora-api:textValueAsXml": new_xmltext.as_xml(),
        "knora-api:textValueHasMapping": {"@id": "http://rdfh.ch/standoff/mappings/StandardMapping"},
    }
    if comment:
        prop_json["knora-api:valueHasComment"] = comment
    jsonobj = {
        "@id": res_iri,
        "@type": res_type,
        link_prop_name: prop_json,
        "@context": context,
    }
    return jsonobj


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
    err_msg = (
        f"Unable to upload XML texts of resource '{resource}', "
        "because the resource cannot be retrieved from the DSP server."
    )
    print(f"{datetime.now()}:   WARNING: {err_msg} Original error message: {received_error.message}")
    logger.error(err_msg)


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
    err_msg = f"Unable to upload the xml text of '{prop_name}' of resource '{stashed_resource_id}'."
    print(f"{datetime.now()}:     WARNING: {err_msg} Original error message: {received_error.message}")
    logger.error(err_msg)
