import pandas as pd
import pytest

from dsp_tools.commands.excel2json.models.input_error import ListNodeProblem
from dsp_tools.commands.excel2json.models.input_error import ListSheetProblem
from dsp_tools.commands.excel2json.models.list_node import ListNode
from dsp_tools.commands.excel2json.models.list_node import ListRoot


class TestListRoot:
    def test_make_myself_comments(self) -> None:
        sub_1 = ListNode(id_="Node_1", labels={"en": "Node_1_label_en"}, parent_id="RootID")
        root = ListRoot(
            id_="RootID",
            labels={"en": "root_label_en", "de": "root_label_de"},
            nodes=[sub_1],
            comments={"en": "root_comment_en", "de": "root_comment_de"},
        )
        expected = {
            "name": "RootID",
            "labels": {"en": "root_label_en", "de": "root_label_de"},
            "comments": {"en": "root_comment_en", "de": "root_comment_de"},
        }
        res = root._make_list_root()
        assert expected == res

    def test_make_myself_no_comments(self) -> None:
        sub_1 = ListNode(id_="Node_1", labels={"en": "Node_1_label_en"}, parent_id="RootID")
        root = ListRoot(
            id_="RootID",
            labels={"en": "root_label_en", "de": "root_label_de"},
            nodes=[sub_1],
        )
        expected = {"name": "RootID", "labels": {"en": "root_label_en", "de": "root_label_de"}}
        res = root._make_list_root()
        assert expected == res

    def test_to_dict(self) -> None:
        sub_1 = ListNode(id_="Node_1", labels={"en": "Node_1_label_en"}, parent_id="RootID")
        sub_21 = ListNode(id_="SubNode_21", labels={"en": "SubNode_21_label_en"}, parent_id="RootID")
        sub_2 = ListNode(id_="Node_2", labels={"en": "Node_2_label_en"}, sub_nodes=[sub_21], parent_id="RootID")
        root = ListRoot(
            id_="RootID",
            labels={"en": "root_label_en", "de": "root_label_de"},
            nodes=[sub_1, sub_2],
        )
        expected = {
            "name": "RootID",
            "labels": {"en": "root_label_en", "de": "root_label_de"},
            "nodes": [
                {"name": "Node_1", "labels": {"en": "Node_1_label_en"}},
                {
                    "name": "Node_2",
                    "labels": {"en": "Node_2_label_en"},
                    "nodes": [{"name": "SubNode_21", "labels": {"en": "SubNode_21_label_en"}}],
                },
            ],
        }
        res = root.to_dict()
        assert res == expected


class TestListRootCreate:
    def test_problem(self) -> None:
        root = ListRoot.create(id_="", sheet_name="sheet", labels={}, comments={}, nodes=[])
        assert isinstance(root, ListSheetProblem)
        assert root.sheet_name == "sheet"
        assert root.root_problems == {
            "labels": "At least one label per list is required.",
            "name": "The name of the list does not contain any characters.",
            "list nodes": "At least one node per list is required.",
        }

    def test_wrong_language(self) -> None:
        root = ListRoot.create(
            id_="str", sheet_name="sheet", labels={"ur": "label"}, comments={"ur": "comment"}, nodes=[]
        )
        assert isinstance(root, ListSheetProblem)
        assert root.sheet_name == "sheet"
        assert root.root_problems == {
            "labels": "Only the following languages are supported: 'en', 'de', 'fr', 'it', 'rm'.",
            "comments": "Only the following languages are supported: 'en', 'de', 'fr', 'it', 'rm'.",
            "list nodes": "At least one node per list is required.",
        }

    def test_id_na(self) -> None:
        root = ListRoot.create(id_=pd.NA, sheet_name="sheet", labels={}, comments={}, nodes=[])  # type: ignore[arg-type]
        assert isinstance(root, ListSheetProblem)
        assert root.root_problems == {
            "name": "The name of the list may not be empty.",
            "labels": "At least one label per list is required.",
            "list nodes": "At least one node per list is required.",
        }

    def test_float(self) -> None:
        nd = ListNode(id_="NodeID", labels={"en": "node_label_en"}, parent_id="RootID")
        root = ListRoot.create(id_=1.123, sheet_name="sheet", labels={"en": "node_label_en"}, comments={}, nodes=[nd])
        assert isinstance(root, ListRoot)
        assert root.id_ == "1.123"
        assert root.labels == {"en": "node_label_en"}
        assert root.nodes == [nd]


