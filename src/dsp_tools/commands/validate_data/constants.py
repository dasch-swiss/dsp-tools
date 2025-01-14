from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import Namespace

from dsp_tools.commands.validate_data.models.data_deserialised import KnoraValueType
from dsp_tools.commands.validate_data.models.data_deserialised import TripleObjectType
from dsp_tools.commands.validate_data.models.data_deserialised import TriplePropertyType

# Namespaces as string
KNORA_API_STR = "http://api.knora.org/ontology/knora-api/v2#"
API_SHAPES_STR = "http://api.knora.org/ontology/knora-api/shapes/v2#"

REGION_RESOURCE = KNORA_API_STR + "Region"
LINKOBJ_RESOURCE = KNORA_API_STR + "LinkObj"
VIDEO_SEGMENT_RESOURCE = KNORA_API_STR + "VideoSegment"
AUDIO_SEGMENT_RESOURCE = KNORA_API_STR + "AudioSegment"

# rdflib Namespaces
DASH = Namespace("http://datashapes.org/dash#")
KNORA_API = Namespace(KNORA_API_STR)
API_SHAPES = Namespace(API_SHAPES_STR)

DATA = Namespace("http://data/")

TRIPLE_PROP_TYPE_TO_IRI_MAPPER = {
    TriplePropertyType.RDF_TYPE: RDF.type,
    TriplePropertyType.RDFS_LABEL: RDFS.label,
}

XML_TAG_TO_VALUE_TYPE_MAPPER = {
    "boolean-prop": KnoraValueType.BOOLEAN_VALUE,
    "color-prop": KnoraValueType.COLOR_VALUE,
    "date-prop": KnoraValueType.DATE_VALUE,
    "decimal-prop": KnoraValueType.DECIMAL_VALUE,
    "geoname-prop": KnoraValueType.GEONAME_VALUE,
    "integer-prop": KnoraValueType.INT_VALUE,
    "resptr-prop": KnoraValueType.LINK_VALUE,
    "time-prop": KnoraValueType.TIME_VALUE,
    "uri-prop": KnoraValueType.URI_VALUE,
}

TRIPLE_OBJECT_TYPE_TO_XSD = {
    TripleObjectType.BOOLEAN: XSD.boolean,
    TripleObjectType.DATETIME: XSD.dateTimeStamp,
    TripleObjectType.DECIMAL: XSD.decimal,
    TripleObjectType.INTEGER: XSD.integer,
    TripleObjectType.STRING: XSD.string,
    TripleObjectType.URI: XSD.anyURI,
}
