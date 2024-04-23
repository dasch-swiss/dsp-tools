import pytest

from dsp_tools.commands.excel2json.models.list_node import ListNode
from dsp_tools.commands.excel2json.models.list_node import ListRoot


class TestListRoot:
    def test_make_myself_comments(self) -> None:
        sub_1 = ListNode(id_="Node_1", labels={"en": "Node_1_label_en"}, row_number=1)
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
        res = root._make_myself()
        assert expected == res

    def test_make_myself_no_comments(self) -> None:
        sub_1 = ListNode(id_="Node_1", labels={"en": "Node_1_label_en"}, row_number=1)
        root = ListRoot(
            id_="RootID",
            labels={"en": "root_label_en", "de": "root_label_de"},
            nodes=[sub_1],
        )
        expected = {"name": "RootID", "labels": {"en": "root_label_en", "de": "root_label_de"}}
        res = root._make_myself()
        assert expected == res

    def test_to_json(self) -> None:
        sub_1 = ListNode(id_="Node_1", labels={"en": "Node_1_label_en"}, row_number=1)
        sub_21 = ListNode(id_="SubNode_21", labels={"en": "SubNode_21_label_en"}, row_number=3)
        sub_2 = ListNode(id_="Node_2", labels={"en": "Node_2_label_en"}, row_number=2, sub_nodes=[sub_21])
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
        res = root.to_json()
        assert res == expected


class TestListNode:
    def test_make_myself(self) -> None:
        nd = ListNode(id_="NodeID", labels={"en": "node_label_en"}, row_number=1)
        expected = {"name": "NodeID", "labels": {"en": "node_label_en"}}
        res = nd._make_myself()
        assert res == expected

    def test_to_json(self) -> None:
        sub_1 = ListNode(id_="SubNode_1", labels={"en": "SubNode_1_label_en"}, row_number=1)
        sub_21 = ListNode(id_="SubNode_21", labels={"en": "SubNode_21_label_en"}, row_number=3)
        sub_2 = ListNode(id_="SubNode_2", labels={"en": "SubNode_2_label_en"}, row_number=2, sub_nodes=[sub_21])
        test_nd = ListNode(id_="NodeID", labels={"en": "node_label_en"}, row_number=0, sub_nodes=[sub_1, sub_2])

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
        res = test_nd.to_json()
        assert res == expected


if __name__ == "__main__":
    pytest.main([__file__])
