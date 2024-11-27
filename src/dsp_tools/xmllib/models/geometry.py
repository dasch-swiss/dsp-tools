from __future__ import annotations

import json
import warnings
from dataclasses import dataclass
from dataclasses import field

from dsp_tools.models.custom_warnings import DspToolsUserWarning
from dsp_tools.xmllib import is_color
from dsp_tools.xmllib import is_decimal


@dataclass
class GeometryShape:
    resource_id: str
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
            warnings.warn(
                DspToolsUserWarning(
                    f"Some of the shape values of the resource with the ID '{self.resource_id}' are not valid: "
                    f"\n- {'\n- '.join(problems)}"
                )
            )
        self.line_width = line_width
        self.color = color
        self.status = status
        self.type_ = type_
        return self

    def to_json_string(self) -> str:
        points = [x.to_dict() for x in self.points]
        json_dict = {
            "status": f'"{self.status}"',
            "type": f'"{self.type_}"',
            "lineWidth": self.line_width,
            "points": points,
        }
        return json.dumps(json_dict)


@dataclass
class GeometryPoint:
    x: float
    y: float
    resource_id: str

    def __post_init__(self) -> None:
        if not all([is_decimal(self.x), is_decimal(self.y)]):
            msg = (
                f"The entered geometry points for the resource with the ID '{self.resource_id}' are not floats. "
                f"x: '{self.x}', y: '{self.y}'"
            )
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
                    f"The following points of the resource with the ID '{self.resource_id}' "
                    f"are not valid: {', '.join(info)}"
                )
                warnings.warn(DspToolsUserWarning(msg))

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y}
