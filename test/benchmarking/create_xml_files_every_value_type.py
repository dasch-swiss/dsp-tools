
from collections.abc import Callable
from typing import Any

from dsp_tools.xmllib import Resource
from dsp_tools.xmllib.models.internal.values import Value

# This is to be used with the ontology: testdata/validate-data/generic/project.json


def create_one_resource(id_counter: int) -> Resource:
    return Resource.create_new(res_id=f"id_{id_counter}", restype=":ClassWithEverything", label=str(id_counter))


def create_values(prop: str, val: Any, func: Callable[Any, str], number_of_vals: int) -> list[Value]:
    return [create_one_value(prop, val, func) for _ in range(number_of_vals)]


def create_one_value(prop: str, val: Any, func: Callable[Any, str]) -> Value:
    return func(val, prop)
