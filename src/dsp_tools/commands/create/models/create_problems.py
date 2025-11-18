from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


@dataclass
class CollectedProblems:
    header: str
    problems: list[CreateProblem]


@dataclass
class UserInformation:
    focus_object: str
    msg: UserInformationMessage


class UserInformationMessage(StrEnum):
    LIST_EXISTS_ON_SERVER = "The list already exists on the server, therefore it is skipped entirely."


@dataclass
class CreateProblem:
    problematic_object: str
    problem: ProblemType


@dataclass
class InputProblem(CreateProblem):
    problem: InputProblemType


@dataclass
class UploadProblem(CreateProblem):
    problem: UploadProblemType


class ProblemType(StrEnum): ...


class InputProblemType(ProblemType):
    USER_PASSWORD_NOT_SET = (
        "This user cannot be created as no password is specified and no default password is saved in a .env file."
    )
    DUPLICATE_LIST_NAME = "You have lists in your project with the same name, this is not permitted."
    PREFIX_COULD_NOT_BE_RESOLVED = (
        "The prefix used is not defined in the 'prefix' section of the file, "
        "nor does it belong to one of the project ontologies."
    )


class UploadProblemType(ProblemType):
    # Groups
    GROUP_COULD_NOT_BE_CREATED = "The group could not be created."
    # Users
    USER_COULD_NOT_BE_CREATED = "The user could not be created."
    USER_COULD_NOT_BE_ADDED_TO_GROUP = "The user could not be added to some or all of the custom groups."
    USER_GROUPS_NOT_FOUND = "The user could not be added to the groups because they do not exist on the server."
    PROJECT_MEMBERSHIP_COULD_NOT_BE_ADDED = "The user could not be added as project member."
    PROJECT_ADMIN_COULD_NOT_BE_ADDED = "The user could not be added as project admin."
    # Lists
    LIST_COULD_NOT_BE_CREATED = "The list could not be created on the server."
    LIST_NODE_COULD_NOT_BE_CREATED = "The list node could not be created on the server."
    # Ontology
    CARDINALITY_COULD_NOT_BE_ADDED = "The cardinality could not be added."
    CARDINALITY_PROPERTY_NOT_FOUND = "The referenced property does not exist on the server."
