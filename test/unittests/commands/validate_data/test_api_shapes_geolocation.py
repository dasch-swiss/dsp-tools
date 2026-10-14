"""The geolocation shapes in api-shapes.ttl mirror the CRS table in geolocation_constants.py."""

import importlib.resources
from decimal import Decimal

import pytest
from rdflib import SH
from rdflib import Graph
from rdflib import Literal
from rdflib.collection import Collection
from rdflib.term import Node

from dsp_tools.utils.geolocation_constants import ALL_CRS
from dsp_tools.utils.geolocation_constants import Crs
from dsp_tools.utils.rdf_constants import API_SHAPES


@pytest.fixture(scope="module")
def api_shapes() -> Graph:
    g = Graph()
    g.parse(str(importlib.resources.files("dsp_tools").joinpath("resources/validate_data/api-shapes.ttl")))
    return g


def _reachable_nodes(g: Graph, start: Node) -> set[Node]:
    found: set[Node] = set()
    to_visit = [start]
    while to_visit:
        node = to_visit.pop()
        if node in found:
            continue
        found.add(node)
        to_visit.extend(g.objects(node, None))
    return found


def _get_bounds(g: Graph, crs_shape: Node, ordinate_name: str) -> tuple[Decimal, Decimal]:
    prop = API_SHAPES[f"geolocationHas{ordinate_name.capitalize()}"]
    bounded_shapes = [
        x for x in _reachable_nodes(g, crs_shape) if (x, SH.path, prop) in g and (x, SH.minInclusive, None) in g
    ]
    assert len(bounded_shapes) == 1
    shape = bounded_shapes[0]
    min_value = next(g.objects(shape, SH.minInclusive))
    max_value = next(g.objects(shape, SH.maxInclusive))
    assert isinstance(min_value, Literal)
    assert isinstance(max_value, Literal)
    return Decimal(str(min_value)), Decimal(str(max_value))


@pytest.mark.parametrize("crs", ALL_CRS, ids=lambda x: x.code)
def test_bounds_match_crs_table(api_shapes: Graph, crs: Crs) -> None:
    crs_shape = API_SHAPES[f"GeolocationValue_{crs.code}_Shape"]
    assert _get_bounds(api_shapes, crs_shape, crs.x_name) == (crs.x_min, crs.x_max)
    assert _get_bounds(api_shapes, crs_shape, crs.y_name) == (crs.y_min, crs.y_max)


def test_crs_codes_match_crs_table(api_shapes: Graph) -> None:
    crs_shape = API_SHAPES.GeolocationValue_Crs_Shape
    in_lists = [
        x for x in _reachable_nodes(api_shapes, crs_shape) if (x, SH.path, API_SHAPES.geolocationHasCrs) in api_shapes
    ]
    assert len(in_lists) == 1
    codes_node = next(api_shapes.objects(in_lists[0], SH["in"]))
    codes = [str(x) for x in Collection(api_shapes, codes_node)]
    assert codes == [x.code for x in ALL_CRS]
