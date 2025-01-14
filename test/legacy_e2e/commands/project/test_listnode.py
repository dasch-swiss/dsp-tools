"""end to end tests for listnode class"""

import unittest

import pytest

from dsp_tools.commands.project.models.listnode import ListNode
from dsp_tools.models.langstring import LangString
from dsp_tools.models.langstring import Languages
from dsp_tools.utils.authentication_client_live import AuthenticationClientLive
from dsp_tools.utils.connection import Connection
from dsp_tools.utils.connection_live import ConnectionLive

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

    def tearDown(self) -> None:
        """
        Logs out from DSP-API.
        For each test method, a new TestCase instance is created, so tearDown() is executed after each test method.
        """
        self.con.logout()

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

    def test_ListNode_create(self) -> None:
        """
        Create a list node
        :return: None
        """
        node = ListNode(
            con=self.con,
            project=self.project,
            label=LangString({Languages.DE: "root node 1"}),
            comments=LangString({Languages.DE: "first root node"}),
            name="test_node_1",
        ).create()
        self.assertIsNotNone(node.iri)
        self.assertEqual(node.project, self.project)
        self.assertEqual(node.label["de"], "root node 1")
        self.assertEqual(node.comments["de"], "first root node")
        self.assertEqual(node.name, "test_node_1")
        self.assertTrue(node.isRootNode)

    def test_ListNode_hierarchy(self) -> None:
        """
        Create a node and a sub-node
        :return: None
        """
        node = ListNode(
            con=self.con,
            project=self.project,
            label=LangString({Languages.EN: "root node"}),
            comments=LangString({Languages.EN: "This is a root node"}),
            name="root_node",
        ).create()
        subnode = ListNode(
            con=self.con,
            project=self.project,
            label=LangString({Languages.DE: "Ein Knoten der Liste"}),
            comments=LangString({Languages.DE: "Ein Kommentar"}),
            name="sub_node",
            parent=node,
        ).create()
        self.assertTrue(node.isRootNode)
        self.assertFalse(subnode.isRootNode)

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
