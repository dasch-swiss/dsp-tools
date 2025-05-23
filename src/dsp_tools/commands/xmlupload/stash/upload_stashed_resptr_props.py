from __future__ import annotations

from datetime import datetime
from typing import cast

from loguru import logger
from rdflib import RDF
from rdflib import BNode
from rdflib import Graph
from rdflib import URIRef
from tqdm import tqdm

from dsp_tools.clients.connection import Connection
from dsp_tools.commands.xmlupload.make_rdf_graph.jsonld_utils import serialise_jsonld_for_value
from dsp_tools.commands.xmlupload.make_rdf_graph.make_values import make_link_value_graph
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStash
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.error.exceptions import BaseError


def upload_stashed_resptr_props(
    upload_state: UploadState,
    con: Connection,
) -> None:
    """
    After all resources are uploaded, the stashed resptr props must be applied to their resources in DSP.
    The upload state is updated accordingly, as a side effect.

    Args:
        upload_state: the current state of the upload
        con: connection to DSP
    """
    logger.info("Upload the stashed links...")
    upload_state.pending_stash = cast(Stash, upload_state.pending_stash)
    link_value_stash = cast(LinkValueStash, upload_state.pending_stash.link_value_stash)
    progress_bar = tqdm(
        link_value_stash.res_2_stash_items.copy().items(), desc="Upload the stashed links", dynamic_ncols=True
    )
    for res_id, stash_items in progress_bar:
        res_iri = upload_state.iri_resolver.get(res_id)
        if not res_iri:
            # resource could not be uploaded to DSP, so the stash cannot be uploaded either
            # no action necessary: this resource will remain in nonapplied_resptr_props,
            # which will be handled by the caller
            continue
        logger.info(f"  Upload resptrs of resource '{res_id}'...")
        for stash_item in reversed(stash_items):
            # reversed avoids any problems caused by removing from the list we loop over at the same time
            target_iri = upload_state.iri_resolver.get(stash_item.value.value)
            if not target_iri:
                continue
            if _upload_stash_item(stash_item, res_iri, target_iri, con):
                link_value_stash.res_2_stash_items[res_id].remove(stash_item)
        # remove res_id if all stash items were uploaded
        if not link_value_stash.res_2_stash_items[res_id]:
            del link_value_stash.res_2_stash_items[res_id]


def _upload_stash_item(
    stash: LinkValueStashItem,
    res_iri: str,
    target_iri: str,
    con: Connection,
) -> bool:
    """
    Upload a single stashed link value to DSP.

    Args:
        stash: the stashed link value to upload
        res_iri: the iri of the resource
        target_iri: the iri of the target resource
        con: connection to DSP

    Returns:
        True, if the upload was successful, False otherwise
    """
    graph = _make_link_value_create_graph(stash, res_iri, target_iri)
    payload = serialise_jsonld_for_value(graph, res_iri)
    try:
        con.post(route="/v2/values", data=payload)
    except BaseError as err:
        _log_unable_to_upload_link_value(err.message, stash.res_id, stash.value.prop_iri)
        return False
    logger.debug(f'  Successfully uploaded resptr links of "{stash.value.prop_iri}"')
    return True


def _make_link_value_create_graph(
    stash: LinkValueStashItem,
    res_iri_str: str,
    target_iri: str,
) -> Graph:
    """This function creates a JSON object that can be sent as an update request to the DSP-API."""
    val_bn = BNode()
    res_iri = URIRef(res_iri_str)
    graph = make_link_value_graph(stash.value, val_bn, res_iri, URIRef(target_iri))
    graph.add((res_iri, RDF.type, URIRef(stash.res_type)))
    return graph


def _log_unable_to_upload_link_value(msg: str, res_id: str, prop_name: str) -> None:
    err_msg = f"Unable to upload the resptr prop of '{prop_name}' of resource '{res_id}'."
    print(f"{datetime.now()}:     WARNING: {err_msg} Original error message: {msg}")
    logger.error(err_msg)
