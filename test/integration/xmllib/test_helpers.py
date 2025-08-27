# mypy: disable-error-code="method-assign,no-untyped-def"
import warnings

import pytest

from dsp_tools.xmllib.general_functions import ListLookup


@pytest.fixture
def list_lookup_en() -> ListLookup:
    with warnings.catch_warnings(record=True) as caught_warnings:
        lst = ListLookup.create_new("testdata/json-project/test-list-lookup.json", "en", "default")
    assert len(caught_warnings) == 0
    return lst


@pytest.fixture
def list_lookup_de() -> ListLookup:
    with warnings.catch_warnings(record=True) as caught_warnings:
        lst = ListLookup.create_new("testdata/json-project/test-list-lookup.json", "de", "default")
    assert len(caught_warnings) == 1
    return lst


class TestGetListLookup:
    def test_lookup_all_labels_have_lang(self, list_lookup_en):
        assert list_lookup_en._label_language == "en"
        assert set(list_lookup_en._lookup.keys()) == {"list1", "list2"}
        expected_1 = {
            "label 1": "list1_node1",
            "Label 1": "list1_node1",
            "label 2": "list1_node2",
            "label 2.1": "list1_node2.1",
            "label 2.2": "list1_node2.2",
            "label 2.2.1": "list1_node2.2.1",
        }
        assert list_lookup_en._lookup["list1"] == expected_1
        expected_2 = {"label 1": "list2_node1", "label 2": "list2_node2"}
        assert list_lookup_en._lookup["list2"] == expected_2

    def test_lookup_some_language_labels_missing(self, list_lookup_de):
        assert list_lookup_de._label_language == "de"
        assert set(list_lookup_de._lookup.keys()) == {"list1", "list2"}
        expected_1 = {
            "Deutsch 1": "list1_node1",
            "deutsch 1": "list1_node1",
            "deutsch 2": "list1_node2",
            "deutsch 2.1": "list1_node2.1",
            "deutsch 2.2": "list1_node2.2",
        }
        assert list_lookup_de._lookup["list1"] == expected_1
        expected_2 = {
            "Deutsch 1": "list2_node1",
            "Deutsch 2": "list2_node2",
            "deutsch 1": "list2_node1",
            "deutsch 2": "list2_node2",
        }
        assert list_lookup_de._lookup["list2"] == expected_2

    def test_prop_to_list_name(self, list_lookup_en):
        expected = {
            "default:defaultOntoHasListOne": "list1",
            ":defaultOntoHasListOne": "list1",
            "other-onto:otherOntoHasListOne": "list1",
            "other-onto:otherOntoHasListTwo": "list2",
        }
        assert list_lookup_en._prop_to_list_name == expected
