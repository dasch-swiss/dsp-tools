from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

from dsp_tools.error.xmllib_warnings import MessageInfo
from dsp_tools.error.xmllib_warnings_util import emit_xmllib_input_warning
from dsp_tools.xmllib.value_checkers import is_color
from dsp_tools.xmllib.value_checkers import is_decimal


@dataclass
class GeometryShape(Protocol):
    color: str

    def to_json_string(self) -> str: ...


@dataclass
class Rectangle(GeometryShape):
    point1: GeometryPoint
    point2: GeometryPoint
    line_width: float
    color: str
    active: bool
    resource_id: str

    def __post_init__(self) -> None:
        _check_warn_shape_info(self.color, self.line_width, self.resource_id)

    def to_json_string(self) -> str:
        json_dict = {
            "status": "active" if self.active else "deleted",
            "type": "rectangle",
            "lineWidth": self.line_width,
            "points": [self.point1.to_dict(), self.point2.to_dict()],
        }
        return json.dumps(json_dict)


@dataclass
class Polygon(GeometryShape):
    points: list[GeometryPoint]
    line_width: float
    color: str
    active: bool
    resource_id: str

    def __post_init__(self) -> None:
        _check_warn_shape_info(self.color, self.line_width, self.resource_id)
        if len(self.points) < 3:
            msg = (
                "The region shape is a polygon. Polygons should have at least 3 points. "
                "If you would like to display a rectangle we recommend to use the designated rectangle shape."
            )
            emit_xmllib_input_warning(MessageInfo(msg, self.resource_id))

    def to_json_string(self) -> str:
        json_dict = {
            "status": "active" if self.active else "deleted",
            "type": "polygon",
            "lineWidth": self.line_width,
            "points": [x.to_dict() for x in self.points],
        }
        return json.dumps(json_dict)


@dataclass
class Circle(GeometryShape):
    center: GeometryPoint
    radius: Vector
    line_width: float
    color: str
    active: bool
    resource_id: str

    def __post_init__(self) -> None:
        _check_warn_shape_info(self.color, self.line_width, self.resource_id)

    def to_json_string(self) -> str:
        json_dict = {
            "status": "active" if self.active else "deleted",
            "type": "circle",
            "lineWidth": self.line_width,
            "points": [self.center.to_dict()],
            "radius": self.radius.to_dict(),
        }
        return json.dumps(json_dict)


@dataclass
class GeometryPoint:
    x: float
    y: float
    resource_id: str

    def __post_init__(self) -> None:
        if not all([is_decimal(self.x), is_decimal(self.y)]):
            msg = f"The entered geometry points are not floats. x: '{self.x}', y: '{self.y}'"
            emit_xmllib_input_warning(MessageInfo(msg, self.resource_id))
        else:
            info = []
            if not 0 <= float(self.x) <= 1:
                info.append(f"x: '{self.x}'")
            if not 0 <= float(self.y) <= 1:
                info.append(f"y: '{self.y}'")
            if info:
                msg = (
                    f"The geometry points must be larger/equal 0 and smaller/equal 1. "
                    f"The following points are not valid: {', '.join(info)}"
                )
                emit_xmllib_input_warning(MessageInfo(msg, self.resource_id))
            self.x = float(self.x)
            self.y = float(self.y)

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y}


@dataclass
class Vector:
    x: float
    y: float
    resource_id: str

    def __post_init__(self) -> None:
        if not all([is_decimal(self.x), is_decimal(self.y)]):
            msg = f"The radius vector are not floats. x: '{self.x}', y: '{self.y}'"
            emit_xmllib_input_warning(MessageInfo(msg, self.resource_id))
        else:
            info = []
            if not 0 <= float(self.x) <= 1:
                info.append(f"x: '{self.x}'")
            if not 0 <= float(self.y) <= 1:
                info.append(f"y: '{self.y}'")
            if info:
                msg = (
                    f"The radius vector must be larger/equal 0 and smaller/equal 1. "
                    f"The following values are not valid: {', '.join(info)}"
                )
                emit_xmllib_input_warning(MessageInfo(msg, self.resource_id))
            self.x = float(self.x)
            self.y = float(self.y)

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y}


def _check_warn_shape_info(color: str, line_width: float, res_id: str) -> None:
    problems = []
    line_msg = f"The line width must be a number between 1-5. The provided value is not valid: {line_width}"
    if not is_decimal(line_width):
        problems.append(line_msg)
    elif not 0 < int(line_width) <= 5:
        problems.append(line_msg)
    if not is_color(color):
        problems.append(f"The color must be a valid hexadecimal color. The provided value is not valid: {color}")
    if problems:
        msg = f"Some of the shape values are not valid: \n- {'\n- '.join(problems)}"
        emit_xmllib_input_warning(MessageInfo(msg, res_id))
