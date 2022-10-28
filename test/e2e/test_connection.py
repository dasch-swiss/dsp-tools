"""end to end tests for connection class"""
import unittest

from knora.dsplib.models.connection import Connection
from knora.dsplib.models.helpers import BaseError


class TestConnection(unittest.TestCase):
    def setUp(self) -> None:
        """
        is executed before all tests; sets up a connection and logs in as user root
        """
        self.con = Connection('http://0.0.0.0:3333')
        self.con.login('root@example.com', 'test')

    def test_Connection(self) -> None:
        self.assertIsInstance(self.con, Connection)

    def test_log_in_and_out(self) -> None:
        con = Connection('http://0.0.0.0:3333')
        con.login('root@example.com', 'test')
        self.assertIsNotNone(con.token)
        con.logout()
        self.assertIsNone(con.token)
        self.assertRaisesRegex(BaseError, 'KNORA-ERROR: status code=400*', con.login, 'invalid', 'invalid')

    def test_get(self) -> None:
        res = self.con.get("/ontology/0001/anything/simple/v2")
        self.assertIsNotNone(res['@graph'])
        self.assertRaises(BaseError, self.con.get, "/doesNotExist")
        self.con.logout()
        self.assertIsNotNone(res['@graph'])
        self.assertRaises(BaseError, self.con.get, "/doesNotExist")

    def test_put(self) -> None:
        # TODO add test
        pass

    def test_post(self) -> None:
        res_info = """{
            "@type" : "anything:Thing",
            "knora-api:attachedToProject" : {
                "@id" : "http://rdfh.ch/projects/Lw3FC39BSzCwvmdOaTyLqQ"
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

        res = self.con.post('/v2/resources', res_info)

        self.assertIsNotNone(res['@id'])
        self.assertEqual(res['@type'], 'anything:Thing')
        self.assertEqual(res['rdfs:label'], 'knora-py thing')

        res_id = res['@id']

        erase_info = f"""{{
            "@id" : "{res_id}",
            "@type" : "anything:Thing",
            "@context" : {{
                "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "knora-api" : "http://api.knora.org/ontology/knora-api/v2#",
                "rdfs" : "http://www.w3.org/2000/01/rdf-schema#",
                "xsd" : "http://www.w3.org/2001/XMLSchema#",
                "anything" : "http://0.0.0.0:3333/ontology/0001/anything/v2#"
            }}
        }}
        """

        res = self.con.post('/v2/resources/erase', erase_info)
        self.assertIsNotNone(res['knora-api:result'])
        self.assertEqual(res['knora-api:result'], 'Resource erased')

    def test_delete(self) -> None:
        # TODO add test
        pass

    def tearDown(self) -> None:
        """
        is executed after all tests are run through; performs a log out
        """
        self.con.logout()


if __name__ == '__main__':
    unittest.main()
