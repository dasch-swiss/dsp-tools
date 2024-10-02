from pathlib import Path

import pytest
from rdflib import Graph

from dsp_tools.commands.xml_validate.models.input_problems import MaxCardinalityViolation
from dsp_tools.commands.xml_validate.models.input_problems import MinCardinalityViolation
from dsp_tools.commands.xml_validate.models.input_problems import NonExistentCardinalityViolation
from dsp_tools.commands.xml_validate.reformat_validaton_result import reformat_validation_graph
from dsp_tools.commands.xml_validate.xml_validate import _get_data_info_from_file

LOCAL_API = "http://0.0.0.0:3333"


@pytest.fixture
def data_cardinality_violation() -> Graph:
    data = _get_data_info_from_file(Path("testdata/xml-validate/data/cardinality_violation.xml"), LOCAL_API)
    return data.make_graph()


@pytest.fixture
def result_cardinality_violation() -> Graph:
    g = Graph()
    g.parse("testdata/xml-validate/validation_results/cardinality_violation_result.ttl")
    return g


def test_reformat_validation_graph(result_cardinality_violation: Graph, data_cardinality_violation: Graph) -> None:
    result = reformat_validation_graph(result_cardinality_violation, data_cardinality_violation)
    assert not result.unexpected_results
    assert len(result.problems) == 4
    sorted_problems = sorted(result.problems, key=lambda x: x.sort_value())
    val_one = sorted_problems[0]
    assert isinstance(val_one, MinCardinalityViolation)
    assert val_one.res_id == "id_card_one"
    val_one = sorted_problems[1]
    assert isinstance(val_one, MaxCardinalityViolation)
    assert val_one.res_id == "id_max_card"
    val_one = sorted_problems[2]
    assert isinstance(val_one, MinCardinalityViolation)
    assert val_one.res_id == "id_min_card"
    val_one = sorted_problems[3]
    assert isinstance(val_one, NonExistentCardinalityViolation)
    assert val_one.res_id == "id_closed_constraint"


if __name__ == "__main__":
    pytest.main([__file__])