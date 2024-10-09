import pytest

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue


def test_find_ids_referenced_in_salsah_links_one_link() -> None:
    one_link_KnoraStandoffXml = FormattedTextValue(
        xmlstr=(
            '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="open">'
            '<text-prop name=":hasRichtext"><text permissions="open" encoding="xml">'
            '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
            "</text></text-prop></resource>"
        )
    )
    returned_set = one_link_KnoraStandoffXml.find_internal_ids()
    assert returned_set == {"r2_id"}


def test_find_ids_referenced_in_salsah_links_three_links() -> None:
    three_link_KnoraStandoffXml = FormattedTextValue(
        xmlstr=(
            '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="open">'
            '<text-prop name=":hasRichtext"><text permissions="open" encoding="xml">'
            '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>This is normal text'
            '<a class="salsah-link" href="IRI:r3_id:IRI">r3_id</a>'
            '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
            "</text></text-prop></resource>"
        )
    )
    returned_set = three_link_KnoraStandoffXml.find_internal_ids()
    assert returned_set == {"r2_id", "r3_id"}


def test__replace_internal_ids_with_iris_one_link() -> None:
    resolver = IriResolver({"r1_id": "r1_iri", "r2_id": "r2_iri", "r3_id": "r3_iri"})
    one_link_KnoraStandoffXml = FormattedTextValue(
        xmlstr=(
            '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="open">'
            '<text-prop name=":hasRichtext"><text permissions="open" encoding="xml">'
            '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
            "</text></text-prop></resource>"
        )
    )
    returned_instance = one_link_KnoraStandoffXml.with_iris(resolver)
    expected_str = (
        '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="open">'
        '<text-prop name=":hasRichtext"><text permissions="open" encoding="xml">'
        '<a class="salsah-link" href="r2_iri">r2_id</a>'
        "</text></text-prop></resource>"
    )
    assert returned_instance.xmlstr == expected_str


def test__replace_internal_ids_with_iris_three_links() -> None:
    resolver = IriResolver({"r1_id": "r1_iri", "r2_id": "r2_iri", "r3_id": "r3_iri"})
    three_link_KnoraStandoffXml = FormattedTextValue(
        xmlstr=(
            '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="open">'
            '<text-prop name=":hasRichtext"><text permissions="open" encoding="xml">'
            '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>This is normal text'
            '<a class="salsah-link" href="IRI:r3_id:IRI">r3_id</a>'
            '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
            "</text></text-prop></resource>"
        )
    )
    returned_instance = three_link_KnoraStandoffXml.with_iris(resolver)
    expected_str = (
        '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="open">'
        '<text-prop name=":hasRichtext"><text permissions="open" encoding="xml">'
        '<a class="salsah-link" href="r2_iri">r2_id</a>This is normal text'
        '<a class="salsah-link" href="r3_iri">r3_id</a>'
        '<a class="salsah-link" href="r2_iri">r2_id</a>'
        "</text></text-prop></resource>"
    )
    assert returned_instance.xmlstr == expected_str


if __name__ == "__main__":
    pytest.main([__file__])
