# ruff: noqa: D101 (undocumented-public-class)
# ruff: noqa: D102 (undocumented-public-method)

from unittest import TestCase

import pytest

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.value import FormattedTextValue


class TestXMLUploadStash(TestCase):
    def test_find_ids_referenced_in_salsah_links_one_link(self) -> None:
        one_link_KnoraStandoffXml = FormattedTextValue(
            xmlstr=(
                '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
                '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
                "</text></text-prop></resource>"
            )
        )
        returned_set = one_link_KnoraStandoffXml.find_internal_ids()
        self.assertEqual({"r2_id"}, returned_set)

    def test_find_ids_referenced_in_salsah_links_three_links(self) -> None:
        three_link_KnoraStandoffXml = FormattedTextValue(
            xmlstr=(
                '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
                '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>This is normal text'
                '<a class="salsah-link" href="IRI:r3_id:IRI">r3_id</a>'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
                "</text></text-prop></resource>"
            )
        )
        returned_set = three_link_KnoraStandoffXml.find_internal_ids()
        self.assertEqual({"r2_id", "r3_id"}, returned_set)

    def test__replace_internal_ids_with_iris_one_link(self) -> None:
        resolver = IriResolver({"r1_id": "r1_iri", "r2_id": "r2_iri", "r3_id": "r3_iri"})
        one_link_KnoraStandoffXml = FormattedTextValue(
            xmlstr=(
                '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
                '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
                "</text></text-prop></resource>"
            )
        )
        returned_instance = one_link_KnoraStandoffXml.with_iris(resolver)
        expected_str = (
            '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
            '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
            '<a class="salsah-link" href="r2_iri">r2_id</a>'
            "</text></text-prop></resource>"
        )
        self.assertEqual(expected_str, returned_instance.xmlstr)

    def test__replace_internal_ids_with_iris_three_links(self) -> None:
        resolver = IriResolver({"r1_id": "r1_iri", "r2_id": "r2_iri", "r3_id": "r3_iri"})
        three_link_KnoraStandoffXml = FormattedTextValue(
            xmlstr=(
                '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
                '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>This is normal text'
                '<a class="salsah-link" href="IRI:r3_id:IRI">r3_id</a>'
                '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
                "</text></text-prop></resource>"
            )
        )
        returned_instance = three_link_KnoraStandoffXml.with_iris(resolver)
        expected_str = (
            '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="res-default">'
            '<text-prop name=":hasRichtext"><text permissions="res-default" encoding="xml">'
            '<a class="salsah-link" href="r2_iri">r2_id</a>This is normal text'
            '<a class="salsah-link" href="r3_iri">r3_id</a>'
            '<a class="salsah-link" href="r2_iri">r2_id</a>'
            "</text></text-prop></resource>"
        )
        self.assertEqual(expected_str, returned_instance.xmlstr)


if __name__ == "__main__":
    pytest.main([__file__])
