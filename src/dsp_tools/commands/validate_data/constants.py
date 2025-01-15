from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import Namespace

from dsp_tools.commands.validate_data.models.data_deserialised import KnoraValueType
from dsp_tools.commands.validate_data.models.data_deserialised import TripleObjectType
from dsp_tools.commands.validate_data.models.data_deserialised import TriplePropertyType
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import BOOLEAN_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import COLOR_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import DECIMAL_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import GEONAME_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import INT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import RICHTEXT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import SIMPLE_TEXT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import TIME_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import URI_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo

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


# Mapper from XML to internal representation

XML_TAG_TO_VALUE_TYPE_MAPPER = {
    "boolean-prop": KnoraValueType.BOOLEAN_VALUE,
    "color-prop": KnoraValueType.COLOR_VALUE,
    "date-prop": KnoraValueType.DATE_VALUE,
    "decimal-prop": KnoraValueType.DECIMAL_VALUE,
    "geoname-prop": KnoraValueType.GEONAME_VALUE,
    "list-prop": KnoraValueType.LIST_VALUE,
    "integer-prop": KnoraValueType.INT_VALUE,
    "resptr-prop": KnoraValueType.LINK_VALUE,
    "time-prop": KnoraValueType.TIME_VALUE,
    "uri-prop": KnoraValueType.URI_VALUE,
}


# Mappers from internal representation to API format

TRIPLE_PROP_TYPE_TO_IRI_MAPPER = {
    TriplePropertyType.RDF_TYPE: RDF.type,
    TriplePropertyType.RDFS_LABEL: RDFS.label,
}

VALUE_INFO_TO_RDF_MAPPER = {
    KnoraValueType.BOOLEAN_VALUE: BOOLEAN_PROP_TYPE_INFO,
    KnoraValueType.COLOR_VALUE: COLOR_PROP_TYPE_INFO,
    KnoraValueType.DATE_VALUE: RDFPropTypeInfo(KNORA_API.DateValue, KNORA_API.valueAsString, XSD.string),
    KnoraValueType.DECIMAL_VALUE: DECIMAL_PROP_TYPE_INFO,
    KnoraValueType.GEONAME_VALUE: GEONAME_PROP_TYPE_INFO,
    KnoraValueType.LIST_VALUE: RDFPropTypeInfo(KNORA_API.ListValue, API_SHAPES.listNodeAsString, XSD.string),
    KnoraValueType.LINK_VALUE: RDFPropTypeInfo(KNORA_API.LinkValue, API_SHAPES.linkValueHasTargetID, XSD.string),
    KnoraValueType.INT_VALUE: INT_PROP_TYPE_INFO,
    KnoraValueType.SIMPLETEXT_VALUE: SIMPLE_TEXT_PROP_TYPE_INFO,
    KnoraValueType.RICHTEXT_VALUE: RICHTEXT_PROP_TYPE_INFO,
    KnoraValueType.TIME_VALUE: TIME_PROP_TYPE_INFO,
    KnoraValueType.URI_VALUE: URI_PROP_TYPE_INFO,
}

VALUE_INFO_TRIPLE_OBJECT_TYPE = {
    KnoraValueType.BOOLEAN_VALUE: TripleObjectType.BOOLEAN,
    KnoraValueType.COLOR_VALUE: TripleObjectType.STRING,
    KnoraValueType.DATE_VALUE: TripleObjectType.STRING,
    KnoraValueType.DECIMAL_VALUE: TripleObjectType.DECIMAL,
    KnoraValueType.GEONAME_VALUE: TripleObjectType.STRING,
    KnoraValueType.LIST_VALUE: TripleObjectType.STRING,
    KnoraValueType.LINK_VALUE: TripleObjectType.IRI,
    KnoraValueType.INT_VALUE: TripleObjectType.INTEGER,
    KnoraValueType.SIMPLETEXT_VALUE: TripleObjectType.STRING,
    KnoraValueType.RICHTEXT_VALUE: TripleObjectType.STRING,
    KnoraValueType.TIME_VALUE: TripleObjectType.DATETIME,
    KnoraValueType.URI_VALUE: TripleObjectType.URI,
}

TRIPLE_OBJECT_TYPE_TO_XSD = {
    TripleObjectType.BOOLEAN: XSD.boolean,
    TripleObjectType.DATETIME: XSD.dateTimeStamp,
    TripleObjectType.DECIMAL: XSD.decimal,
    TripleObjectType.INTEGER: XSD.integer,
    TripleObjectType.STRING: XSD.string,
    TripleObjectType.URI: XSD.anyURI,
}
