from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import StrEnum
from enum import auto

import regex

from dsp_tools.commands.validate_data.models.validation import UnexpectedComponent


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
class MessageStrings:
    message_header: str
    message_body: str


@dataclass
class UserPrintMessages:
    violations: MessageStrings | None
    warnings: MessageStrings | None
    infos: MessageStrings | None
    unexpected_violations: MessageStrings | None


@dataclass
class InputProblem:
    problem_type: ProblemType
    res_id: str
    res_type: str
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
    FILE_VALUE = "file problem"
    FILE_DUPLICATE = "file used several times"
    MAX_CARD = "Maximum Cardinality Violation"
    MIN_CARD = "Minimum Cardinality Violation"
    NON_EXISTING_CARD = "The resource class does not have a cardinality for this property."
    FILE_VALUE_PROHIBITED = "A file was added to the resource. This resource type must not have a file."
    VALUE_TYPE_MISMATCH = "Value Type Mismatch"
    INPUT_REGEX = "Wrong Format of Input"
    LINK_TARGET_TYPE_MISMATCH = "Linked Resource Type Mismatch"
    INEXISTENT_LINKED_RESOURCE = "Linked Resource does not exist"
    DUPLICATE_VALUE = "Your input is duplicated"