class TestListNodeCreate:
    def test_problem(self) -> None:
        nd = ListNode.create(id_="", labels={}, parent_id="RootID", sub_nodes=[])
        assert isinstance(nd, ListNodeProblem)
        assert nd.node_id == ""
        assert nd.problems == {
            "name": "The name of the node does not contain any characters.",
            "labels": "At least one label per list is required.",
        }

    def test_wrong_language(self) -> None:
        root = ListNode.create(id_="str", labels={"ur": "label"}, parent_id="RootID", sub_nodes=[])
        assert isinstance(root, ListNodeProblem)
        assert root.node_id == "str"
        assert root.problems == {
            "labels": "Only the following languages are supported: 'en', 'de', 'fr', 'it', 'rm'.",
        }

    def test_id_na(self) -> None:
        root = ListNode.create(id_=pd.NA, labels={}, parent_id="", sub_nodes=[])  # type: ignore[arg-type]
        assert isinstance(root, ListNodeProblem)
        assert root.problems == {
            "name": "The name of the node may not be empty.",
            "labels": "At least one label per list is required.",
            "parent_id": "The node does not have a parent node specified.",
        }

    def test_float(self) -> None:
        nd = ListNode(id_="NodeID", labels={"en": "node_label_en"}, parent_id="RootID")
        nd_2 = ListNode.create(id_=1.123, labels={"en": "node_label_en"}, sub_nodes=[nd], parent_id="RootID")
        assert isinstance(nd_2, ListNode)
        assert nd_2.id_ == "1.123"
        assert nd_2.labels == {"en": "node_label_en"}
        assert nd_2.sub_nodes == [nd]

    def test_none(self) -> None:
        root = ListNode.create(id_="str", labels={"en": "node_label_en"}, sub_nodes=[], parent_id="RootID")
        assert isinstance(root, ListNode)
        assert root.id_ == "str"
        assert root.labels == {"en": "node_label_en"}
        assert isinstance(root.sub_nodes, list)


class TestListNode:
    def test_make_myself(self) -> None:
        nd = ListNode(id_="NodeID", labels={"en": "node_label_en"}, parent_id="RootID")
        expected = {"name": "NodeID", "labels": {"en": "node_label_en"}}
        res = nd._make_own_node()
        assert res == expected

    def test_to_dict(self) -> None:
        sub_1 = ListNode(id_="SubNode_1", labels={"en": "SubNode_1_label_en"}, parent_id="RootID")
        sub_21 = ListNode(id_="SubNode_21", labels={"en": "SubNode_21_label_en"}, parent_id="RootID")
        sub_2 = ListNode(id_="SubNode_2", labels={"en": "SubNode_2_label_en"}, sub_nodes=[sub_21], parent_id="RootID")
        test_nd = ListNode(id_="NodeID", labels={"en": "node_label_en"}, sub_nodes=[sub_1, sub_2], parent_id="RootID")

        expected = {
            "name": "NodeID",
            "labels": {"en": "node_label_en"},
            "nodes": [
                {"name": "SubNode_1", "labels": {"en": "SubNode_1_label_en"}},
                {
                    "name": "SubNode_2",
                    "labels": {"en": "SubNode_2_label_en"},
                    "nodes": [{"name": "SubNode_21", "labels": {"en": "SubNode_21_label_en"}}],
                },
            ],
        }
        res = test_nd.to_dict()
        assert res == expected


if __name__ == "__main__":
    pytest.main([__file__])
