"""Unit tests for id to iri mapping"""

import unittest
import os

from knora.dsplib.utils.xml_upload import _parse_xml_file
from knora.dsplib.utils.id_to_iri import id_to_iri


class TestIdToIri(unittest.TestCase):
    out_file = 'testdata/tmp/_test-id2iri-replaced.xml'

    def setUp(self) -> None:
        """Is executed before each test"""
        os.makedirs('testdata/tmp', exist_ok=True)

    def test_invalid_xml_file_name(self) -> None:
        with self.assertRaises(SystemExit) as cm:
            id_to_iri(xml_file='test.xml',
                      json_file='testdata/test-id2iri-mapping.json',
                      out_file=self.out_file,
                      verbose=True)

        self.assertEqual(cm.exception.code, 1)

    def test_invalid_json_file_name(self) -> None:
        with self.assertRaises(SystemExit) as cm:
            id_to_iri(xml_file='testdata/test-id2iri-data.xml',
                      json_file='test.json',
                      out_file=self.out_file,
                      verbose=True)

        self.assertEqual(cm.exception.code, 1)

    def test_replace_id_with_iri(self) -> None:
        id_to_iri(xml_file='testdata/test-id2iri-data.xml',
                  json_file='testdata/test-id2iri-mapping.json',
                  out_file=self.out_file,
                  verbose=True)

        tree = _parse_xml_file(self.out_file)

        resource_elements = tree.xpath("/knora/resource/resptr-prop/resptr")
        result = []
        for resptr_prop in resource_elements:
            result.append(resptr_prop.text)

        self.assertEqual(result,
                         ["http://rdfh.ch/082E/ylRvrg7tQI6aVpcTJbVrwg", "http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ"])


if __name__ == '__main__':
    unittest.main()
