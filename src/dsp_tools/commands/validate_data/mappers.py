from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD

from dsp_tools.commands.validate_data.constants import ARCHIVE_FILE_VALUE
from dsp_tools.commands.validate_data.constants import AUDIO_FILE_VALUE
from dsp_tools.commands.validate_data.constants import DOCUMENT_FILE_VALUE
from dsp_tools.commands.validate_data.constants import IIIF_URI_VALUE
from dsp_tools.commands.validate_data.constants import MOVING_IMAGE_FILE_VALUE
from dsp_tools.commands.validate_data.constants import STILL_IMAGE_FILE_VALUE
from dsp_tools.commands.validate_data.constants import TEXT_FILE_VALUE
from dsp_tools.commands.validate_data.models.input_problems import ProblemType
from dsp_tools.commands.validate_data.models.rdf_like_data import TripleObjectType
from dsp_tools.commands.validate_data.models.rdf_like_data import TriplePropertyType
from dsp_tools.commands.validate_data.models.validation import ViolationType
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import BOOLEAN_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import COLOR_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import DECIMAL_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import GEOMETRY_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import GEONAME_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import INT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import RICHTEXT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import SIMPLE_TEXT_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import TIME_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.make_rdf_graph.constants import URI_PROP_TYPE_INFO
from dsp_tools.commands.xmlupload.models.rdf_models import RDFPropTypeInfo
from dsp_tools.utils.rdflib_constants import API_SHAPES
from dsp_tools.utils.rdflib_constants import KNORA_API
from dsp_tools.utils.rdflib_constants import KNORA_API_STR
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType

FILE_TYPE_TO_PROP = {
    KnoraValueType.ARCHIVE_FILE: f"{KNORA_API_STR}hasArchiveFileValue",
    KnoraValueType.AUDIO_FILE: f"{KNORA_API_STR}hasAudioFileValue",
    KnoraValueType.DOCUMENT_FILE: f"{KNORA_API_STR}hasDocumentFileValue",
    KnoraValueType.MOVING_IMAGE_FILE: f"{KNORA_API_STR}hasMovingImageFileValue",
    KnoraValueType.STILL_IMAGE_FILE: f"{KNORA_API_STR}hasStillImageFileValue",
    KnoraValueType.STILL_IMAGE_IIIF: f"{KNORA_API_STR}hasStillImageFileValue",
    KnoraValueType.TEXT_FILE: f"{KNORA_API_STR}hasTextFileValue",
}

# Mappers from internal representation to API format
XML_TAG_TO_VALUE_TYPE_MAPPER = {
    "boolean-prop": KnoraValueType.BOOLEAN_VALUE,
    "color-prop": KnoraValueType.COLOR_VALUE,
    "date-prop": KnoraValueType.DATE_VALUE,
    "decimal-prop": KnoraValueType.DECIMAL_VALUE,
    "geometry-prop": KnoraValueType.GEOM_VALUE,
    "geoname-prop": KnoraValueType.GEONAME_VALUE,
    "list-prop": KnoraValueType.LIST_VALUE,
    "integer-prop": KnoraValueType.INT_VALUE,
    "resptr-prop": KnoraValueType.LINK_VALUE,
    "time-prop": KnoraValueType.TIME_VALUE,
    "uri-prop": KnoraValueType.URI_VALUE,
}

TRIPLE_PROP_TYPE_TO_IRI_MAPPER = {
    TriplePropertyType.RDF_TYPE: RDF.type,
    TriplePropertyType.RDFS_LABEL: RDFS.label,
    TriplePropertyType.KNORA_COMMENT_ON_VALUE: KNORA_API.valueHasComment,
    TriplePropertyType.KNORA_PERMISSIONS: KNORA_API.hasPermissions,
    TriplePropertyType.KNORA_INTERVAL_START: KNORA_API.intervalValueHasStart,
    TriplePropertyType.KNORA_INTERVAL_END: KNORA_API.intervalValueHasEnd,
    TriplePropertyType.KNORA_STANDOFF_LINK: KNORA_API.hasStandoffLinkTo,
    TriplePropertyType.KNORA_LICENSE: KNORA_API.hasLicense,
    TriplePropertyType.KNORA_AUTHORSHIP: KNORA_API.hasAuthorship,
    TriplePropertyType.KNORA_COPYRIGHT_HOLDER: KNORA_API.hasCopyrightHolder,
    TriplePropertyType.KNORA_DATE_START: API_SHAPES.dateHasStart,
    TriplePropertyType.KNORA_DATE_END: API_SHAPES.dateHasEnd,
}

VALUE_INFO_TO_RDF_MAPPER = {
    KnoraValueType.BOOLEAN_VALUE: BOOLEAN_PROP_TYPE_INFO,
    KnoraValueType.COLOR_VALUE: COLOR_PROP_TYPE_INFO,
    KnoraValueType.DATE_VALUE: RDFPropTypeInfo(KNORA_API.DateValue, KNORA_API.valueAsString, XSD.string),
    KnoraValueType.DECIMAL_VALUE: DECIMAL_PROP_TYPE_INFO,
    KnoraValueType.GEONAME_VALUE: GEONAME_PROP_TYPE_INFO,
    KnoraValueType.GEOM_VALUE: GEOMETRY_PROP_TYPE_INFO,
    KnoraValueType.LIST_VALUE: RDFPropTypeInfo(KNORA_API.ListValue, KNORA_API.listValueAsListNode, XSD.string),
    KnoraValueType.LINK_VALUE: RDFPropTypeInfo(KNORA_API.LinkValue, API_SHAPES.linkValueHasTargetID, XSD.string),
    KnoraValueType.INT_VALUE: INT_PROP_TYPE_INFO,
    KnoraValueType.INTERVAL_VALUE: RDFPropTypeInfo(KNORA_API.IntervalValue, KNORA_API.hasSegmentBounds),
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
    KnoraValueType.GEOM_VALUE: TripleObjectType.STRING,
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
    TripleObjectType.DATE_YYYY_MM_DD: XSD.date,
}

# validation results

RESULT_TO_PROBLEM_MAPPER = {
    ViolationType.SEQNUM_IS_PART_OF: ProblemType.GENERIC,
    ViolationType.UNIQUE_VALUE: ProblemType.DUPLICATE_VALUE,
    ViolationType.VALUE_TYPE: ProblemType.VALUE_TYPE_MISMATCH,
    ViolationType.PATTERN: ProblemType.INPUT_REGEX,
    ViolationType.GENERIC: ProblemType.GENERIC,
    ViolationType.LINK_TARGET: ProblemType.LINK_TARGET_TYPE_MISMATCH,
    ViolationType.MAX_CARD: ProblemType.MAX_CARD,
    ViolationType.MIN_CARD: ProblemType.MIN_CARD,
    ViolationType.NON_EXISTING_CARD: ProblemType.NON_EXISTING_CARD,
    ViolationType.FILE_VALUE_PROHIBITED: ProblemType.FILE_VALUE_PROHIBITED,
    ViolationType.FILE_VALUE_MISSING: ProblemType.FILE_VALUE_MISSING,
}
