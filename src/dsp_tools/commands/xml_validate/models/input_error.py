from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class InputError(Protocol):
    def get_msg(self) -> str:
        raise NotImplementedError


@dataclass
class ResourceErrorCollection:
    res_id: str
    errors: list[InputError]

    def get_msg(self) -> str:
        raise NotImplementedError


#######################
# Cardinality Violation


@dataclass
class MaxCardinalityViolation:
    res_id: str
    prop_name: str
    number_used: str

    def get_msg(self) -> str:
        raise NotImplementedError


#######################
# Ontology Violations


@dataclass
class PropNotFoundInOntology:
    res_id: str
    prop_name: str

    def get_msg(self) -> str:
        raise NotImplementedError


@dataclass
class ResClassNotFoundInOntology:
    res_id: str
    cls_name: str

    def get_msg(self) -> str:
        raise NotImplementedError


@dataclass
class PropTypeMismatch:
    res_id: str
    prop_name: str
    prop_type_used: str
    prop_type_expected: str

    def get_msg(self) -> str:
        raise NotImplementedError


@dataclass
class LinkTargetMismatch:
    res_id: str
    prop_name: str
    target_class_used: str
    target_class_expected: str

    def get_msg(self) -> str:
        raise NotImplementedError


#######################
# List Violation


@dataclass
class ListNodeNotFound:
    res_id: str
    prop_name: str
    list_name: str
    node_name: str

    def get_msg(self) -> str:
        raise NotImplementedError


#######################
# Miscellaneous Errors


@dataclass
class DuplicateContent:
    res_id: str
    prop_name: str
    content: str
    number_of_occurrence: int

    def get_msg(self) -> str:
        raise NotImplementedError
