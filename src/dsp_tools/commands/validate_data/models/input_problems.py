from __future__ import annotations

import warnings
from abc import ABC
from abc import abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
from rdflib import Graph

from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.models.custom_warnings import DspToolsUserWarning

LIST_SEPARATOR = "\n    - "
GRAND_SEPARATOR = "\n\n----------------------------\n"


@dataclass
class UnknownClassesInData:
    unknown_classes: set[str]
    classes_onto: set[str]

    def get_msg(self) -> str:
        if unknown := self._get_unknown_ontos_msg():
            return unknown
        return self._get_unknown_classes_msg()

    def _get_unknown_ontos_msg(self) -> str:
        def split_prefix(relative_iri: str) -> str:
            return relative_iri.split(":")[0]

        used_ontos = set(split_prefix(x) for x in self.unknown_classes)
        exising_ontos = set(split_prefix(x) for x in self.classes_onto)
        msg = ""
        if unknown := used_ontos - exising_ontos:
            msg = (
                f"Your data uses ontologies that don't exist in the database.\n"
                f"The following ontologies that are used in the data are unknown: {', '.join(exising_ontos)}"
                f"The following ontologies are uploaded: {', '.join(unknown)}\n"
            )
        return msg

    def _get_unknown_classes_msg(self) -> str:
        unknown_classes = sorted(list(self.unknown_classes))
        known_classes = sorted(list(self.classes_onto))
        return (
            f"Your data uses resource classes that do not exist in the ontologies in the database.\n"
            f"The following classes that are used in the data are unknown: {', '.join(unknown_classes)}\n"
            f"The following classes exist in the uploaded ontologies: {', '.join(known_classes)}\n"
        )


@dataclass
class UnexpectedResults:
    components: list[UnexpectedComponent]

    def save_inform_user(self, results_graph: Graph, shacl: Graph, data: Graph) -> None:
        cwdr = Path.cwd()
        prefix = f"{datetime.now()!s}_"
        unique_components = list(set(x.component_type for x in self.components))
        components = sorted(unique_components)
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

    def get_msg(self, file_path: Path) -> str:
        coll = self._make_collection()
        title_msg = f"\nDuring the validation of the data {len(self.problems)} errors were found:\n\n"
        if len(self.problems) > 50:
            out_path = file_path.parent / f"{file_path.stem}_validation_errors.csv"
            self._save_as_csv(out_path)
            out_message = (
                title_msg + f"Due to the large number or errors, the validation errors were saved at:\n{out_path}"
            )
        else:
            msg = [x.get_msg() for x in coll]
            out_message = title_msg + GRAND_SEPARATOR.join(msg)
        return out_message

    def _make_collection(self) -> list[ResourceProblemCollection]:
        d = defaultdict(list)
        for e in self.problems:
            d[e.res_id].append(e)
        collection_list = []
        for k, v in d.items():
            collection_list.append(ResourceProblemCollection(k, v))
        return sorted(collection_list, key=lambda x: x.res_id)

    def _save_as_csv(self, out_path: Path) -> None:
        all_problems = [x.to_dict() for x in self.problems]
        df = pd.DataFrame.from_records(all_problems)
        df = df.sort_values(by=["Resource Type", "Resource ID", "Property"])
        df.to_csv(out_path, index=False)


@dataclass
class ResourceProblemCollection:
    res_id: str
    problems: list[InputProblem]

    def get_msg(self) -> str:
        prop_msg = self._msg_for_properties()
        return f"Resource ID: {self.res_id} | Resource Type: {self.problems[0].res_type}\n{prop_msg}"

    def _msg_for_properties(self) -> str:
        grouped = self._make_collection()
        out_list = []
        for prop_name, problem in grouped.items():
            problem_list = [x.get_msg() for x in problem]
            out_list.append((prop_name, f"{prop_name}{LIST_SEPARATOR}{LIST_SEPARATOR.join(problem_list)}"))
        sorted_list = sorted(out_list, key=lambda x: x[0])
        return "\n".join([x[1] for x in sorted_list])

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

    @property
    @abstractmethod
    def problem(self) -> str: ...

    @abstractmethod
    def get_msg(self) -> str: ...

    @abstractmethod
    def to_dict(self) -> dict[str, str]: ...

    def _base_dict(self) -> dict[str, str]:
        return {
            "Resource Type": self.res_type,
            "Resource ID": self.res_id,
            "Property": self.prop_name,
            "Problem": self.problem,
        }

    @abstractmethod
    def sort_value(self) -> str: ...


#######################
# Generic Problem


@dataclass
class GenericProblem(InputProblem):
    results_message: str
    actual_content: str

    @property
    def problem(self) -> str:
        return self.results_message

    def get_msg(self) -> str:
        return f"{self.problem} | Content: '{self.actual_content}'"

    def to_dict(self) -> dict[str, str]:
        problm_dict = self._base_dict()
        problm_dict["Actual"] = self.actual_content
        return problm_dict

    def sort_value(self) -> str:
        return self.prop_name


