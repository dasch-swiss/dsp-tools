"""Unit tests for id to iri mapping"""

import unittest
import os
from dsp_tools.models.exceptions import BaseError

from dsp_tools.utils.xml_upload import _parse_xml_file
from dsp_tools.utils.id_to_iri import id_to_iri


class TestIdToIri(unittest.TestCase):
    out_file = 'testdata/tmp/_test-id2iri-replaced.xml'

    @classmethod
    def setUpClass(cls) -> None:
        """Is executed before the methods of this class are run"""
        os.makedirs('testdata/tmp', exist_ok=True)

    @classmethod
    def tearDownClass(cls) -> None:
        """Is executed after the methods of this class have all run through"""
        for file in os.listdir('testdata/tmp'):
            os.remove('testdata/tmp/' + file)
        os.rmdir('testdata/tmp')

    def test_invalid_xml_file_name(self) -> None:
        with self.assertRaisesRegex(BaseError, r"File test\.xml could not be found"):
            id_to_iri(xml_file='test.xml',
                      json_file='testdata/id2iri/test-id2iri-mapping.json',
                      out_file=self.out_file,
                      verbose=True)

    def test_invalid_json_file_name(self) -> None:
        with self.assertRaisesRegex(BaseError, r"File test\.json could not be found"):
            id_to_iri(xml_file='testdata/id2iri/test-id2iri-data.xml',
                      json_file='test.json',
                      out_file=self.out_file,
                      verbose=True)

    def test_replace_id_with_iri(self) -> None:
        id_to_iri(xml_file='testdata/id2iri/test-id2iri-data.xml',
                  json_file='testdata/id2iri/test-id2iri-mapping.json',
                  out_file=self.out_file,
                  verbose=True)

        root = _parse_xml_file(self.out_file)

        resource_elements = root.xpath("/knora/resource/resptr-prop/resptr")
        result = []
        for resptr_prop in resource_elements:
            result.append(resptr_prop.text)

        self.assertEqual(result,
                         ["http://rdfh.ch/082E/ylRvrg7tQI6aVpcTJbVrwg", "http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ"])


if __name__ == '__main__':
    unittest.main()
