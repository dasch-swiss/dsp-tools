from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import quote_plus

from dsp_tools.models.connection import Connection
from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.xmlproperty import XMLProperty
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.shared import try_network_action

logger = get_logger(__name__)


@dataclass(frozen=True)
class LinkStashItem:
    """
    This class holds information about a single stashed (resptr) link.
    """

    res_id: str
    res_iri: str
    res_type: str
    link_name: str
    link_target_iri: str


@dataclass(frozen=True)
class ResourceLinkStash:
    """
    This class holds information about all stashed (resptr) links or a single resource.
    """

    res_id: str
    res_iri: str
    res_type: str
    stash: list[LinkStashItem]


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
            # Apart from that, no action is necessary:
            # this resource will remain in nonapplied_resptr_props, which will be handled by the caller
            _log_if_unable_to_retrieve_resource(err=err, resource=resource)
            continue
        logger.info(f'  Upload resptrs of resource "{resource.id}"...')
        context: dict[str, str] = existing_resource["@context"]
        prop_name_2_prop = {prop.name: prop for prop in resource.properties}
        stash_items = list(_create_stash_items(id2iri_mapping, resource, prop_2_resptrs, res_iri))
        stash = ResourceLinkStash(
            res_id=resource.id,
            res_iri=res_iri,
            res_type=resource.restype,
            stash=stash_items,
        )
        to_remove = _upload_all_resptr_props_of_single_resource(
            stash=stash,
            con=con,
            context=context,
            verbose=verbose,
        )
        for link_name, res_id in to_remove:
            link_prop = prop_name_2_prop[link_name]
            nonapplied_resptr_props[resource][link_prop].remove(res_id)

    # make a purged version of nonapplied_resptr_props, without empty entries
    nonapplied_resptr_props = purge_stashed_resptr_props(
        stashed_resptr_props=nonapplied_resptr_props,
        id2iri_mapping=id2iri_mapping,
    )
    return nonapplied_resptr_props


def _create_stash_items(
    id2iri_mapping: dict[str, str],
    resource: XMLResource,
    prop_2_resptrs: dict[XMLProperty, list[str]],
    res_iri: str,
) -> Iterable[LinkStashItem]:
    for link_prop, resptrs in prop_2_resptrs.items():
        for resptr in resptrs:
            yield LinkStashItem(
                res_id=resptr,
                res_iri=res_iri,
                res_type=resource.restype,
                link_name=link_prop.name,
                link_target_iri=id2iri_mapping.get(resptr, resptr),
            )


def _upload_all_resptr_props_of_single_resource(
    stash: ResourceLinkStash,
    con: Connection,
    context: dict[str, str],
    verbose: bool,
) -> list[tuple[str, str]]:
    """
    This function takes one resource stashed resource and resptr-props that are specific to a property.
    It sends them to the DSP-API and removes them from the nonapplied_resptr_props dictionary.

    Args:
        resource_in_triplestore: The resource retried from the triplestore
        stashed_resource: The resource from the stash
        link_prop: the property object to which the stashed resptrs belong to
        res_iri: the IRI as given by the DSP-API
        resptrs: List with all the resptr-props for that one property
        id2iri_mapping: mapping of internal id to the IRI from the DSP-API
        con: Connection to the DSP-API
        nonapplied_resptr_props: stashed resources
        verbose: If True, more information is logged

    Returns:
        ...
    """
    res: list[tuple[str, str]] = []
    for stash_item in stash.stash:
        jsondata = _create_resptr_prop_json_object_to_update(stash_item, context)
        try:
            try_network_action(con.post, route="/v2/values", jsondata=jsondata)
        except BaseError as err:
            # print the message to keep track of the cause for the failure.
            # Apart from that, no action is necessary:
            # this resource will remain in nonapplied_resptr_props, which will be handled by the caller
            orig_err_msg = err.orig_err_msg_from_api or err.message
            err_msg = f"Unable to upload the resptr prop of '{stash_item.link_name}' of resource '{stash.res_id}'."
            print(f"    WARNING: {err_msg} Original error message: {orig_err_msg}")
            logger.warning(err_msg, exc_info=True)
            continue
        if verbose:
            print(f'  Successfully uploaded resptr-prop of "{stash_item.link_name}". Value: {stash_item.res_id}')
        logger.debug(f'Successfully uploaded resptr-prop of "{stash_item.link_name}". Value: {stash_item.res_id}')
        res.append((stash_item.link_name, stash_item.res_id))
    return res


def _log_if_unable_to_retrieve_resource(
    err: BaseError,
    resource: XMLResource,
) -> None:
    orig_err_msg = err.orig_err_msg_from_api or err.message
    err_msg = (
        f"Unable to upload resptrs of resource '{resource.id}', "
        "because the resource cannot be retrieved from the DSP server."
    )
    print(f"  WARNING: {err_msg} Original error message: {orig_err_msg}")
    logger.warning(err_msg, exc_info=True)


def _create_resptr_prop_json_object_to_update(
    stash: LinkStashItem,
    context: dict[str, str],
) -> str:
    """
    This function creates a JSON object that can be sent as an update request to the DSP-API.

    Args:
        stashed_resource: Resource that contains the information to be sent to the DSP-API
        resource_in_triplestore: Resource that is retrieved from the DSP-API
        property_name: name of the property with which the resources are linked
        link_prop: XMLProperty with the information
        res_iri: IRI from the DSP-API
        id2iri_mapping: mapping of the internal id to the IRI

    Returns:
        A JSON object that is suitable for the upload.
    """
    jsonobj = {
        "@id": stash.res_iri,
        "@type": stash.res_type,
        f"{stash.link_name}Value": {
            "@type": "knora-api:LinkValue",
            "knora-api:linkValueHasTargetIri": {
                # if target doesn't exist in DSP, send the (invalid) resource ID of target to DSP,
                # which will produce an understandable error message
                "@id": stash.link_target_iri
            },
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
