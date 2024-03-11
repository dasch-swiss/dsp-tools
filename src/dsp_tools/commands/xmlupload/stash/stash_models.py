from __future__ import annotations

from dataclasses import dataclass
from itertools import groupby

from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue


@dataclass(frozen=True)
class StandoffStashItem:
    """Holds information about a single stashed XML text value."""

    res_id: str
    res_type: str
    uuid: str
    prop_name: str
    value: FormattedTextValue


@dataclass(frozen=True)
class StandoffStash:
    """Holds information about a number of stashed XML text values, organized by resource instance."""

    res_2_stash_items: dict[str, list[StandoffStashItem]]

    @staticmethod
    def make(items: list[StandoffStashItem]) -> StandoffStash | None:
        """
        Factory method for StandoffStash.

        Args:
            items: A list of StandoffStashItem.

        Returns:
            StandoffStash | None: A StandoffStash object or None, if an empty list was passed.
        """

        def _get_res_id(x: StandoffStashItem) -> str:
            return x.res_id

        if not items:
            return None
        items = sorted(items, key=_get_res_id)
        grouped_objects = {k: list(vals) for k, vals in groupby(items, key=_get_res_id)}
        return StandoffStash(grouped_objects)


@dataclass(frozen=True)
class LinkValueStashItem:
    """Holds information about a single stashed link value."""

    res_id: str
    res_type: str
    prop_name: str
    target_id: str
    permission: str | None = None


@dataclass(frozen=True)
class LinkValueStash:
    """Holds information about a number of stashed link values (resptr-props), organized by resource instance."""

    res_2_stash_items: dict[str, list[LinkValueStashItem]]

    @staticmethod
    def make(items: list[LinkValueStashItem]) -> LinkValueStash | None:
        """
        Factory method for LinkValueStash.

        Args:
            items: A list of LinkValueStashItem.

        Returns:
            LinkValueStash | None: A LinkValueStash object or None, if an empty list was passed.
        """

        def _get_res_id(x: LinkValueStashItem) -> str:
            return x.res_id

        if not items:
            return None
        items = sorted(items, key=_get_res_id)
        grouped_objects = {k: list(vals) for k, vals in groupby(items, key=_get_res_id)}
        return LinkValueStash(grouped_objects)


@dataclass(frozen=True)
class Stash:
    """Holds a standoff stash and a linkvalue stash"""

    standoff_stash: StandoffStash | None
    link_value_stash: LinkValueStash | None

    @staticmethod
    def make(standoff_stash: StandoffStash | None, link_value_stash: LinkValueStash | None) -> Stash | None:
        """
        Factory method for Stash.

        Args:
            standoff_stash: A StandoffStash object or None.
            link_value_stash: A LinkValueStash object or None.

        Returns:
            Stash: A Stash object, or None if both inputs are None.
        """
        if standoff_stash or link_value_stash:
            return Stash(standoff_stash, link_value_stash)
        return None
