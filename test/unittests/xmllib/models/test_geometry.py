import warnings

from dsp_tools.xmllib.models.geometry import GeometryPoint
from dsp_tools.xmllib.models.geometry import GeometryShape


class TestGeometryShape:
    def test_customise_shape_good(self) -> None:
        geom_obj = GeometryShape("res_id")
        with warnings.catch_warnings(record=True) as caught_warnings:
            changed = geom_obj.customise_shape(line_width=1, color="#5b24ba", status="deleted", type_="polygon")
            assert len(caught_warnings) == 0
        assert changed.line_width == 1
        assert changed.color == "#5b24ba"
        assert changed.status == "deleted"
        assert changed.type_ == "polygon"

    def test_customise_shape_warns(self) -> None:
        geom_obj = GeometryShape("res_id")
        with warnings.catch_warnings(record=True) as caught_warnings:
            changed = geom_obj.customise_shape(line_width=2, color="not a color", status="active", type_="rectangle")
            assert len(caught_warnings) == 1
        assert changed.color == "not a color"

    def test_to_json_string_success(self) -> None:
        geom_obj = GeometryShape("res_id")
        geom_obj.points = [GeometryPoint(0.1, 0.2, "res_id"), GeometryPoint(0.2, 0.3, "res_id")]
        expected_str = (
            '{"status": "active", "type": "rectangle", "lineWidth": 2, '
            '"points": [{"x": 0.1, "y": 0.2}, {"x": 0.2, "y": 0.3}]}'
        )
        result = geom_obj.to_json_string()
        assert result == expected_str

    def test_to_json_string_no_points(self) -> None:
        with warnings.catch_warnings(record=True) as caught_warnings:
            result = GeometryShape("res_id").to_json_string()
            assert len(caught_warnings) == 1
        expected_str = '{"status": "active", "type": "rectangle", "lineWidth": 2, "points": []}'
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
        assert point.x == "x"
        assert point.y == "y"
