from __future__ import annotations

from dataclasses import dataclass

from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.models.xmlproperty import XMLProperty
from dsp_tools.models.xmlresource import XMLResource


@dataclass(frozen=True)
class StandoffStashItem:
    """
    A dataclass for a stashed standoff xml.
    """

    uuid: str
    link_prop: XMLProperty
    value: KnoraStandoffXml
    # Permissions missing still


@dataclass(frozen=True)
class StandoffStash:
    """..."""

    res_2_stash_items: dict[str, list[StandoffStashItem]]
    res_2_xmlres: dict[str, XMLResource]

    @staticmethod
    def make(tups: list[tuple[XMLResource, StandoffStashItem]]) -> StandoffStash | None:
        """
        Factory method for StandoffStash.

        Args:
            tups: A list of tuples of XMLResource and StandoffStashItem.

        Returns:
            StandoffStash | None: A StandoffStash object or None, if an empty list was passed.
        """
        if not tups:
            return None
        res_2_stash_items = {}
        res_2_xmlres = {}
        for xmlres, stash_item in tups:
            if xmlres.id not in res_2_stash_items:
                res_2_stash_items[xmlres.id] = [stash_item]
                res_2_xmlres[xmlres.id] = xmlres
            else:
                res_2_stash_items[xmlres.id].append(stash_item)
        return StandoffStash(res_2_stash_items, res_2_xmlres)
