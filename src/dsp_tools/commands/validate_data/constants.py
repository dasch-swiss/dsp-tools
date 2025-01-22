from typing import TypeAlias
from typing import Union

from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD
from rdflib import Namespace
from rdflib.term import IdentifiedNode
from rdflib.term import Literal
from rdflib.term import Variable

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

# rdflib typing
PropertyTypeAlias: TypeAlias = Union[IdentifiedNode, Variable]
SubjectObjectTypeAlias: TypeAlias = Union[IdentifiedNode, Literal, Variable]

# Namespaces as string
KNORA_API_STR = "http://api.knora.org/ontology/knora-api/v2#"
API_SHAPES_STR = "http://api.knora.org/ontology/knora-api/shapes/v2#"

LINKOBJ_RESOURCE = KNORA_API_STR + "LinkObj"
VIDEO_SEGMENT_RESOURCE = KNORA_API_STR + "VideoSegment"
AUDIO_SEGMENT_RESOURCE = KNORA_API_STR + "AudioSegment"

# rdflib Namespaces
DASH = Namespace("http://datashapes.org/dash#")
KNORA_API = Namespace(KNORA_API_STR)
API_SHAPES = Namespace(API_SHAPES_STR)

DATA = Namespace("http://data/")


# Mapper from XML to internal representation

XML_ATTRIB_TO_PROP_TYPE_MAPPER = {
    "comment": TriplePropertyType.KNORA_COMMENT_ON_VALUE,
}

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
    TriplePropertyType.KNORA_COMMENT_ON_VALUE: KNORA_API.valueHasComment,
}


ARCHIVE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.ArchiveFileValue, KNORA_API.fileValueHasFilename, XSD.string)
AUDIO_FILE_VALUE = RDFPropTypeInfo(KNORA_API.AudioFileValue, KNORA_API.fileValueHasFilename, XSD.string)
DOCUMENT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.DocumentFileValue, KNORA_API.fileValueHasFilename, XSD.string)
MOVING_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.MovingImageFileValue, KNORA_API.fileValueHasFilename, XSD.string)
STILL_IMAGE_FILE_VALUE = RDFPropTypeInfo(KNORA_API.StillImageFileValue, KNORA_API.fileValueHasFilename, XSD.string)
TEXT_FILE_VALUE = RDFPropTypeInfo(KNORA_API.TextFileValue, KNORA_API.fileValueHasFilename, XSD.string)
IIIF_URI_VALUE = RDFPropTypeInfo(
    KNORA_API.StillImageExternalFileValue, KNORA_API.stillImageFileValueHasExternalUrl, XSD.anyURI
)


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
    KnoraValueType.ARCHIVE_FILE: ARCHIVE_FILE_VALUE,
    KnoraValueType.AUDIO_FILE: AUDIO_FILE_VALUE,
    KnoraValueType.DOCUMENT_FILE: DOCUMENT_FILE_VALUE,
    KnoraValueType.MOVING_IMAGE_FILE: MOVING_IMAGE_FILE_VALUE,
    KnoraValueType.STILL_IMAGE_FILE: STILL_IMAGE_FILE_VALUE,
    KnoraValueType.STILL_IMAGE_IIIF: IIIF_URI_VALUE,
    KnoraValueType.TEXT_FILE: TEXT_FILE_VALUE,
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
    KnoraValueType.ARCHIVE_FILE: TripleObjectType.STRING,
    KnoraValueType.AUDIO_FILE: TripleObjectType.STRING,
    KnoraValueType.DOCUMENT_FILE: TripleObjectType.STRING,
    KnoraValueType.MOVING_IMAGE_FILE: TripleObjectType.STRING,
    KnoraValueType.STILL_IMAGE_FILE: TripleObjectType.STRING,
    KnoraValueType.STILL_IMAGE_IIIF: TripleObjectType.URI,
    KnoraValueType.TEXT_FILE: TripleObjectType.STRING,
}

TRIPLE_OBJECT_TYPE_TO_XSD = {
    TripleObjectType.BOOLEAN: XSD.boolean,
    TripleObjectType.DATETIME: XSD.dateTimeStamp,
    TripleObjectType.DECIMAL: XSD.decimal,
    TripleObjectType.INTEGER: XSD.integer,
    TripleObjectType.STRING: XSD.string,
    TripleObjectType.URI: XSD.anyURI,
}
