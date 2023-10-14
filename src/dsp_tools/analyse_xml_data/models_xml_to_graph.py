from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TripleGraph:
    """
    Contains all classes that express links between resources.
    """

    resptr_links: list[ResptrLink]
    xml_links: list[XMLLink]


@dataclass
class ResptrLink:
    """
    This class represents a link between two resources.
    """

    subject_id: str
    object_id: str


@dataclass
class XMLLink:
    """
    This class represents a link between a resource and an XMl text
    which contains links to other resources.
    """

    subject_id: str
    object_link_ids: set[str]

    @property
    def cost_links(self) -> float:
        """The cost of this outgoing link (1 / number of links in the XML text)"""
        return 1 / len(self.object_link_ids)
