from pathlib import Path

import pytest
from rdflib import Graph

from dsp_tools.commands.xml_validate.reformat_validaton_result import _reformat_result_graph
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


def test_reformat_result_graph(result_cardinality_violation: Graph, data_cardinality_violation: Graph) -> None:
    result = _reformat_result_graph(result_cardinality_violation, data_cardinality_violation)
    assert len(result) == 4


if __name__ == "__main__":
    pytest.main([__file__])
