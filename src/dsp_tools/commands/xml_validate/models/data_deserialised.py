from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any
from typing import Protocol


@dataclass
class DataDeserialised:
    shortcode: str
    default_onto: str
    resources: list[ResourceDeserialised]

    def get_resources_by_type(self) -> dict[str, list[ResourceDeserialised]]:
        res_d = defaultdict(list)
        for r in self.resources:
            res_d[r.res_class].append(r)
        return res_d


@dataclass
class ResourceDeserialised:
    res_id: str
    res_class: str
    label: str
    values: list[ValueDeserialised]

    def get_cardinalities(self) -> list[PropForResourceCardinality]:
        card_d = defaultdict(list)
        for v in self.values:
            card_d[v.prop_name].append(1)
        return [PropForResourceCardinality(res_id=self.res_id, prop_name=k, num_used=len(v)) for k, v in card_d.items()]


@dataclass
class ValueDeserialised(Protocol):
    prop_name: str
    prop_value: Any
    res_id: str


@dataclass
class SimpleTextValueDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: str
    res_id: str


@dataclass
class ListValueDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: str
    list_name: str
    res_id: str


@dataclass
class LinkValueDeserialised(ValueDeserialised):
    prop_name: str
    prop_value: str
    res_id: str


@dataclass
class PropForResourceCardinality:
    res_id: str
    prop_name: str
    num_used: int
