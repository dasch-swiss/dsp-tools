from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class TripleGraph:
    """
    Contains all classes that express links between resources.
    """

    resptr_links: Optional[list[ResptrLink]]
    xml_links: Optional[list[XMLLink]]


@dataclass
class ResptrLink:
    """
    This class represents a link between two resources.
    """

    subject_id: str
    object_id: str
    edge_weight: float | int = 1

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
    edge_weight: float | int
    reified_object_id: UUID
    reified_ede_weight: float | int

    def __init__(
        self,
        subject_id: str,
        object_ids: set[str],
        edge_weight: int | float = 1,
        reified_ede_weight: int | float = 999999999,
    ):
        self.subject_id = subject_id
        self.object_ids = object_ids
        self.reified_object_id = uuid.uuid1()
        self.edge_weight = edge_weight
        self.reified_ede_weight = reified_ede_weight

    def to_reified_networkX_format(self):
        main_node = (self.subject_id, self.reified_object_id), self.edge_weight
        reified_node = [(self.reified_object_id, x) for x in self.object_link_ids]
        return main_node, reified_node, self.reified_ede_weight
