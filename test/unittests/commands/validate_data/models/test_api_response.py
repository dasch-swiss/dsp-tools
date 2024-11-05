import pytest

from dsp_tools.commands.validate_data.models.api_responses import OneList


@pytest.fixture
def one_list() -> OneList:
    return OneList(list_iri="http://rdfh.ch/lists/9999/list1", list_name="firstList", nodes=["n1", "n1.1", "n1.1.1"])


class TestOneList:
    def test_hlist(self, one_list: OneList) -> None:
        result = one_list.hlist()
        expected = '"hlist=<http://rdfh.ch/lists/9999/list1>"'
        assert result == expected
