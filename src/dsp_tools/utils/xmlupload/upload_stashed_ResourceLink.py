from __future__ import annotations

import json
from urllib.parse import quote_plus

from dsp_tools.models.connection import Connection
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.xmlproperty import XMLProperty
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action

logger = get_logger(__name__)


def upload_stashed_resptr_props(
    verbose: bool,
    id2iri_mapping: dict[str, str],
    con: Connection,
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]],
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

    print("Upload the stashed resptrs...")
    logger.info("Upload the stashed resptrs...")
    nonapplied_resptr_props = stashed_resptr_props.copy()
    for resource, prop_2_resptrs in stashed_resptr_props.items():
        if resource.id not in id2iri_mapping:
            # resource could not be uploaded to DSP, so the stash cannot be uploaded either
            # no action necessary: this resource will remain in nonapplied_resptr_props,
            # which will be handled by the caller
            continue
        res_iri = id2iri_mapping[resource.id]
        try:
            existing_resource = try_network_action(con.get, route=f"/v2/resources/{quote_plus(res_iri)}")
        except BaseError as err:
            # print the message to keep track of the cause for the failure. Apart from that, no action is necessary:
            # this resource will remain in nonapplied_resptr_props, which will be handled by the caller
            orig_err_msg = err.orig_err_msg_from_api or err.message
            err_msg = (
                f"Unable to upload resptrs of resource '{resource.id}', "
                "because the resource cannot be retrieved from the DSP server."
            )
            print(f"  WARNING: {err_msg} Original error message: {orig_err_msg}")
            logger.warning(err_msg, exc_info=True)
            continue
        print(f'  Upload resptrs of resource "{resource.id}"...')
        logger.info(f'  Upload resptrs of resource "{resource.id}"...')
        for link_prop, resptrs in prop_2_resptrs.items():
            for resptr in resptrs.copy():
                jsonobj = {
                    "@id": res_iri,
                    "@type": resource.restype,
                    f"{link_prop.name}Value": {
                        "@type": "knora-api:LinkValue",
                        "knora-api:linkValueHasTargetIri": {
                            # if target doesn't exist in DSP, send the (invalid) resource ID of target to DSP,
                            # which will produce an understandable error message
                            "@id": id2iri_mapping.get(resptr, resptr)
                        },
                    },
                    "@context": existing_resource["@context"],
                }
                jsondata = json.dumps(jsonobj, indent=4, separators=(",", ": "))
                try:
                    try_network_action(con.post, route="/v2/values", jsondata=jsondata)
                except BaseError as err:
                    # print the message to keep track of the cause for the failure.
                    # Apart from that, no action is necessary:
                    # this resource will remain in nonapplied_resptr_props, which will be handled by the caller
                    orig_err_msg = err.orig_err_msg_from_api or err.message
                    err_msg = f"Unable to upload the resptr prop of '{link_prop.name}' of resource '{resource.id}'."
                    print(f"    WARNING: {err_msg} Original error message: {orig_err_msg}")
                    logger.warning(err_msg, exc_info=True)
                    continue
                nonapplied_resptr_props[resource][link_prop].remove(resptr)
                if verbose:
                    print(f'  Successfully uploaded resptr-prop of "{link_prop.name}". Value: {resptr}')
                    logger.info(f'Successfully uploaded resptr-prop of "{link_prop.name}". Value: {resptr}')

    # make a purged version of nonapplied_resptr_props, without empty entries
    nonapplied_resptr_props = purge_stashed_resptr_props(
        stashed_resptr_props=nonapplied_resptr_props,
        id2iri_mapping=id2iri_mapping,
    )
    return nonapplied_resptr_props


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
