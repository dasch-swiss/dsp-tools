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
    edge_weight: float = 1

    def to_networkX_format(self):
        return (self.subject_id, self.object_id), self.edge_weight


@dataclass
class XMLLink:
    """
    This class represents a link between a resource and an XMl text
    which contains links to other resources.
    """

    subject_id: str
    object_link_ids: set[str]
    edge_weight: float
    reified_object_id: UUID = field(init=False, default_factory=uuid.uuid4)
    reified_ede_weight: float = 999999999

    def to_reified_networkX_format(self):
        main_node = (self.subject_id, self.reified_object_id), self.edge_weight
        reified_node = [(self.reified_object_id, x) for x in self.object_link_ids]
        return main_node, reified_node, self.reified_ede_weight
