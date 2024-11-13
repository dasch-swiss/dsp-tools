import pytest
from rdflib import SH
from rdflib import Graph

from dsp_tools.commands.validate_data.sparql.file_value_shacl import construct_file_value_cardinality
from test.unittests.commands.validate_data.constants import API_SHAPES
from test.unittests.commands.validate_data.constants import ONTO


def test_construct_file_value_cardinality(onto_graph: Graph) -> None:
    res = construct_file_value_cardinality(onto_graph)
    number_of_classes_implemented = 1
    assert len(list(res.subjects(SH.property))) == number_of_classes_implemented
    moving_image = next(res.subjects(SH.property, API_SHAPES.hasMovingImageFileValue_PropShape))
    assert moving_image == ONTO.TestMovingImageRepresentation


if __name__ == "__main__":
    pytest.main([__file__])
