import pytest
from rdflib import Graph


@pytest.fixture
def every_combination_once_report() -> Graph:
    g = Graph()
    g.parse("testdata/validate-data/validation_reports/every_combination_once_report.ttl")
    return g
