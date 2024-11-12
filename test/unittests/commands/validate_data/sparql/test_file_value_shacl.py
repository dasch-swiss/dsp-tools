import pytest
from rdflib import SH
from rdflib import Graph

from dsp_tools.commands.validate_data.sparql.file_value_shacl import _construct_generic_file_value_cardinality
from dsp_tools.commands.validate_data.sparql.file_value_shacl import construct_file_value_cardinality


def test_construct_file_value_cardinality(onto_graph: Graph) -> None:
    res = construct_file_value_cardinality(onto_graph)
    number_of_classes_with_files = 6
    class_shapes = list(res.subjects(predicate=SH.property))
    assert len(class_shapes) == number_of_classes_with_files


def test_construct_generic_file_value_cardinality(onto_graph: Graph) -> None:
    res = _construct_generic_file_value_cardinality(onto_graph)
    number_of_classes_without_specific_sparql = 6
    class_shapes = list(res.subjects(predicate=SH.property))
    assert len(class_shapes) == number_of_classes_without_specific_sparql


if __name__ == "__main__":
    pytest.main([__file__])
