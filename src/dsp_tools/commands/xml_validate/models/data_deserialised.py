from __future__ import annotations

from collections import Counter
from collections import defaultdict
from dataclasses import dataclass
from typing import Any
from typing import Protocol


@dataclass
class DataDeserialised:
    shortcode: str
    default_onto: str
    resources: list[ResourceData]

    def get_resources_by_type(self) -> dict[str, list[ResourceData]]:
        res_d = defaultdict(list)
        for r in self.resources:
            res_d[r.res_class].append(r)
        return res_d

    def get_resource_and_types(self) -> dict[str, str]:
        return {x.res_id: x.res_class for x in self.resources}


@dataclass
class ResourceData:
    res_id: str
    res_class: str
    label: str
    values: list[ValueData]

    def get_cardinalities(self) -> list[PropForResourceCardinality]:
        card_d = defaultdict(list)
        for v in self.values:
            card_d[v.prop_name].append(1)
        return [PropForResourceCardinality(prop_name=k, num_used=len(v)) for k, v in card_d.items()]

    def get_duplicate_content(self) -> list[tuple[str, Any]]:
        prop_vals = Counter(x.get_prop_value() for x in self.values)
        return [t for t, count in prop_vals.items() if count > 1]


@dataclass
class ValueData(Protocol):
    prop_name: str
    prop_value: Any
    res_id: str

    def type(self) -> str:
        raise NotImplementedError

    def get_prop_value(self) -> tuple[str, Any]:
        return self.prop_name, self.prop_value


@dataclass
class SimpleTextData(ValueData):
    prop_name: str
    prop_value: str
    res_id: str

    def type(self) -> str:
        return "SimpleText"


@dataclass
class IntValueData(ValueData):
    prop_name: str
    prop_value: str
    res_id: str

    def type(self) -> str:
        return "IntValue"


@dataclass
class ListValueData(ValueData):
    prop_name: str
    prop_value: str
    list_name: str
    res_id: str

    def type(self) -> str:
        return "ListValue"


@dataclass
class LinkValueData(ValueData):
    prop_name: str
    prop_value: str
    res_id: str

    def type(self) -> str:
        return "LinkValue"


@dataclass
class PropForResourceCardinality:
    prop_name: str
    num_used: int
