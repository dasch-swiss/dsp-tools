"""end to end tests for listnode class"""

import unittest

import pytest

from dsp_tools.clients.authentication_client_live import AuthenticationClientLive
from dsp_tools.clients.connection import Connection
from dsp_tools.clients.connection_live import ConnectionLive
from dsp_tools.commands.project.legacy_models.listnode import ListNode

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)


class TestListNode(unittest.TestCase):
    con: Connection
    project = "http://rdfh.ch/projects/0001"
    otherTreeList = "http://rdfh.ch/lists/0001/otherTreeList"

    def setUp(self) -> None:
        """
        Creates a connection to DSP-API.
        For each test method, a new TestCase instance is created, so setUp() is executed before each test method.
        """
        auth = AuthenticationClientLive("http://0.0.0.0:3333", "root@example.com", "test")
        self.con = ConnectionLive("http://0.0.0.0:3333", auth)

    def test_ListNode_read(self) -> None:
        """
        Read an existing node
        :return: None
        """
        node = ListNode(con=self.con, iri=self.otherTreeList).read()
        self.assertEqual(node.iri, self.otherTreeList)
        self.assertEqual(node.project, self.project)
        self.assertEqual(node.label["en"], "Tree list root")
        self.assertTrue(node.isRootNode)
        self.assertEqual(node.children, [])

    def test_ListNode_getAllLists(self) -> None:
        """
        Get all lists
        :return: None
        """
        lists = ListNode.getAllLists(self.con, self.project)
        list_ids = list(map(lambda lst: lst.iri, lists))
        self.assertIn(self.otherTreeList, list_ids)
        self.assertIn("http://rdfh.ch/lists/0001/treeList", list_ids)

    def test_ListNode_getAllNodes(self) -> None:
        """
        Get all nodes of a list
        :return: None
        """
        root_node = ListNode(con=self.con, iri=self.otherTreeList).getAllNodes()

        self.assertTrue(root_node.isRootNode)
        self.assertEqual(root_node.project, self.project)
        self.assertEqual(root_node.label["en"], "Tree list root")
        self.assertIsNotNone(root_node.children)

        self.assertEqual(root_node.children[0].iri, "http://rdfh.ch/lists/0001/otherTreeList01")
        self.assertEqual(root_node.children[0].name, "Other Tree list node 01")
        self.assertEqual(root_node.children[0].label["en"], "Other Tree list node 01")

        self.assertEqual(root_node.children[1].iri, "http://rdfh.ch/lists/0001/otherTreeList02")
        self.assertEqual(root_node.children[1].name, "Other Tree list node 02")
        self.assertEqual(root_node.children[1].label["en"], "Other Tree list node 02")

        self.assertEqual(root_node.children[2].iri, "http://rdfh.ch/lists/0001/otherTreeList03")
        self.assertEqual(root_node.children[2].name, "Other Tree list node 03")
        self.assertEqual(root_node.children[2].label["en"], "Other Tree list node 03")

        self.assertIsNotNone(root_node.children[2].children)
        self.assertEqual(root_node.children[2].children[0].iri, "http://rdfh.ch/lists/0001/otherTreeList10")
        self.assertEqual(root_node.children[2].children[0].name, "Other Tree list node 10")
        self.assertEqual(root_node.children[2].children[0].label["en"], "Other Tree list node 10")

        self.assertEqual(root_node.children[2].children[1].iri, "http://rdfh.ch/lists/0001/otherTreeList11")
        self.assertEqual(root_node.children[2].children[1].name, "Other Tree list node 11")
        self.assertEqual(root_node.children[2].children[1].label["en"], "Other Tree list node 11")


if __name__ == "__main__":
    pytest.main([__file__])
