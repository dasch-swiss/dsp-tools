from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass
class GeometryPoint:
    x: float
    y: float


@dataclass
class Geometry:
    line_width: float
    points: list[GeometryPoint] = field(default_factory=list)
    status: str = "active"
    type_: str = "rectangle"

    @staticmethod
    def create_new(
        line_width: float, points: list[GeometryPoint] | None, status: str = "active", type_: str = "rectangle"
    ) -> Geometry: ...
