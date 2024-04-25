import pandas as pd
import pytest
import regex
from pandas.testing import assert_frame_equal

from dsp_tools.commands.excel2json.models.list_node import ListNode
from dsp_tools.commands.excel2json.models.list_node import ListRoot
from dsp_tools.commands.excel2json.new_lists import _add_nodes_to_parent
from dsp_tools.commands.excel2json.new_lists import _fill_id_column
from dsp_tools.commands.excel2json.new_lists import _fill_parent_id
from dsp_tools.commands.excel2json.new_lists import _get_all_languages_for_columns
from dsp_tools.commands.excel2json.new_lists import _get_column_nums
from dsp_tools.commands.excel2json.new_lists import _get_columns_preferred_lang
from dsp_tools.commands.excel2json.new_lists import _get_labels
from dsp_tools.commands.excel2json.new_lists import _get_lang_string
from dsp_tools.commands.excel2json.new_lists import _get_preferred_language
from dsp_tools.commands.excel2json.new_lists import _get_reverse_sorted_columns_list
from dsp_tools.commands.excel2json.new_lists import _handle_ids
from dsp_tools.commands.excel2json.new_lists import _make_list_nodes
from dsp_tools.commands.excel2json.new_lists import _make_one_list
from dsp_tools.commands.excel2json.new_lists import _make_one_node
from dsp_tools.models.exceptions import InputError


class TestMakeOneList:
    def test_make_lists_all_good(self) -> None:
        test_df = pd.DataFrame(
            {
                "id": ["list_id", "1", "1.1", "2", "3", "3.1", "3.2", "3.2.1", "3.2.2"],
                "parent_id": ["list_id", "list_id", "1", "list_id", "list_id", "3", "3", "3.2", "3.2"],
                "index": [0, 1, 2, 3, 4, 5, 6, 7, 8],
                "en_list": [
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                    "Listname_en",
                ],
                "de_list": [
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                    "Listname_de",
                ],
                "en_1": [
                    pd.NA,
                    "Node_en_1",
                    "Node_en_1",
                    "Node_en_2",
                    "Node_en_3",
                    "Node_en_3",
                    "Node_en_3",
                    "Node_en_3",
                    "Node_en_3",
                ],
                "de_1": [
                    pd.NA,
                    "Node_de_1",
                    "Node_de_1",
                    "Node_de_2",
                    "Node_de_3",
                    "Node_de_3",
                    "Node_de_3",
                    "Node_de_3",
                    "Node_de_3",
                ],
                "en_2": [
                    pd.NA,
                    pd.NA,
                    "Node_en_1.1",
                    pd.NA,
                    pd.NA,
                    "Node_en_3.1",
                    "Node_en_3.2",
                    "Node_en_3.2",
                    "Node_en_3.2",
                ],
                "de_2": [
                    pd.NA,
                    pd.NA,
                    "Node_de_1.1",
                    pd.NA,
                    pd.NA,
                    "Node_de_3.1",
                    "Node_de_3.2",
                    "Node_de_3.2",
                    "Node_de_3.2",
                ],
                "en_3": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "Node_en_3.2.1", "Node_en_3.2.2"],
                "de_3": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "Node_de_3.2.1", "Node_de_3.2.2"],
            }
        )
        res = _make_one_list(test_df, "Sheet1")
        assert isinstance(res, ListRoot)
        assert res.id_ == "list_id"
        assert res.labels == {"en": "Listname_en", "de": "Listname_de"}
        assert len(res.nodes) == 3
        assert res.nodes[0].id_ == "1"
        assert res.nodes[1].id_ == "2"
        assert res.nodes[2].id_ == "3"
        assert res.nodes[2].sub_nodes[0].id_ == "3.1"
        assert res.nodes[2].sub_nodes[1].id_ == "3.2"
        assert res.nodes[2].sub_nodes[1].sub_nodes[0].id_ == "3.2.1"
        assert res.nodes[2].sub_nodes[1].sub_nodes[1].id_ == "3.2.2"


