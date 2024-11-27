from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.xmllib import is_decimal


@dataclass
class RegionShape:
    line_width: float
    color: str
    points: list[GeometryPoint]
    status: str
    type_: str

    # TODO: add shape / add shape point
    # TODO: make this shape automatically

    @staticmethod
    def customise_shape(
        points: list[tuple[float, float]] | None = None,
        line_width: float = 2,
        color: str = "#5b24bf",
        status: str = "active",
        type_: str = "rectangle",
    ) -> RegionShape:
        # TODO: inform about that the points must be a decimal representing a percentage of the image
        # TODO: the default value was chosen,
        #  because most color blind people are able to distinguish it, it is a blue, leaning to purple
        pnt = points if points else []
        return RegionShape(line_width, color, pnt, status, type_)

    def add_shape_point(self, x: float, y: float) -> RegionShape:
        self.points.append(GeometryPoint(x, y))
        return self

    def add_shape_point_optional(self, x: Any, y: Any) -> RegionShape:
        if all([is_decimal(x), is_decimal(y)]):
            self.points.append(GeometryPoint(x, y))
        return self

    def add_shape_point_multiple(self, points: list[tuple[float, float]]) -> RegionShape: ...


@dataclass
class GeometryPoint:
    x: float
    y: float

    def __post_init__(self) -> None:
        if not all([is_decimal(self.x), is_decimal(self.y)]):
            msg = f"The entered geometry points are not floats. x: '{self.x}', y: '{self.y}'"
            warnings.warn(DspToolsUserWarning(msg))
        else:
            _warn_if_point_not_in_range(float(self.x), float(self.y))


def _warn_if_point_not_in_range(x: float, y: float) -> None:
    info = []
    if not 0 <= x <= 1:
        info.append(f"x: '{x}'")
    if not 0 <= y <= 1:
        info.append(f"y: '{y}'")
    if info:
        msg = (
            f"The geometry points must be larger/equal 0 and smaller/equal 1. "
            f"The following points do not conform: {', '.join(info)}"
        )
        warnings.warn(DspToolsUserWarning(msg))
