import pytest

from dsp_tools.commands.validate_data.models.data_deserialised import PropertyObject
from dsp_tools.commands.validate_data.models.data_deserialised import ResourceDeserialised
from dsp_tools.commands.validate_data.models.data_deserialised import TripleObjectType
from dsp_tools.commands.validate_data.models.data_deserialised import TriplePropertyType
from dsp_tools.commands.validate_data.models.data_deserialised import ValueInformation

LABEL_TRIPLE = PropertyObject(TriplePropertyType.RDFS_LABEL, "lbl", TripleObjectType.STRING)
TYPE_TRIPLE = PropertyObject(
    TriplePropertyType.RDF_TYPE, "http://0.0.0.0:3333/ontology/9999/onto/v2#ClassWithEverything", TripleObjectType.IRI
)

UNREIFIED_TRIPLE_OBJECTS = [LABEL_TRIPLE, TYPE_TRIPLE]


@pytest.fixture
def resource_deserialised_with_values(
    boolean_value_deserialised_corr: ValueInformation,
) -> ResourceDeserialised:
    return ResourceDeserialised(
        res_id="id",
        property_objects=UNREIFIED_TRIPLE_OBJECTS,
        values=[boolean_value_deserialised_corr],
    )


@pytest.fixture
def resource_deserialised_no_values() -> ResourceDeserialised:
    return ResourceDeserialised(
        res_id="id",
        property_objects=UNREIFIED_TRIPLE_OBJECTS,
        values=[],
    )


@pytest.fixture
def boolean_value_deserialised_corr() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean", "false")


@pytest.fixture
def boolean_value_deserialised_zero() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean", "0")


@pytest.fixture
def boolean_value_deserialised_one() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean", "1")


@pytest.fixture
def boolean_value_deserialised_none() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean", None)


@pytest.fixture
def color_value_deserialised_corr() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testColor", "#00ff00")


@pytest.fixture
def color_value_deserialised_none() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testColor", None)


@pytest.fixture
def date_value_deserialised_corr() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1", "JULIAN:BCE:0700:BCE:0600")


@pytest.fixture
def date_value_deserialised_none() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1", None)


@pytest.fixture
def decimal_value_deserialised_corr() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText", "1.2")


@pytest.fixture
def decimal_value_deserialised_none() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText", None)


@pytest.fixture
def geoname_value_deserialised_corr() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname", "1241345")


@pytest.fixture
def geoname_value_deserialised_none() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname", None)


@pytest.fixture
def int_value_deserialised_corr() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText", "1")


@pytest.fixture
def int_value_deserialised_none() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText", None)


@pytest.fixture
def link_value_deserialised_corr() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo", "link-id")


@pytest.fixture
def link_value_deserialised_none() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo", None)


@pytest.fixture
def list_value_deserialised_corr() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp", "n1", "firstList")


@pytest.fixture
def list_value_deserialised_none() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp", None, "firstList")


@pytest.fixture
def simple_text_deserialised_corr() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea", "simple text")


@pytest.fixture
def simple_text_deserialised_none() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea", None)


@pytest.fixture
def richtext_deserialised_corr() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext", "rich text")


@pytest.fixture
def richtext_deserialised_none() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext", None)


@pytest.fixture
def time_value_deserialised_corr() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue", "2019-10-23T13:45:12.01-14:00")


@pytest.fixture
def time_value_deserialised_none() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue", None)


@pytest.fixture
def uri_value_deserialised_corr() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue", "https://dasch.swiss")


@pytest.fixture
def uri_value_deserialised_none() -> ValueInformation:
    return ValueInformation("http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue", None)
