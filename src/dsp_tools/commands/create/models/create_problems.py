from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


@dataclass
class CollectedProblems:
    header: str
    problems: list[CreateProblem]


@dataclass
class CardinalitiesThatMayCreateAProblematicCircle:
    subject: str
    prop: str
    object_cls: str
    card: str


@dataclass
class UserInformation:
    focus_object: str
    msg: UserInformationMessage


class UserInformationMessage(StrEnum):
    LIST_EXISTS_ON_SERVER = "The list already exists on the server, therefore it is skipped entirely."


@dataclass
class CreateProblem:
    problematic_object: str
    problem: ProblemType | str


@dataclass
class InputProblem(CreateProblem):
    problem: InputProblemType | str


@dataclass
class UploadProblem(CreateProblem):
    problem: UploadProblemType | str


class ProblemType(StrEnum): ...


class InputProblemType(ProblemType):
    USER_PASSWORD_NOT_SET = (
        "This user cannot be created as no password is specified and no default password is saved in a .env file."
    )
    DEFAULT_PERMISSIONS_NOT_CORRECT = (
        "Defining 'default_permissions' is mandatory and must either be 'public' or 'private'."
    )
    LIMITED_VIEW_PERMISSIONS_NOT_CORRECT = (
        "Your input for the 'limited_view' permissions is invalid. It must be either 'all' or a list of image classes."
    )
    UNKNOWN_IRI_IN_PERMISSIONS_OVERRULE = (
        "The referenced class or property in the private overrule permissions is not defined in the ontology."
    )
    INVALID_LIMITED_VIEW_PERMISSIONS_OVERRULE = (
        "This class cannot be used in limited_view permissions "
        "because it is not a subclass of StillImageRepresentation."
    )

    DUPLICATE_LIST_NAME = "You have lists in your project with the same name. List names must be unique."
    DUPLICATE_LIST_NODE_NAME = "You have list nodes in your project with the same name. List node names must be unique."
    PREFIX_COULD_NOT_BE_RESOLVED = (
        "The prefix used is not defined in the 'prefix' section of the file, "
        "nor does it belong to one of the project ontologies."
    )
    UNDEFINED_SUPER_PROPERTY = "This property is derived from an invalid super-property."
    UNDEFINED_SUPER_CLASS = "This resource is derived from an invalid super-class."
    UNDEFINED_PROPERTY_IN_CARDINALITY = "This cardinality references a property that does not exist."
    DUPLICATE_CLASS_NAME = "This class name appears multiple times in the same ontology."
    DUPLICATE_PROPERTY_NAME = "This property name appears multiple times in the same ontology."
    MIN_CARDINALITY_ONE_WITH_CIRCLE = ""
    CIRCULAR_CLASS_INHERITANCE = "This class is part of a circular inheritance chain, which is not allowed."
    CIRCULAR_PROPERTY_INHERITANCE = "This property is part of a circular inheritance chain, which is not allowed."


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
    PROPERTY_COULD_NOT_BE_CREATED = "The property could not be created."
    PROPERTY_LIST_NOT_FOUND = "The property cannot be created, because the list it references does not exist."
    PROPERTY_SUPER_FAILED = "The property cannot be created, because its super-property was not created."
    PROPERTY_REFERENCES_FAILED_CLASS = "The property cannot be created, because a class it references was not created."
    CLASS_COULD_NOT_BE_CREATED = "The class could not be created."
    CLASS_SUPER_FAILED = "The class cannot be created, because its super-class was not created."
    ONTOLOGY_COULD_NOT_BE_CREATED = "The ontology cannot be created."
