import pytest
from rdflib import SH
from rdflib import Graph

from dsp_tools.commands.validate_data.sparql.file_value_shacl import construct_file_value_cardinality
from test.unittests.commands.validate_data.constants import API_SHAPES
from test.unittests.commands.validate_data.constants import ONTO


@pytest.fixture
def file_value_shacl(onto_graph: Graph) -> Graph:
    return construct_file_value_cardinality(onto_graph)


def test_construct_file_value_cardinality(file_value_shacl: Graph) -> None:
    number_of_classes_implemented = 1
    assert len(list(file_value_shacl.subjects(SH.property))) == number_of_classes_implemented


def test_construct_moving_image(file_value_shacl: Graph) -> None:
    result_list = list(file_value_shacl.subjects(SH.property, API_SHAPES.hasMovingImageFileValue_PropShape))
    assert len(result_list) == 1
    moving_image = result_list[0]
    assert moving_image == ONTO.TestMovingImageRepresentation


if __name__ == "__main__":
    pytest.main([__file__])
