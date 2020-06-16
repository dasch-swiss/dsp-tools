import unittest
from knora import Knora, Sipi
from jsonschema import validate
import json

class TestCreateOntology(unittest.TestCase):

    # @unittest.skip("not implemented")
    def test_create_ontology(self):
        server = "http://0.0.0.0:3333"
        sipi = "http://0.0.0.0:1024"
        email = "root@example.com"
        password = "test"
        projectcode = "00FE"
        ontoname = "KPT"

        con = Knora(server)
        con.login(email, password)

        with open("../knora/knora-schema.json") as s:
            schema = json.load(s)

        with open("test-onto.json") as f:
            ontology = json.load(f)

        validate(ontology, schema)
        print("Ontology is syntactically correct and passed validation!")

        pass

if __name__ == "__main__":
    unittest.main()
