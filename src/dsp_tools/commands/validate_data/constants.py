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


PROP_TYPE_MAPPER = {
    "boolean-prop": KnoraTypePropInfo(
        value_type=f"{KNORA_API_STR}BooleanValue",
        knora_prop=f"{KNORA_API_STR}booleanValueAsBoolean",
        data_type=DataTypes.boolean,
    ),
    "color-prop": KnoraTypePropInfo(
        value_type=f"{KNORA_API_STR}ColorValue",
        knora_prop=f"{KNORA_API_STR}colorValueAsColor",
        data_type=DataTypes.string,
    ),
    "date-prop": KnoraTypePropInfo(
        value_type=f"{KNORA_API_STR}DateValue",
        knora_prop=f"{KNORA_API_STR}valueAsString",
        data_type=DataTypes.string,
    ),
    "decimal-prop": KnoraTypePropInfo(
        value_type=f"{KNORA_API_STR}DecimalValue",
        knora_prop=f"{KNORA_API_STR}decimalValueAsDecimal",
        data_type=DataTypes.decimal,
    ),
    "geoname-prop": KnoraTypePropInfo(
        value_type=f"{KNORA_API_STR}GeonameValue",
        knora_prop=f"{KNORA_API_STR}geonameValueAsGeonameCode",
        data_type=DataTypes.string,
    ),
    "integer-prop": KnoraTypePropInfo(
        value_type=f"{KNORA_API_STR}IntValue",
        knora_prop=f"{KNORA_API_STR}intValueAsInt",
        data_type=DataTypes.integer,
    ),
    "resptr-prop": KnoraTypePropInfo(
        value_type=f"{KNORA_API_STR}LinkValue",
        knora_prop=f"{KNORA_API_STR}linkValueHasTargetIri",
        data_type=DataTypes.iri,
    ),
    "time-prop": KnoraTypePropInfo(
        value_type=f"{KNORA_API_STR}TimeValue",
        knora_prop=f"{KNORA_API_STR}timeValueAsTimeStamp",
        data_type=DataTypes.datetime,
    ),
    "uri-prop": KnoraTypePropInfo(
        value_type=f"{KNORA_API_STR}UriValue",
        knora_prop=f"{KNORA_API_STR}uriValueAsUri",
        data_type=DataTypes.uri,
    ),
}

# TODO: "text-prop", "list-prop"
