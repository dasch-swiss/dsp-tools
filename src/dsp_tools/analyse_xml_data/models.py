from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ResptrLink:
    """
    This class represents a direct link (resptr) between a starting resource and a target resource.

    Args:
        source_id: ID of the resource from which the link originates
        target_id: ID of the resource where the link points to
        link_uuid: identifier of this link
    """

    source_id: str
    target_id: str
    link_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def cost_links(self) -> float:
        """The cost of this outgoing is consistently 1"""
        return 1


@dataclass(frozen=True)
class XMLLink:
    """
    This class represents one or more links from a single starting resource to a set of target resources,
    where all target resources are linked to from a single text value of the starting resource.

    Args:
        source_id: ID of the resource from which the link(s) originate
        target_ids: IDs of the resources that are referenced in the text value
        link_uuid: identifier of this link
    """

    source_id: str
    target_ids: set[str]
    link_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def cost_links(self) -> float:
        """The cost of this outgoing link (1 / number of links in the XML text)"""
        return 1 / len(self.target_ids)
