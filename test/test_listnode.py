import unittest
import pprint
import requests
from urllib.parse import quote_plus

from connection import Connection
from helpers import BaseError, Languages, Actions, LangString
from listnode import ListNode
from project import Project




class TestListNode(unittest.TestCase):
    iris = []
    project = 'http://rdfh.ch/projects/0001'
    label = LangString({Languages.DE: 'Eine Liste'})
    comment = LangString({Languages.DE: 'Dies ist der Root-Node einer Liste'})
    name = 'my_root'

    def erase_node(self):
        for iri in self.iris:
            sparql = """
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            PREFIX knora-base: <http://www.knora.org/ontology/knora-base#>
                DELETE {
                    GRAPH <http://www.knora.org/data/0001/anything> {
                        <%s> ?property ?value
                    }
                } WHERE {
                    GRAPH <http://www.knora.org/data/0001/anything> {
                        <%s> ?property ?value
                    }
                }
            """ % (iri, iri)
            req = requests.post('http://localhost:7200/repositories/knora-test/statements',
                                headers={'Content-Type': 'application/sparql-update',
                                         'Accept': 'application/json, text/plain, */*'},
                                data=sparql)
            if 'error' in req:
                print('ERROR: ' + req.error)
            if req.status_code != 204:
                print('STATUS-CODE: ' + str(req.status_code))
                print('TEXT: ' + req.text)
                return req.status_code

    def createTestNode(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        node = ListNode(
            con=con,
            project=self.project,
            label=self.label,
            comment=self.comment,
            name=self.name
        ).create()
        self.assertIsNotNone(node.id)
        self.iris.append(node.id)
        return node

    def tearDown(self):
        res = self.erase_node()

    def test_ListNode(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')


    def test_ListNode_read(self):
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
        node = self.createTestNode()
        self.assertEqual(node.project, self.project)
        self.assertEqual(node.label['de'], self.label['de'])
        self.assertEqual(node.comment['de'], self.comment['de'])
        self.assertEqual(node.name, self.name)
        self.assertTrue(node.isRootNode)
        self.iris.append(node.id)

    def test_ListNode_hierarchy(self):
        node = self.createTestNode()
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        node2 = ListNode(
            con=con,
            project=self.project,
            label=LangString({Languages.DE: 'Eine Knoten der Liste'}),
            comment=LangString({Languages.DE: "So ein Kommentar"}),
            name="NODE2",
            parent=node
        ).create()
        self.iris.append(node2.id)
        self.assertEqual(node2.label['de'], 'Eine Knoten der Liste')
        self.assertEqual(node2.comment['de'], "So ein Kommentar")
        self.assertEqual(node2.name, "NODE2")
        self.assertFalse(node2.isRootNode)

    def test_ListNode_update(self):
        node = self.createTestNode()
        node.addLabel('fr', 'Une racine d\' une liste')
        node.rmLabel('de')
        node.addComment('fr', 'un commentaire en français')
        node.rmComment('de')
        node.name = 'GAGAGA'
        node.update()
        self.assertEqual(node.label['fr'], 'Une racine d\' une liste')
        self.assertEqual(node.comment['fr'], 'un commentaire en français')
        self.assertEqual(node.name, 'GAGAGA')

    def test_ListNode_getAllLists(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        lists = ListNode.getAllLists(con, 'http://rdfh.ch/projects/0001')
        tmp = list(map(lambda a: a.id, lists))
        self.assertIn('http://rdfh.ch/lists/0001/otherTreeList', tmp)
        self.assertIn('http://rdfh.ch/lists/0001/treeList', tmp)

    def test_ListNode_getAllNodes(self):
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
