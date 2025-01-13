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
        f"{KNORA_API_STR}BooleanValue", f"{KNORA_API_STR}booleanValueAsBoolean", DataTypes.boolean
    ),
    "color-prop": KnoraTypePropInfo(
        f"{KNORA_API_STR}ColorValue", f"{KNORA_API_STR}colorValueAsColor", DataTypes.string
    ),
    "date-prop": KnoraTypePropInfo(f"{KNORA_API_STR}DateValue", f"{KNORA_API_STR}valueAsString", DataTypes.string),
    "decimal-prop": KnoraTypePropInfo(
        f"{KNORA_API_STR}DecimalValue", f"{KNORA_API_STR}decimalValueAsDecimal", DataTypes.decimal
    ),
    "geoname-prop": KnoraTypePropInfo(
        f"{KNORA_API_STR}GeonameValue", f"{KNORA_API_STR}geonameValueAsGeonameCode", DataTypes.string
    ),
    "integer-prop": KnoraTypePropInfo(f"{KNORA_API_STR}IntValue", f"{KNORA_API_STR}intValueAsInt", DataTypes.integer),
    "resptr-prop": KnoraTypePropInfo(
        f"{KNORA_API_STR}LinkValue", f"{KNORA_API_STR}linkValueHasTargetIri", DataTypes.iri
    ),
    "time-prop": KnoraTypePropInfo(
        f"{KNORA_API_STR}TimeValue", f"{KNORA_API_STR}timeValueAsTimeStamp", DataTypes.datetime
    ),
    "uri-prop": KnoraTypePropInfo(f"{KNORA_API_STR}UriValue", f"{KNORA_API_STR}uriValueAsUri", DataTypes.uri),
}

# TODO: "text-prop", "list-prop"
