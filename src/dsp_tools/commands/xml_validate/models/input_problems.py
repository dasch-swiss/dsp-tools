from __future__ import annotations

import warnings
from abc import ABC
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from rdflib import Graph
from rdflib.term import Node

from dsp_tools.commands.xml_validate.xml_validate import LIST_SEPARATOR
from dsp_tools.models.custom_warnings import DspToolsUserWarning

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

    def save_inform_user(self, cwdr: Path) -> None:
        save_path = cwdr / f"validation_result_{datetime.now()!s}.ttl"
        components = sorted(x.component_type for x in self.components)
        msg = (
            f"Unexpected violations were found in the validation results:"
            f"{LIST_SEPARATOR}{LIST_SEPARATOR.join(components)}\n"
            f"The validation report was saved here: {save_path}\n"
            f"Please contact the dsp-tools development team with this information."
        )
        self.validation_result.serialize(save_path)
        warnings.warn(DspToolsUserWarning(msg))


@dataclass
class AllProblems:
    problems: list[InputProblem]
    unexpected_results: UnexpectedResults | None

    def communicate_with_the_user(self, cwdr: Path) -> str:
        if self.unexpected_results:
            self.unexpected_results.save_inform_user(cwdr)
        return self.get_msg()

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
class ResourceProblemCollection:
    res_id: str
    problems: list[InputProblem]

    def get_msg(self) -> str:
        msg = [
            f"Resource ID: {self.res_id} | Resource Type: {self.problems[0].res_type} "
            f"has {len(self.problems)} problem(s)."
        ]
        sorted_problems = sorted(self.problems, key=lambda x: x.sort_value())
        msg.extend([x.get_msg() for x in sorted_problems])
        return "\n".join(msg)

    def sort_value(self) -> str:
        return self.res_id


@dataclass
class InputProblem(ABC):
    res_id: str
    res_type: str
    prop_name: str

    def get_msg(self) -> str:
        raise NotImplementedError

    def sort_value(self) -> str:
        raise NotImplementedError


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
        return f"The resource class does not have a cardinality for the property {self.prop_name}"

    def sort_value(self) -> str:
        return self.prop_name
