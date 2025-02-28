from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from enum import auto
from uuid import uuid4

from lxml import etree

from dsp_tools.models.datetimestamp import DateTimeStamp


@dataclass
class XMLProject:
    shortcode: str
    root: etree._Element
    used_ontologies: set[str]


@dataclass
class DataDeserialised:
    resources: list[ResourceDeserialised]


@dataclass
class ResourceDeserialised:
    """
    Represents a user facing project-specific resource.

    Args:
        res_id: resource ID provided by the user in the XML
        property_objects: A list of properties and objects where the subject is the resource itself.
            They are non-reified triples (not values).
            For example, the label of a resource is here.
        values: a list of user-facing values (e.g. BooleanValue)
        asset_value: an asset value (all FileValues excluding the IIIFUri)
        migration_metadata: Metadata used for salsah migration
    """

    res_id: str
    property_objects: list[PropertyObject]
    values: list[ValueInformation]
    asset_value: ValueInformation | None
    migration_metadata: MigrationMetadata


@dataclass
class MigrationMetadata:
    iri: str | None = None
    ark: str | None = None
    creation_date: DateTimeStamp | None = None

    def any(self) -> bool:
        return any([self.iri, self.ark, self.creation_date])


@dataclass
class PropertyObject:
    """
    Property and object of a triple.

    Args:
        property_type: maps to a specific knora-api or rdf(s) property
        object_value: object of the triple, may be user facing (e.g. label) or metadata (e.g. permissions)
        object_type: datatype for literals (e.g. boolean) or that it is an IRI (not a literal)
    """

    property_type: TriplePropertyType
    object_value: str | None
    object_type: TripleObjectType


@dataclass
class ValueInformation:
    """
    Contains information about a user-facing value, for example BooleanValue.

    Args:
        user_facing_prop: Absolute IRI of the property as defined in the ontology
        user_facing_value: User-facing value, for example a number
        knora_type: Maps to a knora value type (e.g. BooleanValue)
        value_metadata: metadata of the value for example permissions, comments, etc.
    """

    user_facing_prop: str
    user_facing_value: str | None
    knora_type: KnoraValueType
    value_metadata: list[PropertyObject]
    value_uuid: str = field(default_factory=lambda: str(uuid4()))


class TriplePropertyType(Enum):
    """
    Maps to a specific knora-api or rdf(s) property.
    For example: KNORA_COMMENT_ON_VALUE -> knora-api:valueHasComment
    """

    RDFS_LABEL = auto()
    RDF_TYPE = auto()
    KNORA_PERMISSIONS = auto()
    KNORA_COMMENT_ON_VALUE = auto()
    KNORA_INTERVAL_START = auto()
    KNORA_INTERVAL_END = auto()
    KNORA_STANDOFF_LINK = auto()
    KNORA_LICENSE = auto()
    KNORA_AUTHORSHIP = auto()
    KNORA_COPYRIGHT_HOLDER = auto()


class TripleObjectType(Enum):
    """
    Maps to an xsd data type in case of literals, for example: BOOLEAN -> xsd:boolean
    Or Indicates that it is an IRI, in which case it is not an RDF Literal
    """

    BOOLEAN = auto()
    DATETIME = auto()
    DECIMAL = auto()
    INTEGER = auto()
    IRI = auto()
    STRING = auto()
    URI = auto()


class KnoraValueType(Enum):
    """
    Maps to a knora value type, for example: BOOLEAN_VALUE -> knora-api:BooleanValue
    """

    BOOLEAN_VALUE = auto()
    COLOR_VALUE = auto()
    DATE_VALUE = auto()
    DECIMAL_VALUE = auto()
    GEONAME_VALUE = auto()
    GEOM_VALUE = auto()
    INT_VALUE = auto()
    INTERVAL_VALUE = auto()
    LINK_VALUE = auto()
    LIST_VALUE = auto()
    SIMPLETEXT_VALUE = auto()
    RICHTEXT_VALUE = auto()
    TIME_VALUE = auto()
    URI_VALUE = auto()

    ARCHIVE_FILE = auto()
    AUDIO_FILE = auto()
    DOCUMENT_FILE = auto()
    MOVING_IMAGE_FILE = auto()
    STILL_IMAGE_FILE = auto()
    STILL_IMAGE_IIIF = auto()
    TEXT_FILE = auto()
