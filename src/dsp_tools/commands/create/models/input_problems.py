from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


@dataclass
class CollectedProblems:
    header: str
    problems: list[CreateProblem]


@dataclass
class CreateProblem:
    problematic_object: str
    problem: ProblemType


@dataclass
class InputProblem(CreateProblem): ...


@dataclass
class UploadProblem(CreateProblem): ...


class ProblemType(StrEnum):
    PREFIX_COULD_NOT_BE_RESOLVED = (
        "The prefix used is not defined in the 'prefix' section of the file, "
        "nor does it belong to one of the project ontologies."
    )
    CARDINALITY_COULD_NOT_BE_ADDED = "The cardinality could not be added."
    DUPLICATE_LIST_NAME = "You have lists in your project with the same name, his is not permitted."
