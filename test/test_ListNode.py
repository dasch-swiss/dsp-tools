import unittest
import pprint
import requests
from urllib.parse import quote_plus

from context import BaseError, Languages, Actions, LangString
from context import Project, ListNode, Connection


def erase_node(iri = None):
    if iri is None:
        return
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

    """ % (iri,iri)
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


class TestListNode(unittest.TestCase):
    iri = None
    project = 'http://rdfh.ch/projects/0001'
    label = LangString({Languages.DE: 'Eine Liste'})
    comment = LangString({Languages.DE: 'Dies ist der Root-Node einer Liste'})
    name = 'my_root'

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
        self.iri = node.id
        return node

    def tearDown(self):
        res = erase_node(self.iri)

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

    def test_ListNode_create(self):
        node = self.createTestNode()
        self.assertEqual(node.project, self.project)
        self.assertEqual(node.label['de'], self.label['de'])
        self.assertEqual(node.comment['de'], self.comment['de'])
        self.assertEqual(node.name, self.name)
        self.assertTrue(node.isRootNode)
        self.iri = node.id

if __name__ == '__main__':
    unittest.main()
