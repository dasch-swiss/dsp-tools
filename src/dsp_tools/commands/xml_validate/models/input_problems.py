from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Protocol

INDENT = "    "
MEDIUM_SEPARATOR = "\n\n"
GRAND_SEPARATOR = "\n\n----------------------------\n\n"


@dataclass
class AllProblems:
    problems: list[InputProblems]

    def get_msg(self) -> str:
        coll = self._make_collection()
        msg = [x.get_msg() for x in coll]
        title_msg = f"During the validation of the data {len(self.problems)} were found:\n\n"
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
class InputProblems(Protocol):
    res_id: str

    def get_msg(self) -> str:
        raise NotImplementedError

    def sort_value(self) -> str:
        raise NotImplementedError


@dataclass
class ResourceProblemCollection:
    res_id: str
    problems: list[InputProblems]

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


#######################
# ObjectClassConstraint / ObjectDatatypeConstraint Violations


@dataclass
class PropTypeMismatch:
    res_id: str
    prop_name: str
    prop_type_used: str
    prop_type_expected: str

    def get_msg(self) -> str:
        return (
            f"The following property does not have the same type in the ontology and the data:\n"
            f"{INDENT}Property: {self.prop_name}\n"
            f"{INDENT}Type used in data: {self.prop_type_used}\n"
            f"{INDENT}Type expected according to the ontology: {self.prop_type_expected}"
        )

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class LinkTargetMismatch:
    res_id: str
    prop_name: str
    target_id: str
    target_class_used: str
    target_class_expected: str

    def get_msg(self) -> str:
        return (
            f"The following link property specifies a different resource type in object position:\n"
            f"{INDENT}Property: {self.prop_name}\n"
            f"{INDENT}Target resource ID: {self.target_id}\n"
            f"{INDENT}Target class of resource: {self.target_class_used}\n"
            f"{INDENT}Target class expected according to the ontology: {self.target_class_expected}"
        )

    def sort_value(self) -> str:
        return self.prop_name


#######################
# List Violation


@dataclass
class ListNodeNotFound:
    res_id: str
    prop_name: str
    list_name: str
    node_name: str

    def get_msg(self) -> str:
        return (
            f"The following list node was not found on the server:\n"
            f"{INDENT}Property: {self.prop_name}\n"
            f"{INDENT}List node used: {self.node_name}\n"
            f"{INDENT}List name in data: {self.list_name}"
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
        return self.prop_name
