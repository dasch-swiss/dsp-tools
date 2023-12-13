"""end to end tests for connection class"""

import unittest

import pytest

from dsp_tools.models.exceptions import BaseError
from dsp_tools.utils.connection_live import ConnectionLive

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)
# ruff: noqa: PT027 (pytest-unittest-raises-assertion) (remove this line when pytest is used instead of unittest)


class TestConnectionLive(unittest.TestCase):
    con: ConnectionLive

    def setUp(self) -> None:
        """
        Creates a connection to DSP-API.
        For each test method, a new TestCase instance is created, so setUp() is executed before each test method.
        """
        self.con = ConnectionLive(server="http://0.0.0.0:3333")
        self.con.login(email="root@example.com", password="test")

    def tearDown(self) -> None:
        """
        Logs out from DSP-API.
        For each test method, a new TestCase instance is created, so tearDown() is executed after each test method.
        """
        self.con.logout()

    def test_Connection(self) -> None:
        self.assertIsInstance(self.con, ConnectionLive)

    def test_log_in_and_out(self) -> None:
        con = ConnectionLive("http://0.0.0.0:3333")
        con.login("root@example.com", "test")
        self.assertIsNotNone(con.token)
        con.logout()
        self.assertIsNone(con.token)
        self.assertRaisesRegex(BaseError, "KNORA-ERROR: status code=400*", con.login, "invalid", "invalid")

    def test_get(self) -> None:
        res = self.con.get("/ontology/0001/anything/simple/v2")
        self.assertIsNotNone(res["@graph"])
        self.assertRaises(BaseError, self.con.get, "/doesNotExist")
        self.con.logout()
        self.assertIsNotNone(res["@graph"])
        self.assertRaises(BaseError, self.con.get, "/doesNotExist")

    def test_post(self) -> None:
        res_info = """{
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

        res = self.con.post("/v2/resources", res_info)

        self.assertIsNotNone(res["@id"])
        self.assertEqual(res["@type"], "anything:Thing")
        self.assertEqual(res["rdfs:label"], "knora-py thing")

        res_id = res["@id"]

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

        res = self.con.post("/v2/resources/erase", erase_info)
        self.assertIsNotNone(res["knora-api:result"])
        self.assertEqual(res["knora-api:result"], "Resource erased")


if __name__ == "__main__":
    pytest.main([__file__])
