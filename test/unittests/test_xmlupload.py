"""Unit tests for xmlupload"""

import unittest
from lxml import etree

from knora.dsplib.models.helpers import BaseError
from knora.dsplib.utils.xml_upload import convert_ark_v0_to_resource_iri, remove_circular_references
from knora.dsplib.models.xmlresource import XMLResource


class TestXMLUpload(unittest.TestCase):

    def test_convert_ark_v0_to_resource_iri(self) -> None:
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


    def test_remove_circular_references(self) -> None:
        # create a list of XMLResources from the test data file
        tree = etree.parse('testdata/test-data.xml')
        for elem in tree.getiterator():
            if not (isinstance(elem, etree._Comment) or isinstance(elem, etree._ProcessingInstruction)):
                elem.tag = etree.QName(elem).localname  # remove namespace URI in the element's name
        etree.cleanup_namespaces(tree)  # remove unused namespace declarations
        resources = [XMLResource(x, 'testonto') for x in tree.getroot() if x.tag == "resource"]

        # get the purged resources and the stashes from the function to be tested
        resources, stashed_xml_texts_original, stashed_resptr_props_original = remove_circular_references(resources, False)

        # make a list of all hashes from the stashed xml texts
        stashed_xml_texts_hashes = list()
        for res, propdict in stashed_xml_texts_original.items():
            for elem in propdict.values():
                for hash, xml in elem.items():
                    stashed_xml_texts_hashes.append(hash)

        # make a version of the stashes with the IDs from the XML file instead of the Python objects
        stashed_xml_texts = {res.id: {prop.name: [str(x) for x in d.values()] for prop, d in _dict.items()}
                             for res, _dict in stashed_xml_texts_original.items()}
        stashed_resptr_props = {res.id: {prop.name: l for prop, l in _dict.items()}
                                for res, _dict in stashed_resptr_props_original.items()}

        # hardcode the expected values
        stashed_xml_texts_expected = {
            'obj_0001': {
                'testonto:hasRichtext': [
                    '\n                This is<em>bold and<strong>string</strong></em>text! It contains links to all '
                    'resources:\n'
                    '                <a class="salsah-link" href="IRI:obj_0000:IRI">obj_0000</a>\n'
                    '                <a class="salsah-link" href="IRI:obj_0001:IRI">obj_0001</a>\n'
                    '                <a class="salsah-link" href="IRI:obj_0002:IRI">obj_0002</a>\n'
                    '                <a class="salsah-link" href="IRI:obj_0003:IRI">obj_0003</a>\n'
                    '                <a class="salsah-link" href="IRI:obj_0004:IRI">obj_0004</a>\n'
                    '                <a class="salsah-link" href="IRI:obj_0005:IRI">obj_0005</a>\n'
                    '                <a class="salsah-link" href="IRI:obj_0006:IRI">obj_0006</a>\n'
                    '                <a class="salsah-link" href="IRI:obj_0007:IRI">obj_0007</a>\n'
                    '                <a class="salsah-link" href="IRI:obj_0008:IRI">obj_0008</a>\n'
                    '                <a class="salsah-link" href="IRI:obj_0009:IRI">obj_0009</a>\n'
                    '                <a class="salsah-link" href="IRI:obj_0010:IRI">obj_0010</a>\n'
                    '                <a class="salsah-link" href="IRI:obj_0011:IRI">obj_0011</a>\n'
                    '            \n            '
                ]
            },
            'obj_0011': {
                'testonto:hasRichtext': [
                     '\n                This is<em>bold and<strong>string</strong></em>text! It contains links to all '
                     'resources:\n'
                     '                <a class="salsah-link" href="IRI:obj_0000:IRI">obj_0000</a>\n'
                     '                <a class="salsah-link" href="IRI:obj_0001:IRI">obj_0001</a>\n'
                     '                <a class="salsah-link" href="IRI:obj_0002:IRI">obj_0002</a>\n'
                     '                <a class="salsah-link" href="IRI:obj_0003:IRI">obj_0003</a>\n'
                     '                <a class="salsah-link" href="IRI:obj_0004:IRI">obj_0004</a>\n'
                     '                <a class="salsah-link" href="IRI:obj_0005:IRI">obj_0005</a>\n'
                     '                <a class="salsah-link" href="IRI:obj_0006:IRI">obj_0006</a>\n'
                     '                <a class="salsah-link" href="IRI:obj_0007:IRI">obj_0007</a>\n'
                     '                <a class="salsah-link" href="IRI:obj_0008:IRI">obj_0008</a>\n'
                     '                <a class="salsah-link" href="IRI:obj_0009:IRI">obj_0009</a>\n'
                     '                <a class="salsah-link" href="IRI:obj_0010:IRI">obj_0010</a>\n'
                     '                <a class="salsah-link" href="IRI:obj_0011:IRI">obj_0011</a>\n'
                     '            \n            '
                ]
            }
        }
        stashed_resptr_props_expected = {'obj_0000': {'testonto:hasTestThing': ['obj_0001']}}

        # check if the stashes are equal to the expected stashes
        self.assertDictEqual(stashed_resptr_props, stashed_resptr_props_expected)
        self.assertDictEqual(stashed_xml_texts, stashed_xml_texts_expected)

        # check if the stashed hashes can also be found at the correct position in the purged resources
        for res, propdict in stashed_xml_texts_original.items():
            for prop, hashdict in propdict.items():
                stashed_hashes = list(hashdict.keys())
                purged_res = resources[resources.index(res)]
                purged_prop = purged_res.properties[purged_res.properties.index(prop)]
                purged_hashes = [str(val.value) for val in purged_prop.values if str(val.value) in stashed_xml_texts_hashes]
                self.assertListEqual(stashed_hashes, purged_hashes)


if __name__ == '__main__':
    unittest.main()
