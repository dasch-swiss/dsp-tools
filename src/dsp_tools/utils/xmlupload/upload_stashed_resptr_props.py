from __future__ import annotations

import json

from dsp_tools.connection.connection import Connection
from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action
from dsp_tools.utils.xmlupload.stash.stash_models import LinkValueStash, LinkValueStashItem

logger = get_logger(__name__)


def upload_stashed_resptr_props(
    verbose: bool,
    id2iri_mapping: dict[str, str],
    con: Connection,
    stashed_resptr_props: LinkValueStash,
    context: dict[str, str],
) -> LinkValueStash | None:
    """
    After all resources are uploaded, the stashed resptr props must be applied to their resources in DSP.

    Args:
        verbose: bool
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP
        con: connection to DSP
        stashed_resptr_props: all resptr props that have been stashed
        context: the JSON-LD context of the resource

    Returns:
        nonapplied_resptr_props: the resptr props that could not be uploaded
    """

    print("Upload the stashed resptrs...")
    logger.info("Upload the stashed resptrs...")
    not_uploaded: list[LinkValueStashItem] = []
    for res_id, stash_items in stashed_resptr_props.res_2_stash_items.items():
        if res_id not in id2iri_mapping:
            # resource could not be uploaded to DSP, so the stash cannot be uploaded either
            # no action necessary: this resource will remain in nonapplied_resptr_props,
            # which will be handled by the caller
            continue
        res_iri = id2iri_mapping[res_id]
        if verbose:
            print(f'  Upload resptrs of resource "{res_id}"...')
        logger.debug(f'  Upload resptrs of resource "{res_id}"...')
        for stash_item in stash_items:
            target_iri = id2iri_mapping.get(stash_item.target_id)
            if not target_iri:
                continue
            success = _upload_stash_item(stash_item, res_iri, target_iri, con, context)
            if not success:
                not_uploaded.append(stash_item)
    return LinkValueStash.make(not_uploaded)


def _upload_stash_item(
    stash: LinkValueStashItem,
    res_iri: str,
    target_iri: str,
    con: Connection,
    context: dict[str, str],
) -> bool:
    """
    Upload a single stashed link value to DSP.

    Args:
        stash: the stashed link value to upload
        res_iri: the iri of the resource
        target_iri: the iri of the target resource
        con: connection to DSP
        context: the JSON-LD context of the resource

    Returns:
        True, if the upload was successful, False otherwise
    """
    jsondata = _create_resptr_prop_json_object_to_update(stash, res_iri, target_iri, context)
    try:
        try_network_action(con.post, route="/v2/values", jsondata=jsondata)
    except BaseError as err:
        _log_unable_to_upload_link_value(err.orig_err_msg_from_api or err.message, stash.res_id, stash.prop_name)
        return False
    logger.debug(f'  Successfully uploaded xml text of "{stash.prop_name}"\n')
    return True


def _log_unable_to_upload_link_value(msg: str, res_id: str, prop_name: str) -> None:
    err_msg = f"Unable to upload the resptr prop of '{prop_name}' of resource '{res_id}'."
    print(f"    WARNING: {err_msg} Original error message: {msg}")
    logger.warning(err_msg, exc_info=True)


def _create_resptr_prop_json_object_to_update(
    stash: LinkValueStashItem,
    res_iri: str,
    target_iri: str,
    context: dict[str, str],
) -> str:
    """This function creates a JSON object that can be sent as an update request to the DSP-API."""
    jsonobj = {
        "@id": res_iri,
        "@type": stash.res_type,
        f"{stash.prop_name}Value": {
            "@type": "knora-api:LinkValue",
            "knora-api:linkValueHasTargetIri": {"@id": target_iri},
        },
        "@context": context,
    }
    jsondata = json.dumps(jsonobj, indent=4, separators=(",", ": "))
    return jsondata
