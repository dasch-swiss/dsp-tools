import pytest

from dsp_tools.commands.excel2json.models.list_node import ListNode
from dsp_tools.commands.excel2json.models.list_node import ListRoot


class TestListRoot:
    def test_make_myself_comments(self) -> None:
        root = ListRoot(
            "RootID",
            {"en": "root_label_en", "de": "root_label_de"},
            [],
            {"en": "root_comment_en", "de": "root_comment_de"},
        )
        expected = {
            "name": "RootID",
            "labels": {"en": "root_label_en", "de": "root_label_de"},
            "comments": {"en": "root_comment_en", "de": "root_comment_de"},
        }
        res = root._make_list_root()
        assert expected == res

    def test_make_myself_no_comments(self) -> None:
        root = ListRoot(
            "RootID",
            {"en": "root_label_en", "de": "root_label_de"},
            [],
        )
        expected = {"name": "RootID", "labels": {"en": "root_label_en", "de": "root_label_de"}}
        res = root._make_list_root()
        assert expected == res

    def test_to_json(self) -> None:
        sub_1 = ListNode("Node_1", {"en": "Node_1_label_en"}, 1)
        sub_21 = ListNode("SubNode_21", {"en": "SubNode_21_label_en"}, 21)
        sub_2 = ListNode("Node_2", {"en": "Node_2_label_en"}, 2, [sub_21])
        root = ListRoot(
            "RootID",
            {"en": "root_label_en", "de": "root_label_de"},
            [sub_1, sub_2],
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


class TestListNode:
    def test_make_myself(self) -> None:
        nd = ListNode("NodeID", {"en": "node_label_en"}, 1)
        expected = {"name": "NodeID", "labels": {"en": "node_label_en"}}
        res = nd._make_own_node()
        assert res == expected

    def test_to_json(self) -> None:
        sub_1 = ListNode("SubNode_1", {"en": "SubNode_1_label_en"}, 1)
        sub_21 = ListNode("SubNode_21", {"en": "SubNode_21_label_en"}, 21)
        sub_2 = ListNode("SubNode_2", {"en": "SubNode_2_label_en"}, 2, [sub_21])
        test_nd = ListNode("NodeID", {"en": "node_label_en"}, 0, [sub_1, sub_2])

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
