from __future__ import annotations

import warnings
from abc import ABC
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from rdflib import Graph

from dsp_tools.commands.xml_validate.models.validation import UnexpectedComponent
from dsp_tools.models.custom_warnings import DspToolsUserWarning

LIST_SEPARATOR = "\n    - "
INDENT = "\n    "
GRAND_SEPARATOR = "\n\n----------------------------\n"


@dataclass
class UnexpectedResults:
    components: list[UnexpectedComponent]

    def save_inform_user(self, results_graph: Graph, shacl: Graph, data: Graph) -> None:
        cwdr = Path.cwd()
        prefix = f"{datetime.now()!s}"
        components = sorted(x.component_type for x in self.components)
        msg = (
            f"Unexpected violations were found in the validation results:"
            f"{LIST_SEPARATOR}{LIST_SEPARATOR.join(components)}\n"
            f"Please contact the development team with the files starting with the timestamp '{prefix}' "
            f"in the directory '{cwdr}'."
        )
        save_path = cwdr / f"{prefix}validation_result.ttl"
        results_graph.serialize(save_path)
        shacl_p = cwdr / f"{prefix}shacl.ttl"
        shacl.serialize(shacl_p)
        data_p = cwdr / f"{prefix}data.ttl"
        data.serialize(data_p)
        warnings.warn(DspToolsUserWarning(msg))


@dataclass
class AllProblems:
    problems: list[InputProblem]
    unexpected_results: UnexpectedResults | None

    def get_msg(self) -> str:
        coll = self._make_collection()
        msg = [x.get_msg() for x in coll]
        title_msg = f"\nDuring the validation of the data {len(self.problems)} errors were found:\n\n"
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
        msg = [f"Resource ID: {self.res_id} | Resource Type: {self.problems[0].res_type}"]
        sorted_problems = sorted(self.problems, key=lambda x: x.sort_value())
        msg.extend([x.get_msg() for x in sorted_problems])
        return "\n".join(msg)

    def _msg_for_properties(self) -> str:
        grouped = self._make_collection()
        out_list = []
        for prop_name, problem in grouped.items():
            problem_list = [x.get_msg() for x in problem]
            out_list.append(f"{prop_name}{LIST_SEPARATOR}{LIST_SEPARATOR.join(problem_list)}")
        return "\n".join(out_list)

    def _make_collection(self) -> dict[str, list[InputProblem]]:
        grouped_dict = defaultdict(list)
        for problem in self.problems:
            grouped_dict[problem.sort_value()].append(problem)
        return grouped_dict

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
        return f"Maximum Cardinality Violation | Expected Cardinality: {self.expected_cardinality}"

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class MinCardinalityViolation(InputProblem):
    expected_cardinality: str

    def get_msg(self) -> str:
        return f"Minimum Cardinality Violation | Expected Cardinality: {self.expected_cardinality}"

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class NonExistentCardinalityViolation(InputProblem):
    def get_msg(self) -> str:
        return "The resource class does not have a cardinality for this property."

    def sort_value(self) -> str:
        return self.prop_name
