import pytest

from dsp_tools.xmllib.helpers import ListLookup
from dsp_tools.xmllib.helpers import get_list_lookup


@pytest.fixture
def list_lookup() -> ListLookup:
    return get_list_lookup("testdata/json-project/test-list-lookup.json", "en", "default")


def test_get_list_lookup(list_lookup):
    pass


class TestListLookup:
    def test_get_list_lookup(self, list_lookup):
        pass

    def test_get_node_via_list_name(self, list_lookup):
        pass

    def test_get_node_via_list_name_warns_wrong_list(self, list_lookup):
        pass

    def test_get_node_via_list_name_warns_wrong_node(self, list_lookup):
        pass

    def test_get_node_via_property(self, list_lookup):
        pass

    def test_get_node_via_property_warns_wrong_property(self, list_lookup):
        pass
