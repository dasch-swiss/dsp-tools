from rdflib import Namespace

from dsp_tools.commands.validate_data.models.data_deserialised import DataTypes
from dsp_tools.commands.validate_data.models.data_deserialised import KnoraTypePropInfo

KNORA_API_STR = "http://api.knora.org/ontology/knora-api/v2#"
REGION_RESOURCE = KNORA_API_STR + "Region"
LINKOBJ_RESOURCE = KNORA_API_STR + "LinkObj"
VIDEO_SEGMENT_RESOURCE = KNORA_API_STR + "VideoSegment"
AUDIO_SEGMENT_RESOURCE = KNORA_API_STR + "AudioSegment"


DASH = Namespace("http://datashapes.org/dash#")

KNORA_API = Namespace(KNORA_API_STR)
API_SHAPES = Namespace("http://api.knora.org/ontology/knora-api/shapes/v2#")

DATA = Namespace("http://data/")

BOOLEAN_PROP = KnoraTypePropInfo(
    value_type=f"{KNORA_API_STR}BooleanValue",
    knora_prop=f"{KNORA_API_STR}booleanValueAsBoolean",
    data_type=DataTypes.boolean,
)
COLOR_PROP = KnoraTypePropInfo(
    value_type=f"{KNORA_API_STR}ColorValue",
    knora_prop=f"{KNORA_API_STR}colorValueAsColor",
    data_type=DataTypes.string,
)
DATE_PROP = KnoraTypePropInfo(
    value_type=f"{KNORA_API_STR}DateValue",
    knora_prop=f"{KNORA_API_STR}valueAsString",
    data_type=DataTypes.string,
)

DECIMAL_PROP = KnoraTypePropInfo(
    value_type=f"{KNORA_API_STR}DecimalValue",
    knora_prop=f"{KNORA_API_STR}decimalValueAsDecimal",
    data_type=DataTypes.decimal,
)

GEONAME_PROP = KnoraTypePropInfo(
    value_type=f"{KNORA_API_STR}GeonameValue",
    knora_prop=f"{KNORA_API_STR}geonameValueAsGeonameCode",
    data_type=DataTypes.string,
)
INTEGER_PROP = KnoraTypePropInfo(
    value_type=f"{KNORA_API_STR}IntValue",
    knora_prop=f"{KNORA_API_STR}intValueAsInt",
    data_type=DataTypes.integer,
)

LINK_PROP = KnoraTypePropInfo(
    value_type=f"{KNORA_API_STR}LinkValue",
    knora_prop=f"{KNORA_API_STR}linkValueHasTargetIri",  # TODO: change to the shacl one
    data_type=DataTypes.iri,
)
TIME_PROP = KnoraTypePropInfo(
    value_type=f"{KNORA_API_STR}TimeValue",
    knora_prop=f"{KNORA_API_STR}timeValueAsTimeStamp",
    data_type=DataTypes.datetime,
)
URI_PROP = KnoraTypePropInfo(
    value_type=f"{KNORA_API_STR}UriValue",
    knora_prop=f"{KNORA_API_STR}uriValueAsUri",
    data_type=DataTypes.uri,
)

PROP_TYPE_MAPPER = {
    "boolean-prop": BOOLEAN_PROP,
    "color-prop": COLOR_PROP,
    "date-prop": DATE_PROP,
    "decimal-prop": DECIMAL_PROP,
    "geoname-prop": GEONAME_PROP,
    "integer-prop": INTEGER_PROP,
    "resptr-prop": LINK_PROP,
    "time-prop": TIME_PROP,
    "uri-prop": URI_PROP,
}


LIST_PROP = KnoraTypePropInfo(
    value_type=f"{KNORA_API_STR}ListValue",
    knora_prop=f"{KNORA_API_STR}valueAsString",  # TODO: need to change to other prop
    data_type=DataTypes.string,
)

SIMPLE_TEXT_PROP = KnoraTypePropInfo(
    value_type=f"{KNORA_API_STR}TextValue",
    knora_prop=f"{KNORA_API_STR}valueAsString",
    data_type=DataTypes.string,
)
RICH_TEXT_PROP = KnoraTypePropInfo(
    value_type=f"{KNORA_API_STR}TextValue",
    knora_prop=f"{KNORA_API_STR}textValueAsXml",
    data_type=DataTypes.string,
)
