"""Unit tests for ARK v0 conversion"""

import unittest

from knora.dsplib.models.helpers import BaseError
from knora.dsplib.utils.xml_upload import convert_ark_v0_to_resource_iri


class TestARKV02IRI(unittest.TestCase):

    def test_convert_ark_v0_to_resource_iri(self):
        ark = "ark:/72163/080c-779b9990a0c3f-6e"
        iri = convert_ark_v0_to_resource_iri(ark)
        self.assertEqual("http://rdfh.ch/080C/Ef9heHjPWDS7dMR_gGax2Q", iri)

        with self.assertRaises(BaseError) as err1:
            convert_ark_v0_to_resource_iri("ark:/72163/080c-779b999-0a0c3f-6e")
        self.assertEqual(err1.exception.message, "while converting ARK 'ark:/72163/080c-779b999-0a0c3f-6e'. The ARK seems to be invalid")

        with self.assertRaises(BaseError) as err2:
            convert_ark_v0_to_resource_iri("ark:/72163/080X-779b9990a0c3f-6e")
        self.assertEqual(err2.exception.message, "while converting ARK 'ark:/72163/080X-779b9990a0c3f-6e'. Invalid project shortcode '080X'")

        with self.assertRaises(BaseError) as err3:
            convert_ark_v0_to_resource_iri("ark:/72163/080c1-779b9990a0c3f-6e")
        self.assertEqual(err3.exception.message, "while converting ARK 'ark:/72163/080c1-779b9990a0c3f-6e'. Invalid project shortcode '080C1'")

        with self.assertRaises(BaseError) as err3:
            convert_ark_v0_to_resource_iri("ark:/72163/080c-779b99+90a0c3f-6e")
        self.assertEqual(err3.exception.message, "while converting ARK 'ark:/72163/080c-779b99+90a0c3f-6e'. Invalid Salsah ID '779b99+90a0c3f'")


if __name__ == '__main__':
    unittest.main()
