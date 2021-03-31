import unittest

from dsplib.models.connection import Connection
from dsplib.models.langstring import Languages, LangStringParam, LangString
from dsplib.models.listnode import ListNode


class TestListNode(unittest.TestCase):
    project = 'http://rdfh.ch/projects/0001'

    def test_ListNode_read(self):
        """
        Read an existing node
        :return: None
        """
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        node = ListNode(
            con=con,
            id='http://rdfh.ch/lists/0001/otherTreeList'
        ).read()
        self.assertEqual(node.id, 'http://rdfh.ch/lists/0001/otherTreeList')
        self.assertEqual(node.project, 'http://rdfh.ch/projects/0001')
        self.assertEqual(node.label['en'], 'Tree list root')
        self.assertTrue(node.isRootNode)

    def test_ListNode_read2(self):
        """
        read another existing node
        :return:
        """
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        node = ListNode(
            con=con,
            id='http://rdfh.ch/lists/0001/otherTreeList03'
        ).read()
        self.assertEqual(node.id, 'http://rdfh.ch/lists/0001/otherTreeList03')
        self.assertEqual(node.label['en'], 'Other Tree list node 03')
        self.assertFalse(node.isRootNode)
        self.assertEqual(node.rootNodeIri, 'http://rdfh.ch/lists/0001/otherTreeList')
        self.assertIsNone(node.children)

    def test_ListNode_create(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        node = ListNode(
            con=con,
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

    def test_ListNode_hierarchy(self):
        """
        Create a node and a sub-node
        :return: None
        """
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        node = ListNode(
            con=con,
            project=self.project,
            label=LangString({Languages.DE: "root node 2"}),
            comments=LangString({Languages.DE: "second root node"}),
            name="test_node_2"
        ).create()
        node2 = ListNode(
            con=con,
            project=self.project,
            label=LangString({Languages.DE: 'Eine Knoten der Liste'}),
            comments=LangString({Languages.DE: "So ein Kommentar"}),
            name="NODE2",
            parent=node
        ).create()
        self.assertEqual(node2.label['de'], 'Eine Knoten der Liste')
        self.assertEqual(node2.comments['de'], "So ein Kommentar")
        self.assertEqual(node2.name, "NODE2")
        self.assertFalse(node2.isRootNode)

    def test_ListNode_update(self):
        """
        Update the data of a node...
        :return:
        """
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        node = ListNode(
            con=con,
            project=self.project,
            label=LangString({Languages.DE: "root node 3"}),
            comments=LangString({Languages.DE: "Third root node"}),
            name="test_node_3"
        ).create()
        node.addLabel('fr', 'Une racine d\' une liste')
        node.rmLabel('de')
        node.addComment('fr', 'un commentaire en français')
        node.rmComment('de')
        node.name = 'GAGAGA'
        node.update()
        self.assertEqual(node.label['fr'], 'Une racine d\' une liste')
        self.assertEqual(node.comments['fr'], 'un commentaire en français')
        self.assertEqual(node.name, 'GAGAGA')

    def test_ListNode_getAllLists(self):
        """
        gett all root nodes, that is all lists
        :return: None
        """
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        lists = ListNode.getAllLists(con, 'http://rdfh.ch/projects/0001')
        tmp = list(map(lambda a: a.id, lists))
        self.assertIn('http://rdfh.ch/lists/0001/otherTreeList', tmp)
        self.assertIn('http://rdfh.ch/lists/0001/treeList', tmp)

    def test_ListNode_getAllNodes(self):
        """
        Get all node of a list
        :return: None
        """
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        root = ListNode(
            con=con,
            id='http://rdfh.ch/lists/0001/otherTreeList'
        ).getAllNodes()
        self.assertTrue(root.isRootNode)
        self.assertEqual(root.project, 'http://rdfh.ch/projects/0001')
        self.assertEqual(root.label['en'], 'Tree list root')
        self.assertIsNotNone(root.children)

        self.assertEqual(root.children[0].id, 'http://rdfh.ch/lists/0001/otherTreeList01')
        self.assertEqual(root.children[0].name, 'Other Tree list node 01')
        self.assertEqual(root.children[0].label['en'], 'Other Tree list node 01')

        self.assertEqual(root.children[1].id, 'http://rdfh.ch/lists/0001/otherTreeList02')
        self.assertEqual(root.children[1].name, 'Other Tree list node 02')
        self.assertEqual(root.children[1].label['en'], 'Other Tree list node 02')

        self.assertEqual(root.children[2].id, 'http://rdfh.ch/lists/0001/otherTreeList03')
        self.assertEqual(root.children[2].name, 'Other Tree list node 03')
        self.assertEqual(root.children[2].label['en'], 'Other Tree list node 03')

        self.assertIsNotNone(root.children[2].children)
        self.assertEqual(root.children[2].children[0].id, 'http://rdfh.ch/lists/0001/otherTreeList10')
        self.assertEqual(root.children[2].children[0].name, 'Other Tree list node 10')
        self.assertEqual(root.children[2].children[0].label['en'], 'Other Tree list node 10')

        self.assertEqual(root.children[2].children[1].id, 'http://rdfh.ch/lists/0001/otherTreeList11')
        self.assertEqual(root.children[2].children[1].name, 'Other Tree list node 11')
        self.assertEqual(root.children[2].children[1].label['en'], 'Other Tree list node 11')

        #self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
