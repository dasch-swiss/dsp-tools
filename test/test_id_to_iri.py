"""Unit tests for id to iri mapping"""

import unittest

from knora.dsplib.utils.id_to_iri import id_to_iri


class TestTools(unittest.TestCase):
    def setUp(self) -> None:
        """Is executed before each test"""
        print("hello")

    def test_invalid_xml_file_name(self):
        with self.assertRaises(SystemExit) as cm:
            id_to_iri(xml_file='test.xml', json_file='testdata/test-id2iri-mapping.json', out_file='_test-id2iri-replaced.xml', verbose=True)

        self.assertEqual(cm.exception.code, 1)

    def test_invalid_json_file_name(self):
        with self.assertRaises(SystemExit) as cm:
            id_to_iri(xml_file='testdata/test-id2iri-data.xml', json_file='test.json', out_file='_test-id2iri-replaced.xml', verbose=True)

        self.assertEqual(cm.exception.code, 1)
