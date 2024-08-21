import pytest

from dsp_tools.commands.excel2json.new_lists.models.serialise import ListNode
from dsp_tools.commands.excel2json.new_lists.models.serialise import ListRoot


class TestListRoot:
    def test_make_myself_comments(self) -> None:
        sub_1 = ListNode(id_="Node_1", labels={"en": "Node_1_label_en"}, comments={}, parent_id="RootID")
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
        sub_1 = ListNode(id_="Node_1", labels={"en": "Node_1_label_en"}, comments={}, parent_id="RootID")
        root = ListRoot(
            id_="RootID",
            labels={"en": "root_label_en", "de": "root_label_de"},
            comments={"en": "root_comment_en", "de": "root_comment_de"},
            nodes=[sub_1],
        )
        expected = {
            "name": "RootID",
            "labels": {"en": "root_label_en", "de": "root_label_de"},
            "comments": {"en": "root_comment_en", "de": "root_comment_de"},
        }
        res = root._make_list_root()
        assert expected == res

    def test_to_dict(self) -> None:
        sub_1 = ListNode(id_="Node_1", labels={"en": "Node_1_label_en"}, comments={}, parent_id="RootID")
        sub_21 = ListNode(
            id_="SubNode_21", labels={"en": "SubNode_21_label_en"}, comments={"en": "en_comment"}, parent_id="RootID"
        )
        sub_2 = ListNode(
            id_="Node_2", labels={"en": "Node_2_label_en"}, comments={}, sub_nodes=[sub_21], parent_id="RootID"
        )
        root = ListRoot(
            id_="RootID",
            labels={"en": "root_label_en", "de": "root_label_de"},
            comments={},
            nodes=[sub_1, sub_2],
        )
        expected = {
            "name": "RootID",
            "labels": {"en": "root_label_en", "de": "root_label_de"},
            "comments": {"en": "root_label_en", "de": "root_label_de"},
            "nodes": [
                {"name": "Node_1", "labels": {"en": "Node_1_label_en"}},
                {
                    "name": "Node_2",
                    "labels": {"en": "Node_2_label_en"},
                    "nodes": [
                        {
                            "name": "SubNode_21",
                            "labels": {"en": "SubNode_21_label_en"},
                            "comments": {"en": "en_comment"},
                        }
                    ],
                },
            ],
        }
        res = root.to_dict()
        assert res == expected


class TestListNode:
    def test_make_myself(self) -> None:
        nd = ListNode(id_="NodeID", labels={"en": "node_label_en"}, comments={}, parent_id="RootID")
        expected = {"name": "NodeID", "labels": {"en": "node_label_en"}}
        res = nd._make_own_node()
        assert res == expected

    def test_to_dict(self) -> None:
        sub_1 = ListNode(
            id_="SubNode_1", labels={"en": "SubNode_1_label_en"}, comments={"en": "comment en"}, parent_id="RootID"
        )
        sub_21 = ListNode(id_="SubNode_21", labels={"en": "SubNode_21_label_en"}, comments={}, parent_id="RootID")
        sub_2 = ListNode(
            id_="SubNode_2", labels={"en": "SubNode_2_label_en"}, comments={}, sub_nodes=[sub_21], parent_id="RootID"
        )
        test_nd = ListNode(
            id_="NodeID", labels={"en": "node_label_en"}, comments={}, sub_nodes=[sub_1, sub_2], parent_id="RootID"
        )

        expected = {
            "name": "NodeID",
            "labels": {"en": "node_label_en"},
            "nodes": [
                {"name": "SubNode_1", "labels": {"en": "SubNode_1_label_en"}, "comments": {"en": "comment en"}},
                {
                    "name": "SubNode_2",
                    "labels": {"en": "SubNode_2_label_en"},
                    "nodes": [
                        {
                            "name": "SubNode_21",
                            "labels": {"en": "SubNode_21_label_en"},
                        }
                    ],
                },
            ],
        }
        res = test_nd.to_dict()
        assert res == expected


if __name__ == "__main__":
    pytest.main([__file__])
