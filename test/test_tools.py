import unittest
import json

from dsplib.utils.onto_get import get_ontology
from dsplib.utils.onto_get import get_ontology
from dsplib.utils.onto_validate import validate_ontology
from dsplib.utils.onto_create_ontology import create_ontology
from knora.dsplib.utils.xml_upload import xml_upload


class TestTools(unittest.TestCase):

    def test_get(self):

        with open('testdata/anything.json') as f:
            jsonstr = f.read()
        refobj = json.loads(jsonstr)

        get_ontology(projident="anything",
                     outfile="_anything.json",
                     server="http://0.0.0.0:3333",
                     user="root@example.com",
                     password="test",
                     verbose=True)

        with open('_anything.json') as f:
            jsonstr = f.read()
        jsonobj = json.loads(jsonstr)

        self.assertEqual(refobj["project"]["shortcode"], jsonobj["project"]["shortcode"])

    def test_validate_onto(self):
        validate_ontology('testdata/test-onto.json')

    def test_create_onto(self):
        create_ontology(input_file='testdata/test-onto.json',
                        lists_file='lists-out.json',
                        server="http://0.0.0.0:3333",
                        user="root@example.com",
                        password="test",
                        verbose=True,
                        dump=True)

    def test_xmlupload(self):
        xml_upload(input_file="testdata/test-data.xml",
                   server="http://0.0.0.0:3333",
                   user="root@example.com",
                   password="test",
                   imgdir="testdata/bitstreams",
                   sipi="http://0.0.0.0:1024",
                   verbose=True,
                   validate=False)



if __name__ == '__main__':
    unittest.main()
