import pytest

from dsp_tools.commands.validate_data.models.rdf_like_data import PropertyObject
from dsp_tools.commands.validate_data.models.rdf_like_data import RdfLikeValue
from dsp_tools.commands.validate_data.models.rdf_like_data import TripleObjectType
from dsp_tools.commands.validate_data.models.rdf_like_data import TriplePropertyType
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType

LABEL_TRIPLE = PropertyObject(TriplePropertyType.RDFS_LABEL, "lbl", TripleObjectType.STRING)
TYPE_TRIPLE = PropertyObject(
    TriplePropertyType.RDF_TYPE, "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything", TripleObjectType.IRI
)

UNREIFIED_TRIPLE_OBJECTS = [LABEL_TRIPLE, TYPE_TRIPLE]


@pytest.fixture
def int_value_deserialised_corr() -> RdfLikeValue:
    return RdfLikeValue(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText",
        "1",
        KnoraValueType.INT_VALUE,
        [],
    )


@pytest.fixture
def interval_value_deserialised_corr() -> RdfLikeValue:
    seg_start = PropertyObject(TriplePropertyType.KNORA_INTERVAL_START, "1", TripleObjectType.DECIMAL)
    seg_end = PropertyObject(TriplePropertyType.KNORA_INTERVAL_END, "2", TripleObjectType.DECIMAL)
    return RdfLikeValue(
        user_facing_prop=f"{KNORA_API_STR}hasSegmentBounds",
        user_facing_value=None,
        knora_type=KnoraValueType.INTERVAL_VALUE,
        value_metadata=[seg_start, seg_end],
    )


@pytest.fixture
def link_value_deserialised_corr() -> RdfLikeValue:
    return RdfLikeValue(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo",
        "link-id",
        KnoraValueType.LINK_VALUE,
        [],
    )


@pytest.fixture
def link_value_deserialised_none() -> RdfLikeValue:
    return RdfLikeValue("http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo", None, KnoraValueType.LINK_VALUE, [])


@pytest.fixture
def list_value_deserialised_corr() -> RdfLikeValue:
    return RdfLikeValue("http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp", "n1", KnoraValueType.LIST_VALUE, [])


@pytest.fixture
def simple_text_deserialised_corr() -> RdfLikeValue:
    return RdfLikeValue(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea",
        "simple text",
        KnoraValueType.SIMPLETEXT_VALUE,
        [],
    )


@pytest.fixture
def richtext_deserialised_corr() -> RdfLikeValue:
    return RdfLikeValue(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext",
        "rich text",
        KnoraValueType.RICHTEXT_VALUE,
        [],
    )


@pytest.fixture
def time_value_deserialised_corr() -> RdfLikeValue:
    return RdfLikeValue(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue",
        "2019-10-23T13:45:12.01-14:00",
        KnoraValueType.TIME_VALUE,
        [],
    )


@pytest.fixture
def uri_value_deserialised_corr() -> RdfLikeValue:
    return RdfLikeValue(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue",
        "https://dasch.swiss",
        KnoraValueType.URI_VALUE,
        [],
    )
