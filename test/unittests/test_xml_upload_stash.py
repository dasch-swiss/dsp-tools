# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

from unittest import TestCase

import pytest

from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.utils import xml_upload_stash


class TestXMLUploadStash(TestCase):
    def test_find_all_substring_in_xmlstr(self) -> None:
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
        for xml_string, expected_set in test_dict.items():
            returned = xml_string.find_all_iri_in_xmlstr()
            self.assertEqual(expected_set, returned)

    def test__replace_internal_ids_with_iris(self) -> None:
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
        for test_xml, (test_set, expected_str) in test_dict.items():
            returned_instance = xml_upload_stash._replace_internal_ids_with_iris(
                id2iri_mapping=test_id2iri, xml_with_id=test_xml, id_set=test_set
            )
            self.assertEqual(expected_str, str(returned_instance))


if __name__ == "__main__":
    pytest.main([__file__])
