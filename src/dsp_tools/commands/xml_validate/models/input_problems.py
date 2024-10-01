from __future__ import annotations

from abc import ABC
from collections import defaultdict
from dataclasses import dataclass

from rdflib import Graph
from rdflib.term import Node

INDENT = "\n    "
GRAND_SEPARATOR = "\n----------------------------\n"


@dataclass
class ValidationResult:
    source_constraint_component: Node
    res_iri: Node
    res_class: Node
    property: Node
    results_message: str
    value: str | None = None


@dataclass
class UnexpectedComponent:
    component_type: str


@dataclass
class UnexpectedResults:
    components: list[UnexpectedComponent]
    validation_result: Graph


@dataclass
class AllProblems:
    problems: list[InputProblem]
    unexpected_results: UnexpectedResults | None

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
class InputProblem(ABC):
    res_id: str
    res_type: str
    prop_name: str

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
        return "\n".join(msg)

    def sort_value(self) -> str:
        return self.res_id


#######################
# Cardinality Violation


@dataclass
class MaxCardinalityViolation(InputProblem):
    expected_cardinality: str

    def get_msg(self) -> str:
        return (
            f"Maximum Cardinality Violation:"
            f"{INDENT}Property: {self.prop_name} | Expected Cardinality: {self.expected_cardinality}"
        )

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class MinCardinalityViolation(InputProblem):
    expected_cardinality: str

    def get_msg(self) -> str:
        return (
            f"Minimum Cardinality Violation:"
            f"{INDENT}Property: {self.prop_name} | Expected Cardinality: {self.expected_cardinality}"
        )

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class NonExistentCardinalityViolation(InputProblem):
    def get_msg(self) -> str:
        return f"The resource class does not have a cardinality for this property:{INDENT}Property: {self.prop_name}"

    def sort_value(self) -> str:
        return self.prop_name
