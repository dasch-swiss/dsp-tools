import pytest
from rdflib import RDF
from rdflib import SH
from rdflib import Graph
from rdflib import Namespace

from dsp_tools.commands.xml_validate.sparql.value_shacl import _construct_one_property_type_shape_based_on_object_type

ONTO = Namespace("http://0.0.0.0:3333/ontology/9999/onto/v2#")
API_SHAPES = Namespace("http://api.knora.org/ontology/knora-api/shapes/v2#")


def test_construct_one_property_type_shape_based_on_object_type(one_res_one_prop: Graph) -> None:
    res = _construct_one_property_type_shape_based_on_object_type(
        one_res_one_prop, "knora-api:BooleanValue", "api-shapes:BooleanValue_ClassShape"
    )
    assert len(res) == 3
    assert next(res.objects(ONTO.testBoolean_PropShape, SH.path)) == ONTO.testBoolean
    assert next(res.objects(ONTO.testBoolean_PropShape, RDF.type)) == SH.PropertyShape
    assert next(res.objects(ONTO.testBoolean_PropShape, SH.node)) == API_SHAPES.BooleanValue_ClassShape


if __name__ == "__main__":
    pytest.main([__file__])
