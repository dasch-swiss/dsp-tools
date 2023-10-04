from __future__ import annotations

from datetime import datetime
from typing import cast

import regex

from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlproperty import XMLProperty
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def _stash_circular_references(
    nok_resources: list[XMLResource],
    ok_res_ids: list[str],
    ok_resources: list[XMLResource],
    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]],
) -> tuple[
    list[XMLResource],
    list[str],
    list[XMLResource],
    dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    dict[XMLResource, dict[XMLProperty, list[str]]],
]:
    """
    Raises:
        BaseError
    """
    for res in nok_resources.copy():
        for link_prop in res.get_props_with_links():
            if link_prop.valtype == "text":
                for value in link_prop.values:
                    if value.resrefs and not all(_id in ok_res_ids for _id in value.resrefs):
                        # stash this XML text, replace it by its hash, and remove the
                        # problematic resrefs from the XMLValue's resrefs list
                        value_hash = str(hash(f"{value.value}{datetime.now()}"))
                        if res not in stashed_xml_texts:
                            stashed_xml_texts[res] = {link_prop: {value_hash: cast(KnoraStandoffXml, value.value)}}
                        elif link_prop not in stashed_xml_texts[res]:
                            stashed_xml_texts[res][link_prop] = {value_hash: cast(KnoraStandoffXml, value.value)}
                        else:
                            stashed_xml_texts[res][link_prop][value_hash] = cast(KnoraStandoffXml, value.value)
                        value.value = KnoraStandoffXml(value_hash)
                        value.resrefs = [_id for _id in value.resrefs if _id in ok_res_ids]
            elif link_prop.valtype == "resptr":
                for value in link_prop.values.copy():
                    if value.value not in ok_res_ids:
                        # value.value is the id of the target resource. stash it, then delete it
                        if res not in stashed_resptr_props:
                            stashed_resptr_props[res] = {}
                            stashed_resptr_props[res][link_prop] = [str(value.value)]
                        else:
                            if link_prop not in stashed_resptr_props[res]:
                                stashed_resptr_props[res][link_prop] = [str(value.value)]
                            else:
                                stashed_resptr_props[res][link_prop].append(str(value.value))
                        link_prop.values.remove(value)
            else:
                logger.error("ERROR in remove_circular_references(): link_prop.valtype is neither text nor resptr.")
                raise BaseError("ERROR in remove_circular_references(): link_prop.valtype is neither text nor resptr.")

            if len(link_prop.values) == 0:
                # if all values of a link property have been stashed, the property needs to be removed
                res.properties.remove(link_prop)

        ok_resources.append(res)
        ok_res_ids.append(res.id)
        nok_resources.remove(res)

    return nok_resources, ok_res_ids, ok_resources, stashed_xml_texts, stashed_resptr_props


def remove_circular_references(
    resources: list[XMLResource],
    verbose: bool,
) -> tuple[
    list[XMLResource],
    dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]],
    dict[XMLResource, dict[XMLProperty, list[str]]],
]:
    """
    Temporarily removes problematic resource-references from a list of resources.
    A reference is problematic if it creates a circle (circular references).

    Args:
        resources: list of resources that possibly contain circular references
        verbose: verbose output if True

    Raises:
        BaseError

    Returns:
        list: list of cleaned resources
        stashed_xml_texts: dict with the stashed XML texts
        stashed_resptr_props: dict with the stashed resptr-props
    """

    if verbose:
        print("Checking resources for unresolvable references...")
        logger.info("Checking resources for unresolvable references...")

    stashed_xml_texts: dict[XMLResource, dict[XMLProperty, dict[str, KnoraStandoffXml]]] = {}
    stashed_resptr_props: dict[XMLResource, dict[XMLProperty, list[str]]] = {}

    # sort the resources according to outgoing resptrs
    ok_resources: list[XMLResource] = []
    # resources with circular references
    nok_resources: list[XMLResource] = []
    # internal ids for the resources that do not have circular references
    ok_res_ids: list[str] = []
    cnt = 0
    nok_len = 9999999
    while len(resources) > 0 and cnt < 10000:
        for resource in resources:
            resptrs = resource.get_resptrs()
            # get all the resptrs which have an internal id, i.e. that do not exist in the triplestore
            resptrs = [x for x in resptrs if not regex.search(r"https?://rdfh.ch/[a-fA-F0-9]{4}/\w{22}", x)]
            # if there are no resptrs references, append to the ok resources
            if len(resptrs) == 0:
                ok_resources.append(resource)
                ok_res_ids.append(resource.id)
            else:
                ok = True
                # iterate over the list with all the resptrs that have internal links
                for resptr in resptrs:
                    # if that resptr is not in the ok list, set the flag to false
                    if resptr not in ok_res_ids:
                        ok = False
                # if all the resptr are in the ok list, then there are no circular references
                if ok:
                    ok_resources.append(resource)
                    ok_res_ids.append(resource.id)
                # if any of the resptr are not in the ok list append the resource to the not ok list
                else:
                    nok_resources.append(resource)
        resources = nok_resources
        if len(nok_resources) == nok_len:
            # there are circular references. go through all problematic resources, and stash the problematic references.
            (
                nok_resources,
                ok_res_ids,
                ok_resources,
                stashed_xml_texts,
                stashed_resptr_props,
            ) = _stash_circular_references(
                nok_resources=nok_resources,
                ok_res_ids=ok_res_ids,
                ok_resources=ok_resources,
                stashed_xml_texts=stashed_xml_texts,
                stashed_resptr_props=stashed_resptr_props,
            )
        nok_len = len(nok_resources)
        nok_resources = []
        cnt += 1
        if verbose:
            print(f"{cnt}. ordering pass finished.")
            logger.info(f"{cnt}. ordering pass finished.")
    return ok_resources, stashed_xml_texts, stashed_resptr_props
