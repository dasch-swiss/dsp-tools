import pytest

from dsp_tools.xmllib.helpers import ListLookup
from dsp_tools.xmllib.helpers import get_list_lookup


@pytest.fixture
def list_lookup() -> ListLookup:
    return get_list_lookup("testdata/json-project/test-list-lookup.json", "en", "default")


class TestGetListLookup:
    def test_lookup(self, list_lookup):
        assert list_lookup._label_language == "en"
        assert set(list_lookup._lookup.keys()) == {"list1", "list2"}
        expected_1 = {
            "Label 1": "list1_node1",
            "Label 2": "list1_node2",
            "Label 2.1": "list1_node2.1",
            "Label 2.2": "list1_node2.2",
        }
        assert list_lookup._lookup["list1"] == expected_1
        expected_2 = {"Label 1": "list2_node1", "Label 2": "list2_node2"}
        assert list_lookup._lookup["list2"] == expected_2

    def test_prop_to_list_name(self, list_lookup):
        expected = {
            "default:defaultOntoHasListOne": "list1",
            ":defaultOntoHasListOne": "list1",
            "other-onto:otherOntoHasListOne": "list1",
            "other-onto:otherOntoHasListTwo": "list2",
        }
        assert list_lookup._prop_to_list_name == expected