class TestFillIdColumn:
    def test_to_fill(self) -> None:
        test_df = pd.DataFrame(
            {
                "ID (optional)": [pd.NA, "1", pd.NA, "3", pd.NA, pd.NA, pd.NA, pd.NA],
                "en_list": ["list_en", "list_en", "list_en", "list_en", "list_en", "list_en", "list_en", "list_en"],
                "en_1": [pd.NA, "nd_en_1", "nd_en_2", "nd_en_3", "nd_en_3", "nd_en_3", "nd_en_3", "nd_en_3"],
                "en_2": [pd.NA, pd.NA, pd.NA, pd.NA, "nd_en_3.1", "nd_en_3.2", "nd_en_3.2", "nd_en_3.2"],
                "en_3": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "nd_en_3.2.1", "nd_en_3.2.2"],
            }
        )
        expected = [
            "list_en",
            pd.NA,
            "nd_en_2",
            pd.NA,
            "nd_en_3.1",
            "nd_en_3.2",
            "nd_en_3.2.1",
            "nd_en_3.2.2",
        ]
        res = _fill_id_column(test_df, "en")
        assert res["auto_id"].to_list() == expected

    def test_nothing_to_fill(self) -> None:
        test_df = pd.DataFrame(
            {
                "ID (optional)": ["list_en", "1", "2", "3", "3.1", "3.2", "3.2.1", "3.2.2"],
            }
        )
        expected = pd.DataFrame(
            {
                "ID (optional)": ["list_en", "1", "2", "3", "3.1", "3.2", "3.2.1", "3.2.2"],
                "auto_id": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA],
            }
        )
        res = _fill_id_column(test_df, "en")
        assert_frame_equal(res, expected)


def test_handle_ids() -> None:
    test_df = pd.DataFrame(
        {
            "ID (optional)": [pd.NA, pd.NA, "2", "3", pd.NA, "5", "6", pd.NA],
            "en_list": ["list_en", "list_en", "list_en", "list_en", "list_en", "list_en", "list_en", "list_en"],
            "en_1": ["list_en", "nd_en_1", "nd_en_2", "nd_en_3", "nd_en_4", "nd_en_5", "nd_en_6", "nd_en_7"],
        }
    )
    res = _handle_ids(test_df, "en")
    assert res["id"].tolist() == ["list_en", "nd_en_1", "2", "3", "nd_en_4", "5", "6", "nd_en_7"]


def test_fill_parent_id() -> None:
    test_df = pd.DataFrame(
        {
            "ID (optional)": [
                "list_en",
                "1",
                "2",
                "3",
                "3.1",
                "3.2",
                "3.2.1",
                "3.2.2",
            ],
            "en_list": ["list_en", "list_en", "list_en", "list_en", "list_en", "list_en", "list_en", "list_en"],
            "en_1": [pd.NA, "nd_en_1", "nd_en_2", "nd_en_3", "nd_en_3", "nd_en_3", "nd_en_3", "nd_en_3"],
            "en_2": [pd.NA, pd.NA, pd.NA, pd.NA, "nd_en_3.1", "nd_en_3.2", "nd_en_3.2", "nd_en_3.2"],
            "en_3": [pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, "nd_en_3.2.1", "nd_en_3.2.2"],
        }
    )
    expected = ["list_en", "list_en", "list_en", "list_en", "3", "3", "3.2", "3.2"]
    res = _fill_parent_id(test_df, "en")
    assert res["parent_id"].to_list() == expected


def test_add_nodes_to_parent() -> None:
    nd_1 = ListNode("1", {"en": "Node_en_1", "de": "Node_de_1"}, 1, parent_id="list_id")
    nd_2 = ListNode("2", {"en": "Node_en_2", "de": "Node_de_2"}, 2, parent_id="list_id")
    nd_11 = ListNode("1.1", {"en": "Node_en_1.1", "de": "Node_de_1.1"}, 3, parent_id="1")
    nd_12 = ListNode("1.2", {"en": "Node_en_2.1", "de": "Node_de_1.2"}, 4, parent_id="1")
    test_dict = {"1": nd_1, "2": nd_2, "1.1": nd_11, "1.2": nd_12}
    expected = [nd_1, nd_2]
    res = _add_nodes_to_parent(test_dict, "list_id")
    assert res == expected
    assert nd_1.sub_nodes == [nd_11, nd_12]
    assert not nd_2.sub_nodes
    assert not nd_11.sub_nodes
    assert not nd_12.sub_nodes


