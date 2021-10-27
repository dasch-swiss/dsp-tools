"""Unit tests for id to iri mapping"""

import unittest
from lxml import etree

from knora.dsplib.utils.id_to_iri import id_to_iri


class TestTools(unittest.TestCase):
    def test_invalid_xml_file_name(self):
        with self.assertRaises(SystemExit) as cm:
            id_to_iri(xml_file='test.xml',
                      json_file='../testdata/test-id2iri-mapping.json',
                      out_file='_test-id2iri-replaced.xml',
                      verbose=True)

        self.assertEqual(cm.exception.code, 1)

    def test_invalid_json_file_name(self):
        with self.assertRaises(SystemExit) as cm:
            id_to_iri(xml_file='../testdata/test-id2iri-data.xml',
                      json_file='test.json',
                      out_file='_test-id2iri-replaced.xml',
                      verbose=True)

        self.assertEqual(cm.exception.code, 1)

    def test_replace_id_with_iri(self):
        out_file = '_test-id2iri-replaced.xml'
        id_to_iri(xml_file='../testdata/test-id2iri-data.xml',
                  json_file='../testdata/test-id2iri-mapping.json',
                  out_file=out_file,
                  verbose=True)

        tree = etree.parse(out_file)

        for elem in tree.getiterator():
            # skip comments and processing instructions as they do not have namespaces
            if not (
                isinstance(elem, etree._Comment)
                or isinstance(elem, etree._ProcessingInstruction)
            ):
                # remove namespace declarations
                elem.tag = etree.QName(elem).localname

        resource_elements = tree.xpath("/knora/resource/resptr-prop/resptr")
        result = []
        for resptr_prop in resource_elements:
            result.append(resptr_prop.text)

        self.assertEqual(result, ["http://rdfh.ch/082E/ylRvrg7tQI6aVpcTJbVrwg","http://rdfh.ch/082E/JK63OpYWTDWNYVOYFN7FdQ"])
