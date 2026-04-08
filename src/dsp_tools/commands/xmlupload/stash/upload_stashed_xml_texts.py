from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import cast

from loguru import logger
from rdflib import RDF
from rdflib import Graph
from rdflib import URIRef
from tqdm import tqdm

from dsp_tools.clients.resource_client import ResourceClient
from dsp_tools.clients.value_client import ValueClient
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.make_rdf_graph.jsonld_utils import serialise_jsonld_for_value
from dsp_tools.commands.xmlupload.make_rdf_graph.make_values import make_richtext_value_graph
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStash
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.utils.exceptions import DspToolsRequestException
from dsp_tools.utils.request_utils import ResponseCodeAndText


def upload_stashed_xml_texts(
    upload_state: UploadState, val_client: ValueClient, resource_client: ResourceClient
) -> None:
    """
    After all resources are uploaded, the stashed xml texts must be applied to their resources in DSP.
    The upload state is updated accordingly, as a side effect.

    Args:
        upload_state: the current state of the upload
        val_client: value Client
        resource_client: Resource Client
    """
    logger.info("Upload the stashed XML texts...")
    upload_state.pending_stash = cast(Stash, upload_state.pending_stash)
    standoff_stash = cast(StandoffStash, upload_state.pending_stash.standoff_stash)

    progress_bar = tqdm(
        standoff_stash.res_2_stash_items.copy().items(), desc="Upload stashed XML texts", dynamic_ncols=True
    )
    for res_id, stash_items in progress_bar:
        res_iri = upload_state.iri_resolver.get(res_id)
        if not res_iri:
            # resource could not be uploaded to DSP, so the stash cannot be uploaded either
            # no action necessary: this resource will remain in the list of not uploaded stash items,
            # which will be handled by the caller
            continue

        try:
            request_result = resource_client.get_resource(res_iri)
            if isinstance(request_result, ResponseCodeAndText):
                _log_unable_to_retrieve_resource(resource=res_id, msg=request_result.text)
                continue
            else:
                resource_in_triplestore = request_result
        except DspToolsRequestException as err:
            _log_unable_to_retrieve_resource(resource=res_id, msg=err.message)
            continue

        logger.info(f"  Upload XML text(s) of resource '{res_id}'...")
        for stash_item in stash_items:
            value_iri = _get_value_iri(stash_item.value.prop_iri, resource_in_triplestore, stash_item.value.value_uuid)
            if not value_iri:
                continue
            if _upload_stash_item(
                stash_item=stash_item,
                res_iri=res_iri,
                value_iri=value_iri,
                iri_resolver=upload_state.iri_resolver,
                val_client=val_client,
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
    value_iri: str,
    iri_resolver: IriResolver,
    val_client: ValueClient,
) -> bool:
    """
    Upload a single stashed xml text to DSP.

    Args:
        stash_item: the stashed text value to upload
        res_iri: the iri of the resource
        value_iri: the iri of the value
        iri_resolver: resolver to map ids from the XML file to IRIs in DSP
        val_client: Value Client

    Returns:
        True, if the upload was successful, False otherwise
    """
    payload = _serialise_richtext_for_update(
        stash_item=stash_item,
        value_iri_str=value_iri,
        res_iri_str=res_iri,
        iri_resolver=iri_resolver,
    )
    upload_problem = val_client.replace_existing_value(payload)
    if upload_problem:
        _log_unable_to_upload_xml_resource(upload_problem.text, stash_item.res_id, stash_item.value.prop_iri)
        return False
    logger.debug(f'  Successfully uploaded xml text of "{stash_item.value.prop_iri}"')
    return True


def _serialise_richtext_for_update(
    stash_item: StandoffStashItem, value_iri_str: str, res_iri_str: str, iri_resolver: IriResolver
) -> dict[str, Any]:
    graph = _make_richtext_update_graph(
        stash_item=stash_item,
        value_iri_str=value_iri_str,
        res_iri_str=res_iri_str,
        iri_resolver=iri_resolver,
    )
    return serialise_jsonld_for_value(graph, res_iri_str)


def _make_richtext_update_graph(
    stash_item: StandoffStashItem, value_iri_str: str, res_iri_str: str, iri_resolver: IriResolver
) -> Graph:
    res_iri = URIRef(res_iri_str)
    value_iri = URIRef(value_iri_str)
    val_graph = make_richtext_value_graph(
        val=stash_item.value,
        val_node=value_iri,
        res_node=res_iri,
        iri_resolver=iri_resolver,
    )
    val_graph.add((res_iri, RDF.type, URIRef(stash_item.res_type)))
    return val_graph


def _log_unable_to_retrieve_resource(
    resource: str,
    msg: str,
) -> None:
    """
    This function logs the error if it is not possible to retrieve the resource.

    Args:
        resource: the resource id
        msg: the error
    """
    # print the message to keep track of the cause for the failure
    # apart from that; no action is necessary:
    # this resource will remain in nonapplied_xml_texts, which will be handled by the caller
    err_msg = (
        f"Unable to upload XML texts of resource '{resource}', "
        "because the resource cannot be retrieved from the DSP server."
    )
    print(f"{datetime.now()}:   WARNING: {err_msg} Original error message: {msg}")
    logger.error(err_msg)


def _log_unable_to_upload_xml_resource(
    msg: str,
    stashed_resource_id: str,
    prop_name: str,
) -> None:
    """
    This function logs if it is not possible to upload a xml resource.

    Args:
        msg: message
        stashed_resource_id: id of the resource
        prop_name: name of the property
    """
    # print the message to keep track of the cause for the failure
    # apart from that; no action is necessary:
    # this resource will remain in nonapplied_xml_texts, which will be handled by the caller
    err_msg = f"Unable to upload the xml text of '{prop_name}' of resource '{stashed_resource_id}'."
    print(f"{datetime.now()}:     WARNING: {err_msg} Original error message: {msg}")
    logger.error(err_msg)