def test_make_list_nodes_with_valid_data() -> None:
    data = {
        "id": ["list_id", "id_1", "id_1.1", "id_2"],
        "parent_id": ["list_id", "list_id", "id_1", "list_id"],
        "en_list": ["Listname_en", "Listname_en", "Listname_en", "Listname_en"],
        "de_list": ["Listname_de", "Listname_de", "Listname_de", "Listname_de"],
        "en_1": [pd.NA, "Node1", "Node1", "Node2"],
        "de_1": [pd.NA, "Knoten1", "Knoten1", "Knoten2"],
        "en_2": [pd.NA, pd.NA, "Node1.1", pd.NA],
        "de_2": [pd.NA, pd.NA, "Knoten1.1", pd.NA],
        "index": [3, 0, 2, 1],
    }
    df = pd.DataFrame(data)
    node_dict, problems = _make_list_nodes(df)
    assert len(node_dict) == 3
    assert len(problems) == 0
    one = node_dict["id_1"]
    assert isinstance(one, ListNode)
    assert one.id_ == "id_1"
    assert one.labels == {"en": "Node1", "de": "Knoten1"}
    assert one.row_number == 0
    assert one.parent_id == "list_id"
    assert not one.sub_nodes
    one_one = node_dict["id_1.1"]
    assert isinstance(one_one, ListNode)
    assert one_one.id_ == "id_1.1"
    assert one_one.labels == {"en": "Node1.1", "de": "Knoten1.1"}
    assert one_one.row_number == 2
    assert one_one.parent_id == "id_1"
    assert not one_one.sub_nodes
    two = node_dict["id_2"]
    assert isinstance(two, ListNode)
    assert two.id_ == "id_2"
    assert two.labels == {"en": "Node2", "de": "Knoten2"}
    assert two.row_number == 1
    assert two.parent_id == "list_id"
    assert not two.sub_nodes


class TestMakeOneNode:
    def test_all_good_first(self) -> None:
        test_series = pd.Series(
            {
                "id": "node_id",
                "parent_id": "list_id",
                "index": 1,
                "en_list": "Listname_en",
                "en_1": "Node_en_1",
                "de_1": "Node_de_1",
                "en_2": pd.NA,
                "de_2": pd.NA,
            }
        )
        nd = _make_one_node(test_series, [["en_2", "de_2"], ["en_1", "de_1"]])
        assert isinstance(nd, ListNode)
        assert nd.id_ == "node_id"
        assert nd.labels == {"en": "Node_en_1", "de": "Node_de_1"}
        assert nd.row_number == 1
        assert not nd.sub_nodes

    def test_all_good_second(self) -> None:
        test_series = pd.Series(
            {
                "id": "node_id",
                "parent_id": "list_id",
                "index": 2,
                "en_list": "Listname_en",
                "en_1": "Node_en_1",
                "de_1": "Node_de_1",
                "en_2": "Node_en_2",
                "de_2": "Node_de_2",
            }
        )
        nd = _make_one_node(test_series, [["en_2", "de_2"], ["en_1", "de_1"]])
        assert isinstance(nd, ListNode)
        assert nd.id_ == "node_id"
        assert nd.labels == {"en": "Node_en_2", "de": "Node_de_2"}
        assert nd.row_number == 2
        assert not nd.sub_nodes


def test_get_columns_preferred_lang_returns_expected_columns() -> None:
    columns = pd.Index(["en_2", "de_1", "en_1", "it_1"])
    assert _get_columns_preferred_lang(columns, "en") == ["en_1", "en_2"]


def test_get_columns_preferred_lang_returns_empty_list_for_no_match() -> None:
    columns = pd.Index(["de_1", "de_2", "it_1"])
    assert not _get_columns_preferred_lang(columns, "en")


def test_sorted_columns_returns_expected_result() -> None:
    df = pd.DataFrame(columns=["en_1", "de_2", "de_1", "en_2"])
    res = _get_reverse_sorted_columns_list(df)
    assert len(res) == 2
    assert set(res[0]) == {"de_2", "en_2"}
    assert set(res[1]) == {"de_1", "en_1"}


