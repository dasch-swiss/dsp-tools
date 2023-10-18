from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class ResptrLink:
    """This class represents a link between two resources."""

    subject_id: str
    object_id: str
    link_uuid: UUID = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def cost_links(self) -> float:
        """The cost of this outgoing is consistently 1"""
        return 1


@dataclass(frozen=True)
class XMLLink:
    """
    This class represents a link between a resource and an XML text
    the text contains links to one or more other resources.
    """

    subject_id: str
    object_link_ids: set[str]
    link_uuid: UUID = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def cost_links(self) -> float:
        """The cost of this outgoing link (1 / number of links in the XML text)"""
        return 1 / len(self.object_link_ids)


@dataclass
class ResourceStashInfo:
    """
    Holds information about a resource that can be uploaded to the DSP.

    May hold information about the links that need to be stashed from this resource before it can be uploaded.
    An ordered list of UploadResources can be used to determine the order in which resources need to be uploaded.
    """

    res_id: str
    stash_links_to: list[XMLLink | ResptrLink] = field(default_factory=list)
