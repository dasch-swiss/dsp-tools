from __future__ import annotations

import warnings
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.xmllib import is_color
from dsp_tools.xmllib import is_decimal


@dataclass
class GeometryShape:
    points: list[GeometryPoint] = field(default_factory=list)
    line_width: float = 2
    color: str = "#5b24bf"
    status: str = "active"
    type_: str = "rectangle"

    def customise_shape(self, line_width: float, color: str, status: str, type_: str) -> GeometryShape:
        """Change the default values of the geometry shape."""
        problems = []
        line_msg = f"The line width must be a number between 1-5. The provided value is not valid: {line_width}"
        if not is_decimal(line_width):
            problems.append(line_msg)
        elif not 0 < int(line_width) <= 5:
            problems.append(line_msg)
        if not is_color(color):
            problems.append(f"The color must be a valid hexadecimal color. The provided value is not valid: {color}")
        if status not in ["active", "deleted"]:
            problems.append(
                f'The status must be either "active" or "deleted". The provided value is not valid: {status}'
            )
        if type_ not in ["circle", "rectangle", "polygon"]:
            problems.append(
                f'The type must be either ""circle", "rectangle" or "polygon" . '
                f"The provided value is not valid: {type_}"
            )
        if problems:
            warnings.warn(DspToolsUserWarning(f"Some of the shape values are not valid: \n- {'\n- '.join(problems)}"))
        self.line_width = line_width
        self.color = color
        self.status = status
        self.type_ = type_
        return self

    def add_shape_point(self, x: float, y: float) -> GeometryShape:
        self.points.append(GeometryPoint(x, y))
        return self

    def add_shape_point_optional(self, x: Any, y: Any) -> GeometryShape:
        if all([is_decimal(x), is_decimal(y)]):
            self.points.append(GeometryPoint(x, y))
        return self

    def add_shape_point_multiple(self, points: list[tuple[float, float]]) -> GeometryShape: ...


@dataclass
class GeometryPoint:
    x: float
    y: float

    def __post_init__(self) -> None:
        if not all([is_decimal(self.x), is_decimal(self.y)]):
            msg = f"The entered geometry points are not floats. x: '{self.x}', y: '{self.y}'"
            warnings.warn(DspToolsUserWarning(msg))
        else:
            info = []
            if not 0 <= float(self.x) <= 1:
                info.append(f"x: '{self.x}'")
            if not 0 <= float(self.y) <= 1:
                info.append(f"y: '{self.y}'")
            if info:
                msg = (
                    f"The geometry points must be larger/equal 0 and smaller/equal 1. "
                    f"The following points do not conform: {', '.join(info)}"
                )
                warnings.warn(DspToolsUserWarning(msg))
