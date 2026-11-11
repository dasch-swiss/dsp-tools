from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC


# Design considerations
# - In any dataclass you only show fields that can or must be filled
# - It should not be possible to create an invalid class, for example a link property with a list name
# - Neither dsp-tools domain nor outdated knora language should be used
# - The names here should be more descriptive of their intent, for example no reference to gui ontology

class Language(Enum):
    EN = "en"
    DE = "de"
    FR = "fr"
    IT = "it"
    RM = "rm"


# This ensures that each language also has a comment not just a label
@dataclass(frozen=True)
class LabelComments:
    label: str
    comment: str
    language: Language

# Project creation, only done by system admin
@dataclass(frozen=True)
class Project:
    shortcode: str
    shortname: str
    longname: str
    descriptions: dict[str, str]
    keywords: list[str]
    embargo: bool = False


# Legal information, project admin
@dataclass(frozen=True)
class ProjectLegalSettings:
    enabled_licenses: list[str]
    data_license: str | None
    data_copyright_holder: str | None
    default_data_authorship: list[str]


# controlled vocabulary
@dataclass(frozen=True)
class ControlledVocabulary:
    vocabulary_name: str
    vocabulary_information: list[LabelComments]
    vocabulary_nodes: list[VocabularyNode]


@dataclass(frozen=True)
class VocabularyNode:
    node_name: str
    node_information: list[LabelComments]
    vocabulary_sub_nodes: list[VocabularyNode]

# one ontology
@dataclass(frozen=True)
class Ontology:
    name: str
    label: str
    comment: str | None
    classes: list[Class]
    properties: list[Property]


# This generic type will be knora-api:Resource
@dataclass(frozen=True)
class Class:
    class_information: list[LabelComments]
    ontology_super_classes: set[str]
    external_mapping: set[str]
    cardinalities: list[Cardinality]


# These are for all classes that are sub-class of knora-api:Representation
class DspFileTypes(Enum):
    ARCHIVE = auto()
    AUDIO = auto()
    DOCUMENT = auto()
    VIDEO = auto()
    STILL_IMAGE = auto()
    TEXT = auto()


class ClassWithFile(Class):
    file_type: DspFileTypes


class CardinalityNumber(Enum):
    C_0_1 = "0-1"
    C_1 = "1"
    C_0_N = "0-n"
    C_1_N = "1-n"


@dataclass(frozen=True)
class Cardinality:
    property: str
    cardinality: CardinalityNumber
    property_display_order: int | None # this is the gui-element

# The new schema does not refer to gui-element and type since that is not intuitive domain language and logic
# It is also not needed for dsp to understand which combination of knora-api super and gui-element is required

# these are literals in the RDF world
class DspDatatypePropertyTypes(Enum):
    BOOLEAN = auto()
    COLOR = auto()
    DATE = auto()
    DECIMAL = auto()
    GEOLOCATION = auto()
    GEONAME = auto()
    INT = auto()
    REGION_PREVIEW = auto()
    TEXT_ONE_LINE = auto()
    TEXT_MTULI_LINE = auto()
    TEXT_FORMATTED = auto()
    TIME = auto()
    URI = auto()
    HAS_COMMENT = auto()
    SEQNUM = auto()


# these are the supers that are links
class DspObjectPropertyTypes(DspDatatypePropertyTypes):
    LINK_TO_CLASS = auto()
    IS_PART_OF_COLLECTION = auto()
    HAS_REPRESENTATION = auto()


# This is not to be used directly because the three different types require other additional information
@dataclass(frozen=True)
class Property(ABC):
    label_comments: list[LabelComments]
    internal_super_properties: set[str] | None
    external_mapping: set[str] | None
    subject_class: str | None


class DatatypeProperty(Property):
    dsp_type: DspDatatypePropertyTypes


class ObjectProperty(Property):
    dsp_type: DspObjectPropertyTypes
    object_class: str


class ControlledVocabularyProperty(Property):
    vocabulary_name: str
