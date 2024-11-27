from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.xmllib.value_checkers import is_decimal


@dataclass
class GeometryPoint:
    x: float
    y: float

    def __post_init__(self) -> None:
        if not all([is_decimal(self.x), is_decimal(self.y)]):
            msg = f"The entered geometry points are not floats. x: '{self.x}', y: '{self.y}'"
            warnings.warn(DspToolsUserWarning(msg))


@dataclass
class Geometry:
    line_width: float
    points: list[GeometryPoint]
    status: str
    type_: str

    @staticmethod
    def create_new(
        line_width: float,
        points: list[GeometryPoint] | None,
        status: str = "active",
        type_: str = "rectangle",
    ) -> Geometry:
        pnt = points if points else []
        return Geometry(line_width, pnt, status, type_)

    def add_point(self, x: float, y: float) -> Geometry:
        self.points.append(GeometryPoint(x, y))
        return self

    def add_point_optional(self, x: Any, y: Any) -> Geometry:
        if all([is_decimal(x), is_decimal(y)]):
            self.points.append(GeometryPoint(x, y))
        return self
