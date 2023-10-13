from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID


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
    rx_edge_index: Optional[int] = None
    edge_weight: float = 1


@dataclass
class XMLLink:
    """
    This class represents a link between a resource and an XMl text
    which contains links to other resources.
    """

    subject_id: str
    object_link_ids: set[str]
    rx_edge_index: Optional[int] = None
    edge_weight: float = 1
    reified_object_id: UUID = field(init=False, default_factory=uuid.uuid4)

    @property
    def cost_links(self):
        return 1 / len(self.object_link_ids)
