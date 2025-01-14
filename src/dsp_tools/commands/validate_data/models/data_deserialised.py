from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto

from lxml import etree


@dataclass
class XMLProject:
    shortcode: str
    root: etree._Element
    used_ontologies: set[str]


@dataclass
class ProjectDeserialised:
    info: ProjectInformation
    data: DataDeserialised


@dataclass
class ProjectInformation:
    shortcode: str
    default_onto: str


@dataclass
class DataDeserialised:
    resources: list[ResourceDeserialised]
    file_values: list[AbstractFileValueDeserialised]


@dataclass
class ResourceDeserialised:
    """
    Represents a user facing project specific resource.

    Args:
        res_id: resource ID provided by the user in the XML
        property_objects: A list of properties and objects where the subject is the resource itself.
            They are non-reified triples (not values).
            For example, the label of a resource is here.
        values: a list of user-facing values (eg. BooleanValue)
    """

    res_id: str
    property_objects: list[PropertyObject]
    values: list[ValueDeserialised]


@dataclass
class PropertyObject:
    """
    Property and object of a triple.

    Args:
        property_type: maps to a specific knora-api or rdf(s) property
        object_value: object of the triple, may be user facing (eg. label) or metadata (eg. permissions)
        object_type: datatype for literals (eg. boolean) or that it is an IRI (not a literal)
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
        knora_type: Maps to a knora value type (eg. BooleanValue)
        value_metadata: metadata of the value for example permissions, comments, etc.
    """

    user_facing_prop: str
    user_facing_value: str | None
    knora_type: KnoraValueType
    value_metadata: list[PropertyObject]


class TriplePropertyType(Enum):
    """
    Maps to a specific knora-api or rdf(s) property.
    For example: comment -> knora-api:hasComment
    """

    rdfs_label = auto()
    rdf_type = auto()
    knora_permissions = auto()
    knora_comment = auto()


class TripleObjectType(Enum):
    """
    Maps to an xsd data type in case of literals, for example: boolean -> xsd:boolean
    Or Indicates that it is an IRI, in which case it is not an RDF Literal
    """

    boolean = auto()
    datetime = auto()
    decimal = auto()
    integer = auto()
    iri = auto()
    string = auto()
    uri = auto()


class KnoraValueType(Enum):
    BooleanValue = auto()
    ColorValue = auto()
    DateValue = auto()
    DecimalValue = auto()
    GeonameValue = auto()
    IntValue = auto()
    LinkValue = auto()
    ListValue = auto()
    SimpleTextValue = auto()
    RichtextValue = auto()
    TimeValue = auto()
    UriValue = auto()


@dataclass
class ValueDeserialised:
    prop_name: str
    object_value: str | None


@dataclass
class BooleanValueDeserialised(ValueDeserialised): ...


@dataclass
class ColorValueDeserialised(ValueDeserialised): ...


@dataclass
class DateValueDeserialised(ValueDeserialised): ...


@dataclass
class DecimalValueDeserialised(ValueDeserialised): ...


@dataclass
class GeonameValueDeserialised(ValueDeserialised): ...


@dataclass
class IntValueDeserialised(ValueDeserialised): ...


@dataclass
class LinkValueDeserialised(ValueDeserialised): ...


@dataclass
class ListValueDeserialised(ValueDeserialised):
    list_name: str


@dataclass
class SimpleTextDeserialised(ValueDeserialised): ...


@dataclass
class RichtextDeserialised(ValueDeserialised): ...


@dataclass
class TimeValueDeserialised(ValueDeserialised): ...


@dataclass
class UriValueDeserialised(ValueDeserialised): ...


@dataclass
class AbstractFileValueDeserialised:
    res_id: str
    value: str | None


@dataclass
class BitstreamDeserialised(AbstractFileValueDeserialised): ...


@dataclass
class IIIFUriDeserialised(AbstractFileValueDeserialised): ...
