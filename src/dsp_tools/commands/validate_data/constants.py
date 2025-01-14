from rdflib import XSD
from rdflib import Namespace

from dsp_tools.commands.validate_data.models.data_deserialised import KnoraTypePropInfo
from dsp_tools.commands.validate_data.models.data_deserialised import ObjectTypes

# Namespaces as string
KNORA_API_STR = "http://api.knora.org/ontology/knora-api/v2#"
API_SHAPES_STR = "http://api.knora.org/ontology/knora-api/shapes/v2#"

# IRIs as string
RDF_TYPE_STR = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
RDFS_LABEL_STR = "http://www.w3.org/2000/01/rdf-schema#label"

REGION_RESOURCE = KNORA_API_STR + "Region"
LINKOBJ_RESOURCE = KNORA_API_STR + "LinkObj"
VIDEO_SEGMENT_RESOURCE = KNORA_API_STR + "VideoSegment"
AUDIO_SEGMENT_RESOURCE = KNORA_API_STR + "AudioSegment"

# rdflib Namespaces
DASH = Namespace("http://datashapes.org/dash#")
KNORA_API = Namespace(KNORA_API_STR)
API_SHAPES = Namespace(API_SHAPES_STR)

DATA = Namespace("http://data/")

# prop-type mapper info
BOOLEAN_PROP = KnoraTypePropInfo(
    knora_value_type=f"{KNORA_API_STR}BooleanValue",
    knora_prop=f"{KNORA_API_STR}booleanValueAsBoolean",
    object_type=ObjectTypes.boolean,
)
COLOR_PROP = KnoraTypePropInfo(
    knora_value_type=f"{KNORA_API_STR}ColorValue",
    knora_prop=f"{KNORA_API_STR}colorValueAsColor",
    object_type=ObjectTypes.string,
)
DATE_PROP = KnoraTypePropInfo(
    knora_value_type=f"{KNORA_API_STR}DateValue",
    knora_prop=f"{KNORA_API_STR}valueAsString",
    object_type=ObjectTypes.string,
)

DECIMAL_PROP = KnoraTypePropInfo(
    knora_value_type=f"{KNORA_API_STR}DecimalValue",
    knora_prop=f"{KNORA_API_STR}decimalValueAsDecimal",
    object_type=ObjectTypes.decimal,
)

GEONAME_PROP = KnoraTypePropInfo(
    knora_value_type=f"{KNORA_API_STR}GeonameValue",
    knora_prop=f"{KNORA_API_STR}geonameValueAsGeonameCode",
    object_type=ObjectTypes.string,
)
INTEGER_PROP = KnoraTypePropInfo(
    knora_value_type=f"{KNORA_API_STR}IntValue",
    knora_prop=f"{KNORA_API_STR}intValueAsInt",
    object_type=ObjectTypes.integer,
)

LINK_PROP = KnoraTypePropInfo(
    knora_value_type=f"{KNORA_API_STR}LinkValue",
    knora_prop=f"{API_SHAPES_STR}linkValueHasTargetID",
    object_type=ObjectTypes.iri,
)
TIME_PROP = KnoraTypePropInfo(
    knora_value_type=f"{KNORA_API_STR}TimeValue",
    knora_prop=f"{KNORA_API_STR}timeValueAsTimeStamp",
    object_type=ObjectTypes.datetime,
)
URI_PROP = KnoraTypePropInfo(
    knora_value_type=f"{KNORA_API_STR}UriValue",
    knora_prop=f"{KNORA_API_STR}uriValueAsUri",
    object_type=ObjectTypes.uri,
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
    knora_value_type=f"{KNORA_API_STR}ListValue",
    knora_prop=f"{API_SHAPES_STR}listNodeAsString",
    object_type=ObjectTypes.string,
)

SIMPLE_TEXT_PROP = KnoraTypePropInfo(
    knora_value_type=f"{KNORA_API_STR}TextValue",
    knora_prop=f"{KNORA_API_STR}valueAsString",
    object_type=ObjectTypes.string,
)
RICH_TEXT_PROP = KnoraTypePropInfo(
    knora_value_type=f"{KNORA_API_STR}TextValue",
    knora_prop=f"{KNORA_API_STR}textValueAsXml",
    object_type=ObjectTypes.string,
)


DATATYPES_TO_XSD = {
    ObjectTypes.boolean: XSD.boolean,
    ObjectTypes.datetime: XSD.dateTimeStamp,
    ObjectTypes.decimal: XSD.decimal,
    ObjectTypes.integer: XSD.integer,
    ObjectTypes.string: XSD.string,
    ObjectTypes.uri: XSD.anyURI,
}
