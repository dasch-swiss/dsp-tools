# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access

from unittest import TestCase

import pytest

from dsp_tools.models.value import KnoraStandoffXml
from dsp_tools.utils.xmlupload import upload_stashed_xml_texts


class TestXMLUploadStash(TestCase):
    def test_find_ids_referenced_in_salsah_links_one_link(self) -> None:
        one_link_KnoraStandoffXml = KnoraStandoffXml(
            xmlstr=(
                '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
                '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
                "</text></text-prop></resource>"
            )
        )
        returned_set = one_link_KnoraStandoffXml.find_ids_referenced_in_salsah_links()
        self.assertEqual({"r2_id"}, returned_set)

    def test_find_ids_referenced_in_salsah_links_three_links(self) -> None:
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
        returned_set = three_link_KnoraStandoffXml.find_ids_referenced_in_salsah_links()
        self.assertEqual({"r2_id", "r3_id"}, returned_set)

    def test__replace_internal_ids_with_iris_one_link(self) -> None:
        test_id2iri = {"r1_id": "r1_iri", "r2_id": "r2_iri", "r3_id": "r3_iri"}
        one_link_KnoraStandoffXml = KnoraStandoffXml(
            xmlstr=(
                '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
                '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
                "</text></text-prop></resource>"
            )
        )
        returned_instance = upload_stashed_StandoffLink._replace_internal_ids_with_iris(
            id2iri_mapping=test_id2iri, xml_with_id=one_link_KnoraStandoffXml, id_set={"r2_id"}
        )
        expected_str = (
            '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
            '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
            '<a class="salsah-link" href="r2_iri">r2_id</a>'
            "</text></text-prop></resource>"
        )
        self.assertEqual(expected_str, str(returned_instance))

    def test__replace_internal_ids_with_iris_three_links(self) -> None:
        test_id2iri = {"r1_id": "r1_iri", "r2_id": "r2_iri", "r3_id": "r3_iri"}
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
        returned_instance = upload_stashed_StandoffLink._replace_internal_ids_with_iris(
            id2iri_mapping=test_id2iri, xml_with_id=three_link_KnoraStandoffXml, id_set={"r2_id", "r3_id"}
        )
        expected_str = (
            '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
            '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
            '<a class="salsah-link" href="r2_iri">r2_id</a>This is normal text'
            '<a class="salsah-link" href="r3_iri">r3_id</a>'
            '<a class="salsah-link" href="r2_iri">r2_id</a>'
            "</text></text-prop></resource>"
        )
        self.assertEqual(expected_str, str(returned_instance))


if __name__ == "__main__":
    pytest.main([__file__])