class TestGetLabels:
    def test_correct_labels_for_all_languages(self) -> None:
        row = pd.Series(
            {
                "en_1": "Hello",
                "de_1": "Hallo",
                "fr_1": "Bonjour",
                "it_1": "Ciao",
                "rm_1": pd.NA,
                "en_2": "other",
                "de_2": pd.NA,
            }
        )
        cols = ["en_1", "de_1", "fr_1", "it_1", "rm_1"]
        expected = {"en": "Hello", "de": "Hallo", "fr": "Bonjour", "it": "Ciao"}
        assert _get_labels(row, cols) == expected

    def test_returns_empty_dict_for_no_languages(self) -> None:
        row = pd.Series(
            {
                "en_1": pd.NA,
                "de_1": pd.NA,
                "fr_1": pd.NA,
                "fr_2": pd.NA,
                "it_2": pd.NA,
                "rm_2": pd.NA,
            }
        )
        cols = ["en_1", "de_1", "fr_1"]
        assert not _get_labels(row, cols)

    def test_parent(self) -> None:
        row = pd.Series(
            {
                "en_list": "english",
                "de_list": "german",
                "fr_1": pd.NA,
                "fr_2": pd.NA,
                "it_2": pd.NA,
                "rm_2": pd.NA,
            }
        )
        cols = ["en_list", "de_list"]
        assert _get_labels(row, cols) == {"en": "english", "de": "german"}


def test_get_lang_string_good() -> None:
    assert _get_lang_string("en_1") == "en"


def test_get_lang_string_raises() -> None:
    assert not _get_lang_string("ru_1")


class TestGetRemainingColumns:
    def test_with_matching_columns(self) -> None:
        columns = pd.Index(["en_1", "de_2", "fr_3"])
        assert _get_column_nums(columns) == [1, 2, 3]

    def test_with_list_language_columns(self) -> None:
        columns = pd.Index(["en_1", "de_2", "fr_3", "de_list"])
        assert _get_column_nums(columns) == [1, 2, 3]

    def test_with_non_numeric_columns(self) -> None:
        columns = pd.Index(["en_1", "de_2", "fr_3", "it_4", "rm_5", "en_other"])
        assert _get_column_nums(columns) == [1, 2, 3, 4, 5]


class TestGetAllLanguagesForColumns:
    def test_get_all_languages_for_columns_returns_correct_languages(self) -> None:
        columns = pd.Index(["en_1", "de_1", "fr_1", "it_1", "rm_1", "en_2"])
        ending = "1"
        assert _get_all_languages_for_columns(columns, ending) == {"en", "de", "fr", "it", "rm"}

    def test_get_all_languages_for_columns_returns_empty_list_for_no_match(self) -> None:
        columns = pd.Index(["en_1", "de_1", "fr_1", "it_1", "rm_1", "en_2", "de_2", "fr_2", "it_2", "rm_2"])
        ending = "3"
        assert not _get_all_languages_for_columns(columns, ending)


class TestGetPreferredLanguageForId:
    def test_get_preferred_language_for_id_en(self) -> None:
        columns = pd.Index(["en_1", "de_1", "fr_1", "it_1", "rm_1"])
        assert _get_preferred_language(columns, "1") == "en"

    def test_get_preferred_language_for_id_de(self) -> None:
        columns = pd.Index(["de_1", "fr_1", "it_1", "rm_1"])
        assert _get_preferred_language(columns, "1") == "de"

    def test_get_preferred_language_for_id_fr(self) -> None:
        columns = pd.Index(["fr_1", "it_1", "rm_1"])
        assert _get_preferred_language(columns, "1") == "fr"

    def test_get_preferred_language_for_id_it(self) -> None:
        columns = pd.Index(["it_1", "rm_1"])
        assert _get_preferred_language(columns, "1") == "it"

    def test_get_preferred_language_for_id_rm(self) -> None:
        columns = pd.Index(["rm_1"])
        assert _get_preferred_language(columns, "1") == "rm"

    def test_get_preferred_language_for_id_raises(self) -> None:
        columns = pd.Index(["es_1"])
        msg = regex.escape(
            "The columns may only contain the languages: 'en', 'de', 'fr', 'it', 'rm'.\n" "The columns are: es_1"
        )
        with pytest.raises(InputError, match=msg):
            _get_preferred_language(columns, "1")


if __name__ == "__main__":
    pytest.main([__file__])
