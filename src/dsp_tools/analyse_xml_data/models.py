from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ResptrLink:
    """This class represents a link between two resources."""

    subject_id: str
    object_id: str


@dataclass
class XMLLink:
    """
    This class represents a link between a resource and an XML text
    the text contains links to one or more other resources.
    """

    subject_id: str
    object_link_ids: set[str]

    @property
    def cost_links(self) -> float:
        """The cost of this outgoing link (1 / number of links in the XML text)"""
        return 1 / len(self.object_link_ids)


@dataclass
class UploadResource:
    """
    Holds information about a resource that can be uploaded to the DSP.

    May hold information about the links that need to be stashed from this resource before it can be uploaded.
    A ordered list of UploadResources can be used to determine the order in which resources need to be uploaded.
    """

    res_id: str
    stash_links_to: list[str] = field(default_factory=list)
