# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

from unittest import TestCase

import pytest

import dsp_tools.utils.xml_upload_stash as upld
from dsp_tools.models.value import KnoraStandoffXml


class TestXMLUploadStash(TestCase):
    def test_find_all_substring_in_xmlstr(self):
        one_link_KnoraStandoffXml = KnoraStandoffXml(
            xmlstr=(
                '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
                '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
                "</text></text-prop></resource>"
            )
        )
        three_link_KnoraStandoffXml = KnoraStandoffXml(
            xmlstr=(
                '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
                '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>This is normal text'
                '<a class="salsah-link" href="IRI:r3_id:IRI">r3_id</a>'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
                "</text></text-prop></resource>"
            )
        )
        test_dict = {
            one_link_KnoraStandoffXml: {"r2_id"},
            three_link_KnoraStandoffXml: {"r2_id", "r3_id"},
        }
        for test_instance, expected in test_dict.items():
            returned = test_instance.find_all_substring_in_xmlstr(pattern='href="IRI:(.*?):IRI"')
            self.assertEqual(expected, returned)

    def test__replace_internal_ids_with_iris(self):
        test_id2iri = {"r1_id": "r1_iri", "r2_id": "r2_iri", "r3_id": "r3_iri"}
        one_link_KnoraStandoffXml = KnoraStandoffXml(
            xmlstr=(
                '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
                '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
                "</text></text-prop></resource>"
            )
        )
        three_link_KnoraStandoffXml = KnoraStandoffXml(
            xmlstr=(
                '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
                '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>This is normal text'
                '<a class="salsah-link" href="IRI:r3_id:IRI">r3_id</a>'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
                "</text></text-prop></resource>"
            )
        )
        test_dict = {
            one_link_KnoraStandoffXml: (
                {"r2_id"},
                (
                    '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
                    '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
                    '<a class="salsah-link" href="r2_iri">r2_id</a>'
                    "</text></text-prop></resource>"
                ),
            ),
            three_link_KnoraStandoffXml: (
                {"r2_id", "r3_id"},
                (
                    '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
                    '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
                    '<a class="salsah-link" href="r2_iri">r2_id</a>This is normal text'
                    '<a class="salsah-link" href="r3_iri">r3_id</a>'
                    '<a class="salsah-link" href="r2_iri">r2_id</a>'
                    "</text></text-prop></resource>"
                ),
            ),
        }
        for test_instance, (test_set, expected) in test_dict.items():
            returned_instance = upld._replace_internal_ids_with_iris(
                id2iri_mapping=test_id2iri, xml_with_id=test_instance, id_set=test_set
            )
            self.assertEqual(expected, str(returned_instance))


if __name__ == "__main__":
    pytest.main([__file__])
