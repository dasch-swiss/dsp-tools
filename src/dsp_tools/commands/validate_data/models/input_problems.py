from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import StrEnum
from enum import auto

import pandas as pd
import regex

from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent
from dsp_tools.commands.validate_data.models.validation import ValidationReportGraphs


@dataclass
class ValidateDataResult:
    no_problems: bool
    problems: None | UnknownClassesInData | OntologyValidationProblem | SortedProblems
    report_graphs: None | ValidationReportGraphs


@dataclass
class OntologyValidationProblem:
    problems: list[OntologyResourceProblem]


@dataclass
class OntologyResourceProblem:
    res_iri: str
    msg: str


@dataclass
class UnknownClassesInData:
    unknown_classes: set[str]
    defined_classes: set[str]


@dataclass
class DuplicateFileWarning:
    problems: list[InputProblem]


@dataclass
class AllProblems:
    problems: list[InputProblem]
    unexpected_results: list[UnexpectedComponent]


@dataclass
class SortedProblems:
    unique_violations: list[InputProblem]
    user_warnings: list[InputProblem]
    user_info: list[InputProblem]
    unexpected_shacl_validation_components: list[str]


@dataclass
class MessageComponents:
    message_header: str
    message_body: str | None
    message_df: pd.DataFrame | None


@dataclass
class UserPrintMessages:
    violations: MessageComponents | None
    warnings: MessageComponents | None
    infos: MessageComponents | None
    unexpected_violations: MessageComponents | None


@dataclass
class InputProblem:
    problem_type: ProblemType
    res_id: str | None
    res_type: str | None
    prop_name: str
    severity: Severity
    message: str | None = None
    input_value: str | None = None
    input_type: str | None = None
    expected: str | None = None

    def __post_init__(self) -> None:
        self.message = self._clean_input(self.message)
        self.expected = self._clean_input(self.expected)

    def _clean_input(self, to_clean: str | None) -> str | None:
        if not to_clean:
            return None
        if not regex.search(r"\S+", to_clean):
            return None
        str_split = [content for x in to_clean.split(" ") if (content := x.strip())]
        return " ".join(str_split)


class Severity(Enum):
    VIOLATION = auto()
    WARNING = auto()
    INFO = auto()


class ProblemType(StrEnum):
    GENERIC = "generic"
    FILE_VALUE_MISSING = "file problem"
    FILE_DUPLICATE = "Duplicate Filepath / IIIF-URI"
    FILE_VALUE_PROHIBITED = "A file was added to the resource. This resource type must not have a file."
    MAX_CARD = "Maximum Cardinality Violation"
    MIN_CARD = "Minimum Cardinality Violation"
    NON_EXISTING_CARD = "The resource class does not have a cardinality for this property."
    VALUE_TYPE_MISMATCH = "Value Type Mismatch"
    INPUT_REGEX = "Wrong Format of Input"
    LINK_TARGET_TYPE_MISMATCH = "Linked Resource Type Mismatch"
    INEXISTENT_LINKED_RESOURCE = "Linked Resource does not exist"
    DUPLICATE_VALUE = "Your input is duplicated"
