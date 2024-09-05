from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any
from typing import Protocol

from rdflib import Graph

INDENT = "    "
MEDIUM_SEPARATOR = "\n\n"
GRAND_SEPARATOR = "\n\n----------------------------\n\n"


@dataclass
class AllProblems:
    problems: list[InputProblem]

    def get_msg(self) -> str:
        coll = self._make_collection()
        msg = [x.get_msg() for x in coll]
        title_msg = f"During the validation of the data {len(self.problems)} errors were found:\n\n"
        return title_msg + GRAND_SEPARATOR.join(msg)

    def _make_collection(self) -> list[ResourceProblemCollection]:
        d = defaultdict(list)
        for e in self.problems:
            d[e.res_id].append(e)
        collection_list = []
        for k, v in d.items():
            collection_list.append(ResourceProblemCollection(k, v))
        return sorted(collection_list, key=lambda x: x.res_id)


@dataclass
class InputProblem(Protocol):
    res_id: str

    def get_msg(self) -> str:
        raise NotImplementedError

    def sort_value(self) -> str:
        raise NotImplementedError


@dataclass
class ResourceProblemCollection:
    res_id: str
    problems: list[InputProblem]

    def get_msg(self) -> str:
        msg = [f"The resource with the ID '{self.res_id}' has the following problem(s):"]
        sorted_problems = sorted(self.problems, key=lambda x: x.sort_value())
        msg.extend([x.get_msg() for x in sorted_problems])
        return MEDIUM_SEPARATOR.join(msg)

    def sort_value(self) -> str:
        return self.res_id


#######################
# Cardinality Violation


@dataclass
class MaxCardinalityViolation:
    res_id: str
    prop_name: str

    def get_msg(self) -> str:
        return (
            f"The following property should not be used more than once for one resource:\n"
            f"{INDENT}Property: {self.prop_name}"
        )

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class ListViolation:
    res_id: str
    prop_name: str
    msg: str
    list_name: str
    node_name: str

    def get_msg(self) -> str:
        return (
            f"{self.msg}\n"
            f"{INDENT}Property: {self.prop_name}\n"
            f"{INDENT}List node used: {self.node_name}\n"
            f"{INDENT}List name in data: {self.list_name}"
        )

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class GenericContentViolation:
    res_id: str
    prop_name: str
    content: str
    value_type: str
    msg: str

    def get_msg(self) -> str:
        return (
            f"{self.msg}\n"
            f"{INDENT}Property: {self.prop_name}\n"
            f"{INDENT}Value Type: {self.value_type}\n"
            f"{INDENT}Content: {self.content}"
        )

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class DuplicateContent:
    res_id: str
    prop_name: str
    content: str

    def get_msg(self) -> str:
        return (
            f"The following property and values are entered more than once in the data, but they are identical.\n"
            f"Please remove all but one.\n"
            f"{INDENT}Property: {self.prop_name}\n"
            f"{INDENT}Content: {self.content}"
        )

    def sort_value(self) -> str:
        return self.res_id


@dataclass
class ValidationGraphs:
    cardinality_violations: Graph | None
    node_violations: Graph | None


@dataclass
class NodeInfo:
    res_id: str
    prop_name: str
    message: str


@dataclass
class ValueInfo:
    rdf_type: str
    hasValue: str
    hasListName: list[Any]
