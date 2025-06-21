# mypy: disable-error-code="method-assign,no-untyped-def"

from uuid import uuid4

import pytest
from rdflib import RDF
from rdflib import XSD
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedRichtext
from dsp_tools.commands.xmlupload.stash.stash_models import StandoffStashItem
from dsp_tools.commands.xmlupload.stash.upload_stashed_xml_texts import _make_richtext_update_graph
from dsp_tools.commands.xmlupload.stash.upload_stashed_xml_texts import _serialise_richtext_for_update
from dsp_tools.utils.rdflib_constants import KNORA_API

ONTO_STR = "http://0.0.0.0:3333/ontology/9999/onto/v2#"

ONTO = Namespace(ONTO_STR)

RES_IRI_STR = "http://rdfh.ch/9999/res_one"
RES_IRI = URIRef(RES_IRI_STR)
RES_TYPE = ONTO.Resource

PROP_IRI = ONTO.hasText
VAL_IRI_STR = "http://rdfh.ch/9999/res_one/values/richtext"
VAL_IRI = URIRef(VAL_IRI_STR)


@pytest.fixture
def standoff_stash_item() -> StandoffStashItem:
    val = ProcessedRichtext(
        value=FormattedTextValue("text"),
        prop_iri=str(PROP_IRI),
        resource_references=set(),
        value_uuid=str(uuid4()),
        comment=None,
        permissions=None,
    )
    return StandoffStashItem("res_one", str(RES_TYPE), val)


@pytest.fixture
def iri_resolver() -> IriResolver:
    return IriResolver({"res_one": RES_IRI_STR})


def test_make_richtext_update_graph(standoff_stash_item, iri_resolver):
    result = _make_richtext_update_graph(standoff_stash_item, VAL_IRI_STR, RES_IRI_STR, iri_resolver)
    assert len(result) == 5
    assert next(result.objects(RES_IRI, RDF.type)) == RES_TYPE
    assert next(result.objects(RES_IRI, PROP_IRI)) == VAL_IRI
    value = next(result.objects(VAL_IRI, KNORA_API.textValueAsXml))
    assert value == Literal('<?xml version="1.0" encoding="UTF-8"?>\n<text>text</text>', datatype=XSD.string)
    mapping = next(result.objects(VAL_IRI, KNORA_API.textValueHasMapping))
    assert mapping == URIRef("http://rdfh.ch/standoff/mappings/StandardMapping")
    assert next(result.objects(VAL_IRI, RDF.type)) == KNORA_API.TextValue


def test_serialise_richtext_for_update(standoff_stash_item, iri_resolver):
    result = _serialise_richtext_for_update(standoff_stash_item, VAL_IRI_STR, RES_IRI_STR, iri_resolver)
    expected = {
        "@id": "http://rdfh.ch/9999/res_one",
        "@type": "http://0.0.0.0:3333/ontology/9999/onto/v2#Resource",
        "http://0.0.0.0:3333/ontology/9999/onto/v2#hasText": {
            "@id": "http://rdfh.ch/9999/res_one/values/richtext",
            "@type": "http://api.knora.org/ontology/knora-api/v2#TextValue",
            "http://api.knora.org/ontology/knora-api/v2#textValueAsXml": {
                "@type": "http://www.w3.org/2001/XMLSchema#string",
                "@value": '<?xml version="1.0" encoding="UTF-8"?>\n<text>text</text>',
            },
            "http://api.knora.org/ontology/knora-api/v2#textValueHasMapping": {
                "@id": "http://rdfh.ch/standoff/mappings/StandardMapping"
            },
        },
    }
    assert result == expected


def test_find_ids_referenced_in_salsah_links_one_link() -> None:
    one_link_KnoraStandoffXml = FormattedTextValue(
        xmlstr=(
            '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="public">'
            '<text-prop name=":hasRichtext"><text permissions="public" encoding="xml">'
            '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
            "</text></text-prop></resource>"
        )
    )
    returned_set = one_link_KnoraStandoffXml.find_internal_ids()
    assert returned_set == {"r2_id"}


def test_find_ids_referenced_in_salsah_links_three_links() -> None:
    three_link_KnoraStandoffXml = FormattedTextValue(
        xmlstr=(
            '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="public">'
            '<text-prop name=":hasRichtext"><text permissions="public" encoding="xml">'
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
            '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="public">'
            '<text-prop name=":hasRichtext"><text permissions="public" encoding="xml">'
            '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
            "</text></text-prop></resource>"
        )
    )
    returned_instance = one_link_KnoraStandoffXml.with_iris(resolver)
    expected_str = (
        '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="public">'
        '<text-prop name=":hasRichtext"><text permissions="public" encoding="xml">'
        '<a class="salsah-link" href="r2_iri">r2_id</a>'
        "</text></text-prop></resource>"
    )
    assert returned_instance.xmlstr == expected_str


def test__replace_internal_ids_with_iris_three_links() -> None:
    resolver = IriResolver({"r1_id": "r1_iri", "r2_id": "r2_iri", "r3_id": "r3_iri"})
    three_link_KnoraStandoffXml = FormattedTextValue(
        xmlstr=(
            '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="public">'
            '<text-prop name=":hasRichtext"><text permissions="public" encoding="xml">'
            '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>This is normal text'
            '<a class="salsah-link" href="IRI:r3_id:IRI">r3_id</a>'
            '<a class="salsah-link" href="IRI:r2_id:IRI">r2_id</a>'
            "</text></text-prop></resource>"
        )
    )
    returned_instance = three_link_KnoraStandoffXml.with_iris(resolver)
    expected_str = (
        '<resource label="r1_label" restype="r1_restype" id="r1_id" permissions="public">'
        '<text-prop name=":hasRichtext"><text permissions="public" encoding="xml">'
        '<a class="salsah-link" href="r2_iri">r2_id</a>This is normal text'
        '<a class="salsah-link" href="r3_iri">r3_id</a>'
        '<a class="salsah-link" href="r2_iri">r2_id</a>'
        "</text></text-prop></resource>"
    )
    assert returned_instance.xmlstr == expected_str


if __name__ == "__main__":
    pytest.main([__file__])