#######################
# Cardinality Violation


@dataclass
class MaxCardinalityProblem(InputProblem):
    expected_cardinality: str

    @property
    def problem(self) -> str:
        return "Maximum Cardinality Violation"

    def get_msg(self) -> str:
        return f"{self.problem} | Expected Cardinality: {self.expected_cardinality}"

    def to_dict(self) -> dict[str, str]:
        problm_dict = self._base_dict()
        problm_dict["Expected"] = f"Cardinality: {self.expected_cardinality}"
        return problm_dict

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class MinCardinalityProblem(InputProblem):
    expected_cardinality: str

    @property
    def problem(self) -> str:
        return "Minimum Cardinality Violation"

    def get_msg(self) -> str:
        return f"{self.problem} | Expected Cardinality: {self.expected_cardinality}"

    def to_dict(self) -> dict[str, str]:
        problm_dict = self._base_dict()
        problm_dict["Expected"] = f"Cardinality: {self.expected_cardinality}"
        return problm_dict

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class NonExistentCardinalityProblem(InputProblem):
    @property
    def problem(self) -> str:
        return "The resource class does not have a cardinality for this property."

    def get_msg(self) -> str:
        return self.problem

    def to_dict(self) -> dict[str, str]:
        return self._base_dict()

    def sort_value(self) -> str:
        return self.prop_name


#######################
# Value Type Violation


@dataclass
class ValueTypeProblem(InputProblem):
    actual_type: str
    expected_type: str

    @property
    def problem(self) -> str:
        return "Value Type Mismatch"

    def get_msg(self) -> str:
        return f"{self.problem}, Actual Type: {self.actual_type} | Expected Type: {self.expected_type}"

    def to_dict(self) -> dict[str, str]:
        problm_dict = self._base_dict()
        problm_dict["Expected"] = self.expected_type
        problm_dict["Actual"] = self.actual_type
        return problm_dict

    def sort_value(self) -> str:
        return self.prop_name


#######################
# Content Violation


@dataclass
class ContentRegexProblem(InputProblem):
    expected_format: str
    actual_content: str | None

    @property
    def problem(self) -> str:
        return "Wrong Content Format"

    def get_msg(self) -> str:
        msg = f"{self.problem}, Expected Format: {self.expected_format}"
        if self.actual_content:
            msg += f" | Content: '{self._short_content()}'"
        return msg

    def to_dict(self) -> dict[str, str]:
        problm_dict = self._base_dict()
        problm_dict["Expected"] = self.expected_format
        if self.actual_content:
            problm_dict["Content"] = self._short_content()
        return problm_dict

    def _short_content(self) -> str:
        if not self.actual_content:
            return ""
        if len(self.actual_content) > 15:
            return f"{self.actual_content[:15]}[...]"
        return self.actual_content

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class LinkTargetTypeMismatchProblem(InputProblem):
    link_target_id: str
    actual_type: str
    expected_type: str

    @property
    def problem(self) -> str:
        return "Linked Resource Type Mismatch"

    def get_msg(self) -> str:
        return (
            f"{self.problem}, Target Resource ID: '{self.link_target_id}' "
            f"Actual Type: '{self.actual_type}' | Expected Resource Type: '{self.expected_type}'"
        )

    def to_dict(self) -> dict[str, str]:
        problm_dict = self._base_dict()
        problm_dict["Expected"] = self.expected_type
        problm_dict["Actual"] = self.actual_type
        problm_dict["Content"] = self.link_target_id
        return problm_dict

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class LinkedResourceDoesNotExistProblem(InputProblem):
    link_target_id: str

    @property
    def problem(self) -> str:
        return "Linked Resource does not Exist"

    def get_msg(self) -> str:
        return f"{self.problem}, Target Resource ID: '{self.link_target_id}'"

    def to_dict(self) -> dict[str, str]:
        problm_dict = self._base_dict()
        problm_dict["Actual"] = self.link_target_id
        return problm_dict

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class DuplicateValueProblem(InputProblem):
    actual_content: str

    @property
    def problem(self) -> str:
        return "Value is duplicated"

    def get_msg(self) -> str:
        return f"{self.problem}, Content: '{self.actual_content}'"

    def to_dict(self) -> dict[str, str]:
        problm_dict = self._base_dict()
        problm_dict["Content"] = self.actual_content
        return problm_dict

    def sort_value(self) -> str:
        return self.prop_name


@dataclass
class FileValueProblem(InputProblem):
    expected: str

    @property
    def problem(self) -> str:
        return self.expected

    def get_msg(self) -> str:
        return f"{self.problem}"

    def to_dict(self) -> dict[str, str]:
        problm_dict = self._base_dict()
        problm_dict["Expected"] = self.expected
        return problm_dict

    def sort_value(self) -> str:
        return self.prop_name
