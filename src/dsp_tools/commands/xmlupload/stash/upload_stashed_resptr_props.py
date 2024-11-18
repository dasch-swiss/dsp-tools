from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import cast

from loguru import logger

from dsp_tools.commands.xmlupload.models.namespace_context import JSONLDContext
from dsp_tools.commands.xmlupload.models.upload_state import UploadState
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStash
from dsp_tools.commands.xmlupload.stash.stash_models import LinkValueStashItem
from dsp_tools.commands.xmlupload.stash.stash_models import Stash
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.connection import Connection


def upload_stashed_resptr_props(
    upload_state: UploadState,
    con: Connection,
    jsonld_context: JSONLDContext,
) -> None:
    """
    After all resources are uploaded, the stashed resptr props must be applied to their resources in DSP.
    The upload state is updated accordingly, as a side effect.

    Args:
        upload_state: the current state of the upload
        con: connection to DSP
        jsonld_context: the JSON-LD context of the resource
    """

    print(f"{datetime.now()}: Upload the stashed resptrs...")
    logger.info("Upload the stashed resptrs...")
    upload_state.pending_stash = cast(Stash, upload_state.pending_stash)
    link_value_stash = cast(LinkValueStash, upload_state.pending_stash.link_value_stash)
    for res_id, stash_items in link_value_stash.res_2_stash_items.copy().items():
        res_iri = upload_state.iri_resolver.get(res_id)
        if not res_iri:
            # resource could not be uploaded to DSP, so the stash cannot be uploaded either
            # no action necessary: this resource will remain in nonapplied_resptr_props,
            # which will be handled by the caller
            continue
        print(f"{datetime.now()}:   Upload resptrs of resource '{res_id}'...")
        logger.info(f"  Upload resptrs of resource '{res_id}'...")
        for stash_item in reversed(stash_items):
            # reversed avoids any problems caused by removing from the list we loop over at the same time
            target_iri = upload_state.iri_resolver.get(stash_item.target_id)
            if not target_iri:
                continue
            if _upload_stash_item(stash_item, res_iri, target_iri, con, jsonld_context):
                link_value_stash.res_2_stash_items[res_id].remove(stash_item)
        # remove res_id if all stash items were uploaded
        if not link_value_stash.res_2_stash_items[res_id]:
            del link_value_stash.res_2_stash_items[res_id]


def _upload_stash_item(
    stash: LinkValueStashItem,
    res_iri: str,
    target_iri: str,
    con: Connection,
    jsonld_context: JSONLDContext,
) -> bool:
    """
    Upload a single stashed link value to DSP.

    Args:
        stash: the stashed link value to upload
        res_iri: the iri of the resource
        target_iri: the iri of the target resource
        con: connection to DSP
        jsonld_context: the JSON-LD context of the resource

    Returns:
        True, if the upload was successful, False otherwise
    """
    payload = _create_resptr_prop_json_object_to_update(stash, res_iri, target_iri, jsonld_context)
    try:
        con.post(route="/v2/values", data=payload)
    except BaseError as err:
        _log_unable_to_upload_link_value(err.message, stash.res_id, stash.prop_name)
        return False
    logger.debug(f'  Successfully uploaded resptr links of "{stash.prop_name}"')
    return True


def _log_unable_to_upload_link_value(msg: str, res_id: str, prop_name: str) -> None:
    err_msg = f"Unable to upload the resptr prop of '{prop_name}' of resource '{res_id}'."
    print(f"{datetime.now()}:     WARNING: {err_msg} Original error message: {msg}")
    logger.opt(exception=True).warning(err_msg)


def _create_resptr_prop_json_object_to_update(
    stash: LinkValueStashItem,
    res_iri: str,
    target_iri: str,
    jsonld_context: JSONLDContext,
) -> dict[str, Any]:
    """This function creates a JSON object that can be sent as an update request to the DSP-API."""
    linkVal = {
        "@type": "knora-api:LinkValue",
        "knora-api:linkValueHasTargetIri": {"@id": target_iri},
    }
    if stash.permission:
        linkVal["knora-api:hasPermissions"] = stash.permission
    jsonobj = {
        "@id": res_iri,
        "@type": stash.res_type,
        f"{stash.prop_name}Value": linkVal,
    }
    jsonobj.update(jsonld_context.serialise())
    return jsonobj
