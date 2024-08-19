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


@dataclass
class MinCardinalityViolation:
    res_id: str
    prop_name: str

    def get_msg(self) -> str:
        raise NotImplementedError


@dataclass
class MaxCardinalityViolation:
    res_id: str
    prop_name: str
    number_used: str

    def get_msg(self) -> str:
        raise NotImplementedError


@dataclass
class ListNameNotFound:
    res_id: str
    prop_name: str
    list_used: str

    def get_msg(self) -> str:
        raise NotImplementedError


@dataclass
class ListNodeNotFound:
    res_id: str
    prop_name: str
    list_name: str
    node_name: str

    def get_msg(self) -> str:
        raise NotImplementedError
