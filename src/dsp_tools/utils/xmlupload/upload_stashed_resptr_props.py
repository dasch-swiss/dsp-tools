from __future__ import annotations

import json
from urllib.parse import quote_plus

from dsp_tools.models.connection import Connection
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.xmlproperty import XMLProperty
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action
from dsp_tools.utils.xmlupload.stash.stash_models import LinkValueStash, LinkValueStashItem

logger = get_logger(__name__)


def upload_stashed_resptr_props(
    verbose: bool,
    id2iri_mapping: dict[str, str],
    con: Connection,
    stashed_resptr_props: LinkValueStash,
) -> LinkValueStash | None:
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

    # XXX: how to handle not found resources. currently nothing happens apart from a warning.
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
        try:
            existing_resource = try_network_action(con.get, route=f"/v2/resources/{quote_plus(res_iri)}")
        except BaseError as err:
            _log_if_unable_to_retrieve_resource(err, res_id)
            continue
        if verbose:
            logger.info(f'  Upload resptrs of resource "{res_id}"...')
        logger.debug(f'  Upload resptrs of resource "{res_id}"...')
        context: dict[str, str] = existing_resource["@context"]
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
        stash_item: the stashed link value to upload
        res_iri: the iri of the resource
        res_type: the type of the resource
        res_id: the internal id of the resource
        id2iri_mapping: mapping of ids from the XML file to IRIs in DSP
        con: connection to DSP
        context: the JSON-LD context of the resource

    Returns:
        True, if the upload was successful, False otherwise
    """
    jsondata = _create_resptr_prop_json_object_to_update(stash, res_iri, target_iri, context)
    try:
        try_network_action(con.put, route="/v2/values", jsondata=jsondata)
    except BaseError as err:
        orig_err_msg = err.orig_err_msg_from_api or err.message
        err_msg = f"Unable to upload the resptr prop of '{stash.prop_name}' of resource '{stash.res_id}'."
        print(f"    WARNING: {err_msg} Original error message: {orig_err_msg}")
        logger.warning(err_msg, exc_info=True)
        return False
    logger.debug(f'  Successfully uploaded xml text of "{stash.prop_name}"\n')
    return True


def _log_if_unable_to_retrieve_resource(
    err: BaseError,
    resource_id: str,
) -> None:
    orig_err_msg = err.orig_err_msg_from_api or err.message
    err_msg = (
        f"Unable to upload resptrs of resource '{resource_id}', "
        "because the resource cannot be retrieved from the DSP server."
    )
    print(f"  WARNING: {err_msg} Original error message: {orig_err_msg}")
    logger.warning(err_msg, exc_info=True)


def _create_resptr_prop_json_object_to_update(
    stash: LinkValueStashItem,
    res_iri: str,
    target_iri: str,
    context: dict[str, str],
) -> str:
    """
    This function creates a JSON object that can be sent as an update request to the DSP-API.
    """
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


def purge_stashed_resptr_props(
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
