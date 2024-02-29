from __future__ import annotations

import uuid
from dataclasses import dataclass
from dataclasses import field


@dataclass(frozen=True)
class ResptrLink:
    """
    This class represents a direct link (resptr) between a starting resource and a target resource.

    Attributes:
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

    Attributes:
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


@dataclass(frozen=True)
class Edge:
    """
    This class represents an edge in the rustworkx graph.

    Attributes:
        source: rustworkx index of the resource from which the link originates
        target: rustworkx index of the resource where the link points to
        link_object: the link that connects the source with the target
    """

    source: int
    target: int
    link_object: ResptrLink | XMLLink

    def as_tuple(self) -> tuple[int, int, ResptrLink | XMLLink]:
        """Returns a representation of this edge as a tuple of the source index, target index and link object"""
        return self.source, self.target, self.link_object


@dataclass(frozen=True)
class Cost:
    """
    Attributes:
        source: rustworkx index of the resource from which the link originates
        target: rustworkx index of the resource where the link points to
        node_value: cost-gain-ratio if this link is stashed
    """

    source: int
    target: int
    node_value: float
