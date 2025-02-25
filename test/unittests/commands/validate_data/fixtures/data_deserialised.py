import pytest

from dsp_tools.commands.validate_data.constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.models.data_deserialised import KnoraValueType
from dsp_tools.utils.xml_parsing.models.data_deserialised import MigrationMetadata
from dsp_tools.utils.xml_parsing.models.data_deserialised import PropertyObject
from dsp_tools.utils.xml_parsing.models.data_deserialised import ResourceDeserialised
from dsp_tools.utils.xml_parsing.models.data_deserialised import TripleObjectType
from dsp_tools.utils.xml_parsing.models.data_deserialised import TriplePropertyType
from dsp_tools.utils.xml_parsing.models.data_deserialised import ValueInformation

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
        asset_value=None,
        migration_metadata=MigrationMetadata(),
    )


@pytest.fixture
def resource_deserialised_no_values() -> ResourceDeserialised:
    return ResourceDeserialised(
        res_id="id",
        property_objects=UNREIFIED_TRIPLE_OBJECTS,
        values=[],
        asset_value=None,
        migration_metadata=MigrationMetadata(),
    )


@pytest.fixture
def resource_deserialised_with_asset() -> ResourceDeserialised:
    return ResourceDeserialised(
        res_id="id",
        property_objects=UNREIFIED_TRIPLE_OBJECTS,
        values=[],
        asset_value=ValueInformation(
            f"{KNORA_API_STR}hasAudioFileValue",
            "testdata/bitstreams/test.wav",
            KnoraValueType.AUDIO_FILE,
            [],
        ),
        migration_metadata=MigrationMetadata(),
    )


@pytest.fixture
def boolean_value_deserialised_corr() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean", "false", KnoraValueType.BOOLEAN_VALUE, []
    )


@pytest.fixture
def boolean_value_deserialised_zero() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean", "0", KnoraValueType.BOOLEAN_VALUE, []
    )


@pytest.fixture
def boolean_value_deserialised_one() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testBoolean", "1", KnoraValueType.BOOLEAN_VALUE, []
    )


@pytest.fixture
def color_value_deserialised_corr() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testColor", "#00ff00", KnoraValueType.COLOR_VALUE, []
    )


@pytest.fixture
def date_value_deserialised_corr() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testSubDate1",
        "JULIAN:BCE:0700:BCE:0600",
        KnoraValueType.DATE_VALUE,
        [],
    )


@pytest.fixture
def decimal_value_deserialised_corr() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testDecimalSimpleText",
        "1.2",
        KnoraValueType.DECIMAL_VALUE,
        [],
    )


@pytest.fixture
def geoname_value_deserialised_corr() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testGeoname",
        "1241345",
        KnoraValueType.GEONAME_VALUE,
        [],
    )


@pytest.fixture
def int_value_deserialised_corr() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testIntegerSimpleText",
        "1",
        KnoraValueType.INT_VALUE,
        [],
    )


@pytest.fixture
def interval_value_deserialised_corr() -> ValueInformation:
    seg_start = PropertyObject(TriplePropertyType.KNORA_INTERVAL_START, "1", TripleObjectType.DECIMAL)
    seg_end = PropertyObject(TriplePropertyType.KNORA_INTERVAL_END, "2", TripleObjectType.DECIMAL)
    return ValueInformation(
        user_facing_prop=f"{KNORA_API_STR}hasSegmentBounds",
        user_facing_value=None,
        knora_type=KnoraValueType.INTERVAL_VALUE,
        value_metadata=[seg_start, seg_end],
    )


@pytest.fixture
def link_value_deserialised_corr() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo",
        "link-id",
        KnoraValueType.LINK_VALUE,
        [],
    )


@pytest.fixture
def link_value_deserialised_none() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testHasLinkTo", None, KnoraValueType.LINK_VALUE, []
    )


@pytest.fixture
def list_value_deserialised_corr() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testListProp", "n1", KnoraValueType.LIST_VALUE, []
    )


@pytest.fixture
def simple_text_deserialised_corr() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testTextarea",
        "simple text",
        KnoraValueType.SIMPLETEXT_VALUE,
        [],
    )


@pytest.fixture
def richtext_deserialised_corr() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testRichtext",
        "rich text",
        KnoraValueType.RICHTEXT_VALUE,
        [],
    )


@pytest.fixture
def time_value_deserialised_corr() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testTimeValue",
        "2019-10-23T13:45:12.01-14:00",
        KnoraValueType.TIME_VALUE,
        [],
    )


@pytest.fixture
def uri_value_deserialised_corr() -> ValueInformation:
    return ValueInformation(
        "http://0.0.0.0:3333/ontology/9999/onto/v2#testUriValue",
        "https://dasch.swiss",
        KnoraValueType.URI_VALUE,
        [],
    )
