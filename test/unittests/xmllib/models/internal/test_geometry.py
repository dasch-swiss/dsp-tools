import warnings

import pytest

from dsp_tools.xmllib.models.internal.geometry import Circle
from dsp_tools.xmllib.models.internal.geometry import GeometryPoint
from dsp_tools.xmllib.models.internal.geometry import Polygon
from dsp_tools.xmllib.models.internal.geometry import Rectangle
from dsp_tools.xmllib.models.internal.geometry import Vector


class TestGeometryShape:
    def test_rectangle_to_json_string_success(self) -> None:
        geom_obj = Rectangle(
            point1=GeometryPoint(0.1, 0.2, "res_id"),
            point2=GeometryPoint(0.2, 0.3, "res_id"),
            line_width=2,
            color="#5b24bf",
            active=True,
            resource_id="res_id",
        )
        expected_str = (
            '{"status": "active", "type": "rectangle", "lineWidth": 2, '
            '"points": [{"x": 0.1, "y": 0.2}, {"x": 0.2, "y": 0.3}]}'
        )
        result = geom_obj.to_json_string()
        assert result == expected_str

    def test_polygon_to_json_string_no_points(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            polygon = Polygon(
                points=[],
                line_width=2,
                color="#5b24bf",
                active=True,
                resource_id="res_id",
            )
            assert len(caught_warnings) == 1
        result = polygon.to_json_string()
        expected_str = '{"status": "active", "type": "polygon", "lineWidth": 2, "points": []}'
        assert result == expected_str

    def test_circle_to_json_string_success(self) -> None:
        geom_obj = Circle(
            center=GeometryPoint(0.1, 0.2, "res_id"),
            radius=Vector(0.2, 0.2, "res_id"),
            line_width=2,
            color="#5b24bf",
            active=True,
            resource_id="res_id",
        )
        expected_str = (
            '{"status": "active", "type": "circle", "lineWidth": 2, '
            '"points": [{"x": 0.1, "y": 0.2}], "radius": {"x": 0.2, "y": 0.2}}'
        )
        result = geom_obj.to_json_string()
        assert result == expected_str


class TestGeometryPoint:
    def test_success(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            point = GeometryPoint(0.1, 0.2, "res_id")
            assert len(caught_warnings) == 0
        assert point.x == 0.1
        assert point.y == 0.2

    def test_success_as_string(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            point = GeometryPoint("0.1", "0.2", "res_id")  # type: ignore[arg-type]
            assert len(caught_warnings) == 0
        assert point.x == 0.1
        assert point.y == 0.2

    def test_warning(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            point = GeometryPoint("x", "y", "res_id")  # type: ignore[arg-type]
            assert len(caught_warnings) == 1
        assert point.x == "x"  # type: ignore[comparison-overlap]
        assert point.y == "y"  # type: ignore[comparison-overlap]


if __name__ == "__main__":
    pytest.main([__file__])
