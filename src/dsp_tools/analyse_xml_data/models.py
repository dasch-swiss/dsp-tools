from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ResptrLink:
    """
    This class represents a direct link (resptr) between a starting resource and a target resource.

    Args:
        subject_id: resource ID that is in subject position of the triple
        object_id: resource ID that is in object position of the triple
        link_uuid: each link, which is represented in the graph gets a UUID
    """

    subject_id: str
    object_id: str
    link_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def cost_links(self) -> float:
        """The cost of this outgoing is consistently 1"""
        return 1


@dataclass(frozen=True)
class XMLLink:
    """
    This class represents one or more links from a single starting resource to a set of target resources,
    where all target resources are linked to from a single text value on the starting resource.

    Args:
        subject_id: resource ID that is in subject position of the triple
        object_link_ids: a set that contains the resource IDs which were embedded in the <text> element
        link_uuid: each link, which is represented in the graph gets a UUID
    """

    subject_id: str
    object_link_ids: set[str]
    link_uuid: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def cost_links(self) -> float:
        """The cost of this outgoing link (1 / number of links in the XML text)"""
        return 1 / len(self.object_link_ids)
