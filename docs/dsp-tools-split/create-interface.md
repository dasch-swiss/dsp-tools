---
status: proposed
date: 2026-11-11
---

# Interface of `create` in `dsp-vre`

## Summary

This document proposes the input dataclasses for the `create` operation in `dsp-vre`.
For each dataclass, it gives the intent, the code and the related keys of the JSON project file.
The principles come from [ADR-dsp-vre.md](ADR-dsp-vre.md).
The steps of `create` are in [dsp-vre-to-tools-map.md](dsp-vre-to-tools-map.md).
The code is also in [create_classes.py](create_classes.py).

## Design Rules

The dataclasses follow these rules:

1. A dataclass shows only fields that the user can or must fill.
2. It is not possible to create an invalid object, for example a link property with a list name.
3. The names do not use `dsp-tools` terms or old `knora` terms.
4. The names describe the intent, for example they do not refer to the GUI ontology.

All dataclasses are frozen.

## Scope

Groups, users and permissions are not in this document. A later document describes them.

## Language, Label and Comment

`Language` is the closed set of languages that DSP supports.

`LabelComments` holds the label and the comment for one language.
The intent is that each language has a label and a comment.
A label without a comment is not possible.

Classes, properties and vocabulary nodes use a `list[LabelComments]`, with one item for each language.

```python
class Language(Enum):
    EN = "en"
    DE = "de"
    FR = "fr"
    IT = "it"
    RM = "rm"


@dataclass(frozen=True)
class LabelComments:
    label: str
    comment: str
    language: Language
```

| JSON project file                                                 | Proposed field                                |
|-------------------------------------------------------------------|-----------------------------------------------|
| `labels: {"en": "..."}` and `comments: {"en": "..."}` (two dicts) | `list[LabelComments]` (one item per language) |
| Language code as a free string                                    | `Language`                                    |

## Project and Legal Information

### Project

A system admin creates the project.
`Project` holds the identity and the description of the project.
`embargo` sets the embargo state at creation. The default is no embargo.

```python
@dataclass(frozen=True)
class Project:
    shortcode: str
    shortname: str
    longname: str
    descriptions: dict[Language, str]
    keywords: list[str]
    embargo: bool = False
```

### Legal Information

A project admin sets the legal information.
`ProjectLegalSettings` is separate from `Project`, because a different role owns it.

```python
@dataclass(frozen=True)
class ProjectLegalSettings:
    enabled_licenses: list[str]
    data_license: str | None
    data_copyright_holder: str | None
    default_data_authorship: list[str]
```

| JSON project file (`project`)                                                          | Proposed field                              |
|----------------------------------------------------------------------------------------|---------------------------------------------|
| `shortcode`, `shortname`, `longname`, `keywords`                                       | `Project`: same names                       |
| `descriptions: {"en": "..."}`                                                          | `Project.descriptions: dict[Language, str]` |
| Not available                                                                          | `Project.embargo`                           |
| `enabled_licenses`, `data_license`, `data_copyright_holder`, `default_data_authorship` | `ProjectLegalSettings`: same names          |

## Ontology

### Data Model

`Ontology` holds the classes and the properties of one data model.
The label is one string and the comment is optional. They do not have a language.

```python
@dataclass(frozen=True)
class Ontology:
    name: str
    label: str
    comment: str | None
    classes: list[Class]
    properties: list[Property]
```

### Class

`Class` is a class without a file. On the server, it is a sub-class of `knora-api:Resource`.

The intent is to separate two kinds of super-classes:

- `ontology_super_classes`: classes of the same project. They give inheritance.
- `external_mapping`: classes of external ontologies, for example CIDOC CRM. They give meaning only.

```python
@dataclass(frozen=True)
class Class:
    name: str
    class_information: list[LabelComments]
    ontology_super_classes: set[str]
    external_mapping: set[str]
    cardinalities: list[Cardinality]
```

### Class with File

`ClassWithFile` is a class that has a file. On the server, it is a sub-class of `knora-api:Representation`.
The user selects the file type. The user does not select the `knora-api` super-class.

```python
class DspFileTypes(Enum):
    ARCHIVE = auto()
    AUDIO = auto()
    DOCUMENT = auto()
    VIDEO = auto()
    STILL_IMAGE = auto()
    TEXT = auto()


@dataclass(frozen=True)
class ClassWithFile(Class):
    file_type: DspFileTypes
```

