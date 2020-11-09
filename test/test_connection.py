import sys
import unittest
import pprint
import os

sys.path.append("../knora")

from dsplib.models.helpers import BaseError
from dsplib.models.connection import Connection


class TestConnection(unittest.TestCase):
    def test_Connection(self):
        con = Connection('http://0.0.0.0:3333')
        self.assertIsInstance(con, Connection)

    def test_loginout(self):
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        self.assertIsNotNone(con.token)
        con.logout()
        self.assertIsNone(con.token)
        self.assertRaisesRegex(BaseError, 'KNORA-ERROR: status code=400*', con.login, 'invalid', 'invalid')

    def test_get(self):
        con = Connection('http://0.0.0.0:3333')
        res = con.get("/ontology/0001/anything/simple/v2")
        con.logout()
        self.assertIsNotNone(res['@graph'])
        self.assertRaises(BaseError, con.get, "/gagaga")

    def test_put(self):
        pass

    def test_post(self):
        resinfo = """{
            "@type" : "anything:Thing",
            "knora-api:attachedToProject" : {
                "@id" : "http://rdfh.ch/projects/0001"
            },
            "anything:hasBoolean" : {
                "@type" : "knora-api:BooleanValue",
                "knora-api:booleanValueAsBoolean" : true
            },
            "rdfs:label" : "knora-py thing",
            "knora-api:hasPermissions" : "CR knora-admin:Creator|V http://rdfh.ch/groups/0001/thing-searcher",
            "@context" : {
                "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "knora-api" : "http://api.knora.org/ontology/knora-api/v2#",
                "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
                "xsd" : "http://www.w3.org/2001/XMLSchema#",
                "anything" : "http://0.0.0.0:3333/ontology/0001/anything/v2#"
            }
        }
        """
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        res = con.post('/v2/resources', resinfo)
        self.assertIsNotNone(res['@id'])
        id = res['@id']
        self.assertEqual(res['@type'], 'anything:Thing')
        self.assertEqual(res['rdfs:label'], 'knora-py thing')

        eraseinfo = """{
            "@id" : "%s",
            "@type" : "anything:Thing",
            "@context" : {
                "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "knora-api" : "http://api.knora.org/ontology/knora-api/v2#",
                "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
                "xsd" : "http://www.w3.org/2001/XMLSchema#",
                "anything" : "http://0.0.0.0:3333/ontology/0001/anything/v2#"
            }
        }
        """ % id
        res = con.post('/v2/resources/erase', eraseinfo)
        self.assertIsNotNone(res['knora-api:result'])
        self.assertEqual(res['knora-api:result'], 'Resource erased')

    def test_delete(self):
        pass


if __name__ == '__main__':
    unittest.main()
