from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


@dataclass
class CollectedProblems:
    header: str
    problems: list[InputProblem]


@dataclass
class InputProblem:
    problematic_object: str
    problem: ProblemType


class ProblemType(StrEnum):
    PREFIX_COULD_NOT_BE_RESOLVED = (
        "The prefix used is not defined in the 'prefix' section of the file, "
        "nor does it belong to one of the project ontologies."
    )

