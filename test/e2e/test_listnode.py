"""end to end tests for listnode class"""
import unittest

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.langstring import Languages, LangString
from knora.dsplib.models.listnode import ListNode


class TestListNode(unittest.TestCase):
    project = "http://rdfh.ch/projects/Lw3FC39BSzCwvmdOaTyLqQ"
    otherTreeList = "http://rdfh.ch/lists/0001/otherTreeList"

    def setUp(self) -> None:
        """
        is executed before all tests; sets up a connection and logs in as user root
        """
        self.con = Connection('http://0.0.0.0:3333')
        self.con.login('root@example.com', 'test')

    def test_ListNode_read(self) -> None:
        """
        Read an existing node
        :return: None
        """
        node = ListNode(
            con=self.con,
            id=self.otherTreeList
        ).read()
        self.assertEqual(node.id, self.otherTreeList)
        self.assertEqual(node.project, self.project)
        self.assertEqual(node.label['en'], 'Tree list root')
        self.assertTrue(node.isRootNode)
        self.assertIsNone(node.children)

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
            name="test_node_1"
        ).create()
        self.assertIsNotNone(node.id)
        self.assertEqual(node.project, self.project)
        self.assertEqual(node.label['de'], "root node 1")
        self.assertEqual(node.comments['de'], "first root node")
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
            name="root_node"
        ).create()
        subnode = ListNode(
            con=self.con,
            project=self.project,
            label=LangString({Languages.DE: 'Ein Knoten der Liste'}),
            comments=LangString({Languages.DE: "Ein Kommentar"}),
            name="sub_node",
            parent=node
        ).create()
        self.assertTrue(node.isRootNode)
        self.assertFalse(subnode.isRootNode)

    def test_ListNode_update(self) -> None:
        """
        Update the data of a node
        :return: None
        """
        node = ListNode(
            con=self.con,
            project=self.project,
            label=LangString({Languages.EN: "root node 3"}),
            comments=LangString({Languages.EN: "Third root node"}),
            name="test_node"
        ).create()
        node.addLabel('de', "Neues Label")
        node.rmLabel('en')
        node.addComment('fr', 'un commentaire en français')
        node.rmComment('en')
        node.name = 'test_node_update'
        node.update()
        self.assertEqual(node.label['de'], "Neues Label")
        self.assertEqual(node.comments['fr'], 'un commentaire en français')
        self.assertEqual(node.name, 'test_node_update')

    def test_ListNode_getAllLists(self) -> None:
        """
        Get all lists
        :return: None
        """
        lists = ListNode.getAllLists(self.con, self.project)
        list_ids = list(map(lambda l: l.id, lists))
        self.assertIn(self.otherTreeList, list_ids)
        self.assertIn('http://rdfh.ch/lists/0001/treeList', list_ids)

    def test_ListNode_getAllNodes(self) -> None:
        """
        Get all nodes of a list
        :return: None
        """
        root_node = ListNode(
            con=self.con,
            id=self.otherTreeList
        ).getAllNodes()

        self.assertTrue(root_node.isRootNode)
        self.assertEqual(root_node.project, self.project)
        self.assertEqual(root_node.label['en'], 'Tree list root')
        self.assertIsNotNone(root_node.children)

        self.assertEqual(root_node.children[0].id, 'http://rdfh.ch/lists/0001/otherTreeList01')
        self.assertEqual(root_node.children[0].name, 'Other Tree list node 01')
        self.assertEqual(root_node.children[0].label['en'], 'Other Tree list node 01')

        self.assertEqual(root_node.children[1].id, 'http://rdfh.ch/lists/0001/otherTreeList02')
        self.assertEqual(root_node.children[1].name, 'Other Tree list node 02')
        self.assertEqual(root_node.children[1].label['en'], 'Other Tree list node 02')

        self.assertEqual(root_node.children[2].id, "http://rdfh.ch/lists/0001/otherTreeList03")
        self.assertEqual(root_node.children[2].name, 'Other Tree list node 03')
        self.assertEqual(root_node.children[2].label['en'], 'Other Tree list node 03')

        self.assertIsNotNone(root_node.children[2].children)
        self.assertEqual(root_node.children[2].children[0].id, 'http://rdfh.ch/lists/0001/otherTreeList10')
        self.assertEqual(root_node.children[2].children[0].name, 'Other Tree list node 10')
        self.assertEqual(root_node.children[2].children[0].label['en'], 'Other Tree list node 10')

        self.assertEqual(root_node.children[2].children[1].id, 'http://rdfh.ch/lists/0001/otherTreeList11')
        self.assertEqual(root_node.children[2].children[1].name, 'Other Tree list node 11')
        self.assertEqual(root_node.children[2].children[1].label['en'], 'Other Tree list node 11')

    def tearDown(self) -> None:
        """
        is executed after all tests are run through; performs a log out
        """
        self.con.logout()


if __name__ == '__main__':
    unittest.main()
