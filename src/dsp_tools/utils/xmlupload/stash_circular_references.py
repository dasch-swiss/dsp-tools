from __future__ import annotations

from typing import cast
from uuid import uuid4

from dsp_tools.models.exceptions import BaseError
from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlresource import XMLResource
from dsp_tools.utils.create_logger import get_logger
from dsp_tools.utils.xmlupload.stash.stash_models import (
    LinkValueStash,
    LinkValueStashItem,
    StandoffStash,
    StandoffStashItem,
    Stash,
)

logger = get_logger(__name__)


def _stash_circular_references(
    nok_resources: list[XMLResource],
    ok_res_ids: set[str],
) -> tuple[list[XMLResource], set[str], list[XMLResource], Stash | None]:
    """
    Raises:
        BaseError
    """
    stashed_standoff_values: list[StandoffStashItem] = []
    stashed_link_values: list[LinkValueStashItem] = []
    ok_resources: list[XMLResource] = []

    for res in nok_resources.copy():
        for link_prop in res.get_props_with_links():
            if link_prop.valtype == "text":
                for value in link_prop.values:
                    if value.resrefs and not all(_id in ok_res_ids for _id in value.resrefs):
                        # replace the problematic XML with a UUID
                        # and remove the problematic resrefs from the XMLValue's resrefs list
                        standoff_xml = cast(KnoraStandoffXml, value.value)
                        uuid = str(uuid4())
                        standoff_stash_item = StandoffStashItem(
                            res_id=res.id,
                            res_type=res.restype,
                            uuid=uuid,
                            prop_name=link_prop.name,
                            value=standoff_xml,
                        )
                        stashed_standoff_values.append(standoff_stash_item)
                        value.value = KnoraStandoffXml(uuid)
                        value.resrefs = [_id for _id in value.resrefs if _id in ok_res_ids]
            elif link_prop.valtype == "resptr":
                for value in link_prop.values.copy():
                    if value.value not in ok_res_ids:
                        # value.value is the id of the target resource. stash it, then delete it
                        link_stash_item = LinkValueStashItem(
                            res_id=res.id,
                            res_type=res.restype,
                            prop_name=link_prop.name,
                            target_id=str(value.value),
                        )
                        stashed_link_values.append(link_stash_item)
                        link_prop.values.remove(value)
            else:
                logger.error("ERROR in remove_circular_references(): link_prop.valtype is neither text nor resptr.")
                raise BaseError("ERROR in remove_circular_references(): link_prop.valtype is neither text nor resptr.")

            if len(link_prop.values) == 0:
                # if all values of a link property have been stashed, the property needs to be removed
                res.properties.remove(link_prop)

        ok_resources.append(res)
        ok_res_ids.add(res.id)
        nok_resources.remove(res)

    standoff_stash = StandoffStash.make(stashed_standoff_values)
    link_value_stash = LinkValueStash.make(stashed_link_values)
    stash = Stash.make(standoff_stash, link_value_stash)

    return nok_resources, ok_res_ids, ok_resources, stash


def remove_circular_references(
    resources: list[XMLResource],
    verbose: bool,
) -> tuple[list[XMLResource], Stash | None]:
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
        stash: an object that contains the problematic references
    """

    if verbose:
        print("Checking resources for unresolvable references...")
        logger.info("Checking resources for unresolvable references...")

    stash: Stash | None = None
    # sort the resources according to outgoing resptrs
    ok_resources: list[XMLResource] = []
    # resources with circular references
    nok_resources: list[XMLResource] = []
    # internal ids for the resources that do not have circular references
    ok_res_ids: set[str] = set()
    cnt = 0
    nok_len = 9999999
    while len(resources) > 0 and cnt < 10000:
        for resource in resources:
            resptrs = resource.get_internal_resptrs()
            # if there are no resptrs references
            # or all of them are in the ok resources,
            # append the resource to the ok resources
            if len(resptrs) == 0 or resptrs.issubset(ok_res_ids):
                ok_resources.append(resource)
                ok_res_ids.add(resource.id)
            else:
                nok_resources.append(resource)
        resources = nok_resources
        if len(nok_resources) == nok_len:
            # there are circular references. go through all problematic resources, and stash the problematic references.
            nok_resources, ok_res_ids, ok_res, stash = _stash_circular_references(nok_resources, ok_res_ids)
            ok_resources.extend(ok_res)
        nok_len = len(nok_resources)
        nok_resources = []
        cnt += 1
        if verbose:
            print(f"{cnt}. ordering pass finished.")
        logger.debug(f"{cnt}. ordering pass finished.")

    return ok_resources, stash