### Cardinality

`Cardinality` connects a property to a class.
`property_display_order` sets the position of the property in the user interface.

```python
class CardinalityNumber(Enum):
    C_0_1 = "0-1"
    C_1 = "1"
    C_0_N = "0-n"
    C_1_N = "1-n"


@dataclass(frozen=True)
class Cardinality:
    property: str
    cardinality: CardinalityNumber
    property_display_order: int | None  # this is the gui_order
```

### Property

`Property` is abstract. The user creates one of three types:

- `DatatypeProperty`: the value is a literal, for example a text or a date.
- `ObjectProperty`: the value is a link to a resource.
- `ControlledVocabularyProperty`: the value is a node of a controlled vocabulary.

Each type has only the fields that it needs.
Thus, a link property with a vocabulary name is not possible.

The property type replaces the combination of `super`, `object` and `gui_element` in the JSON project file.
The user states the intent, for example `TEXT_MULTI_LINE`.
`dsp-vre` then selects the correct `knora-api` super-property, value type and GUI element.

As with classes, `internal_super_properties` gives inheritance and `external_mapping` gives meaning only.

```python
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
    TEXT_MULTI_LINE = auto()
    TEXT_FORMATTED = auto()
    TIME = auto()
    URI = auto()
    HAS_COMMENT = auto()
    SEQNUM = auto()


class DspObjectPropertyTypes(Enum):
    LINK_TO_CLASS = auto()
    IS_PART_OF_COLLECTION = auto()
    HAS_REPRESENTATION = auto()


@dataclass(frozen=True)
class Property(ABC):
    name: str
    label_comments: list[LabelComments]
    internal_super_properties: set[str] | None
    external_mapping: set[str] | None
    subject_class: str | None


@dataclass(frozen=True)
class DatatypeProperty(Property):
    dsp_type: DspDatatypePropertyTypes


@dataclass(frozen=True)
class ObjectProperty(Property):
    dsp_type: DspObjectPropertyTypes
    object_class: str


@dataclass(frozen=True)
class ControlledVocabularyProperty(Property):
    vocabulary_name: str
```

| JSON project file                                               | Proposed field                                 |
|-----------------------------------------------------------------|------------------------------------------------|
| `ontologies[].name`, `label`, `comment`                         | `Ontology`: same names                         |
| `resources[].labels`, `comments`                                | `Class.class_information`                      |
| `resources[].super` (project class)                             | `Class.ontology_super_classes`                 |
| `resources[].super` (external class)                            | `Class.external_mapping`                       |
| `resources[].super: StillImageRepresentation` (and other files) | `ClassWithFile.file_type`                      |
| `cardinalities[].propname`, `cardinality`                       | `Cardinality.property`, `cardinality`          |
| `cardinalities[].gui_order`                                     | `Cardinality.property_display_order`           |
| `properties[].labels`, `comments`                               | `Property.label_comments`                      |
| `properties[].super` (project property)                         | `Property.internal_super_properties`           |
| `properties[].super` (external property)                        | `Property.external_mapping`                    |
| `properties[].subject`                                          | `Property.subject_class`                       |
| `properties[].super`, `object`, `gui_element`                   | `dsp_type`                                     |
| `properties[].object` (class name)                              | `ObjectProperty.object_class`                  |
| `properties[].gui_attributes: {"hlist": ...}`                   | `ControlledVocabularyProperty.vocabulary_name` |

## Controlled Vocabulary

`ControlledVocabulary` is a tree of nodes. The JSON project file calls it a list.
`VocabularyNode` can have sub-nodes, thus the tree can have many levels.
Each node has a label and a comment in each language.

```python
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
```

| JSON project file (`lists`)  | Proposed field                                |
|------------------------------|-----------------------------------------------|
| `lists[].name`               | `ControlledVocabulary.vocabulary_name`        |
| `lists[].labels`, `comments` | `ControlledVocabulary.vocabulary_information` |
| `lists[].nodes`              | `ControlledVocabulary.vocabulary_nodes`       |
| `nodes[].name`               | `VocabularyNode.node_name`                    |
| `nodes[].labels`, `comments` | `VocabularyNode.node_information`             |
| `nodes[].nodes`              | `VocabularyNode.vocabulary_sub_nodes`         |
