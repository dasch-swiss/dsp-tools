import pytest
from rdflib import RDF
from rdflib import SH
from rdflib import Graph

from dsp_tools.commands.validate_data.sparql.value_shacl import _add_property_shapes_to_class_shapes
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_link_value_shape
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_one_property_type_shape_based_on_object_type
from dsp_tools.commands.validate_data.sparql.value_shacl import _construct_one_property_type_text_value
from test.unittests.commands.validate_data.constants import API_SHAPES
from test.unittests.commands.validate_data.constants import ONTO


def test_construct_one_property_type_shape_based_on_object_type(one_res_one_prop: Graph) -> None:
    res = _construct_one_property_type_shape_based_on_object_type(
        one_res_one_prop, "knora-api:BooleanValue", "api-shapes:BooleanValue_ClassShape"
    )
    assert len(res) == 3
    assert next(res.objects(ONTO.testBoolean_PropShape, SH.path)) == ONTO.testBoolean
    assert next(res.objects(ONTO.testBoolean_PropShape, RDF.type)) == SH.PropertyShape
    assert next(res.objects(ONTO.testBoolean_PropShape, SH.node)) == API_SHAPES.BooleanValue_ClassShape


def test_construct_link_value_shape(link_prop: Graph) -> None:
    res = _construct_link_value_shape(link_prop)
    assert len(res) == 3
    assert next(res.objects(ONTO.testHasLinkTo_PropShape, SH.path)) == ONTO.testHasLinkTo
    assert next(res.objects(ONTO.testHasLinkTo_PropShape, RDF.type)) == SH.PropertyShape
    assert next(res.objects(ONTO.testHasLinkTo_PropShape, SH.node)) == API_SHAPES.LinkValue_ClassShape


def test_construct_one_property_type_text_value(one_richtext_prop: Graph) -> None:
    res = _construct_one_property_type_text_value(
        one_richtext_prop, "salsah-gui:Richtext", "api-shapes:FormattedTextValue_ClassShape"
    )
    assert len(res) == 3
    assert next(res.objects(ONTO.testRichtext_PropShape, SH.path)) == ONTO.testRichtext
    assert next(res.objects(ONTO.testRichtext_PropShape, RDF.type)) == SH.PropertyShape
    assert next(res.objects(ONTO.testRichtext_PropShape, SH.node)) == API_SHAPES.FormattedTextValue_ClassShape


def test_add_property_shapes_to_class_shapes(card_1: Graph) -> None:
    res = _add_property_shapes_to_class_shapes(card_1)
    assert len(res) == 1
    assert next(res.objects(ONTO.ClassMixedCard, SH.property)) == ONTO.testBoolean_PropShape


if __name__ == "__main__":
    pytest.main([__file__])
