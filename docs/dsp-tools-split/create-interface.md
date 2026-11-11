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
The sections follow the order of the domains in the ADR.

## Design Rules

The dataclasses follow these rules:

1. A dataclass shows only fields that the user can or must fill.
2. It is not possible to create an invalid object, for example a link property with a list name.
3. The names do not use `dsp-tools` terms or old `knora` terms.
4. The names describe the intent, for example they do not refer to the GUI ontology.

All dataclasses are frozen.

## Scope

Each domain has its own `create` operation and its own input dataclasses.
There is no dataclass that holds a complete project.
`dsp-tools create` calls the operations of the domains in the order of the map.

Not in this document:

- Connection: it has no `create` input.
- Data: `xmlupload` creates data, not `create`.

## Shared Types

### Language, Label and Comment

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

### References

The user refers to items by their local names (ADR principle 4).
A reference has one of these forms:

- An item of the same ontology: the name only, for example `Book`.
- An item of another ontology of the same project: `<ontology>:<name>`, for example `biblio:Book`.
- A class or property of an external ontology: the full IRI, for example `http://www.cidoc-crm.org/cidoc-crm/E22`.
- A user: the username only.

`dsp-vre` has no prefixes.
`dsp-tools` uses the `prefixes` of the JSON project file to change prefixed external names into full IRIs.

## Projects

### Project

A system admin creates the project.
`Project` holds the identity and the description of the project.
`embargo` sets the embargo state at creation. The default is no embargo.

The first release mocks the embargo.
If `embargo` is true, `dsp-vre` creates the restricted permissions and sets all other permissions to private.
When the server implements the embargo, only the code changes, not the interface.
Thus, the JSON project file can record the necessary final state now.

A private project uses the embargo. There is no other project-level private default.

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
`ProjectLegalSettings` is separate from `Project`.

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

## Access

### User

`User` is a person who can log in.
`dsp-vre` always gets a password.
If the JSON project file has no password, `dsp-tools` reads it from the environment variable `DSP_USER_PASSWORD`.

```python
@dataclass(frozen=True)
class User:
    username: str
    email: str
    given_name: str
    family_name: str
    password: str
    language: Language = Language.EN
```

### Project Membership

`ProjectMembership` connects a user to the project and sets the role of the user.
A user has one role in a project.
It is separate from `User`, because a user can exist before the project and be a member of many projects.

The user does not see groups. The role states the intent, for example "this person can edit the data".
`dsp-vre` then sets the necessary rights on the server.

```python
class ProjectUserRole(Enum):
    ADMIN = auto()
    EDITOR = auto()
    WRITER = auto()
    READER = auto()


@dataclass(frozen=True)
class ProjectMembership:
    username: str
    role: ProjectUserRole
```

The roles give these rights:

| Role     | Project data | Create resources | Data model, users, legal info, restrictions |
|----------|--------------|------------------|---------------------------------------------|
| `ADMIN`  | `CR`         | Yes              | Yes                                         |
| `EDITOR` | `D`          | Yes              | No                                          |
| `WRITER` | `M`          | Yes              | No                                          |
| `READER` | `V`          | No               | No                                          |

`CR` includes delete and the change of permissions. `D` includes delete, but not the change of permissions.
`M` does not include delete.
A `READER` can see private data of the project.

### Implementation of Roles

Roles are the design for `dsp-vre`. There are two ways to implement them:

- A: DSP-API supports roles.
  The server enforces the roles.
  This is a breaking change in DSP-API and in `dsp-tools`.
- B: `dsp-vre` creates one fixed custom group for each role, and the default permissions for these groups.
  `ADMIN` uses the existing project admin group.
  This needs no change in DSP-API.
  `dsp-vre` hides the groups, but other clients, for example DSP-APP, show them.

### Fallback: Groups

If A and B are both rejected, `dsp-vre` uses the classical groups of DSP-API.
Then the interface has a `Group`, and `ProjectMembership` has the groups of the user:

```python
@dataclass(frozen=True)
class Group:
    name: str
    descriptions: dict[Language, str]


@dataclass(frozen=True)
class ProjectMembership:
    username: str
    is_project_admin: bool
    groups: set[str]
```

| JSON project file (`project`)        | Proposed field                       |
|--------------------------------------|--------------------------------------|
| `users[].username`, `email`          | `User`: same names                   |
| `users[].givenName`, `familyName`    | `User.given_name`, `family_name`     |
| `users[].password`                   | `User.password`                      |
| `users[].password: null`             | `User.password` from the environment |
| `users[].lang`                       | `User.language`                      |
| `users[].projects: [":admin"]`       | `ProjectUserRole.ADMIN`              |
| `users[].projects: [":member"]`      | Open decision                        |
| `groups[]`, `users[].groups`         | No field (fallback only)             |

Open decisions:

- Mapping of `:member`: today, a member gets `D` (delete) on the project data.
  `EDITOR`: the rights stay the same, because `EDITOR` also has `D`.
  `WRITER`: no member gets a new right, but each member loses the right to delete.

## Data Model

### Ontology

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

- `ontology_super_classes`: classes of the same project. They give inheritance, which is visible in DSP.
- `external_mapping`: classes of external ontologies, for example CIDOC CRM. They give meaning only.

An empty set means that the class has no super-class of that kind.

```python
@dataclass(frozen=True)
class Class:
    name: str
    label_comments: list[LabelComments]
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

| `DspFileTypes` | `knora-api` super-class     |
|----------------|-----------------------------|
| `ARCHIVE`      | `ArchiveRepresentation`     |
| `AUDIO`        | `AudioRepresentation`       |
| `DOCUMENT`     | `DocumentRepresentation`    |
| `VIDEO`        | `MovingImageRepresentation` |
| `STILL_IMAGE`  | `StillImageRepresentation`  |
| `TEXT`         | `TextRepresentation`        |

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
    property_display_order: int | None
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

As with classes, `ontology_super_properties` gives inheritance and `external_mapping` gives meaning only.
An empty set means that the property has no super-property of that kind.

`ObjectProperty.object_class` is the class that the link points to.
For `HAS_REPRESENTATION`, it is a `ClassWithFile` of the project.

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
    ontology_super_properties: set[str]
    external_mapping: set[str]
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

The table shows which property type replaces which combination in the JSON project file.

| Property type                  | `super`             | `object`             | `gui_element`           |
|--------------------------------|---------------------|----------------------|-------------------------|
| `BOOLEAN`                      | `hasValue`          | `BooleanValue`       | `Checkbox`              |
| `COLOR`                        | `hasColor`          | `ColorValue`         | `Colorpicker`           |
| `DATE`                         | `hasValue`          | `DateValue`          | `Date`                  |
| `DECIMAL`                      | `hasValue`          | `DecimalValue`       | `Spinbox`, `SimpleText` |
| `GEOLOCATION`                  | `hasValue`          | `GeolocationValue`   | `Geolocation`           |
| `GEONAME`                      | `hasValue`          | `GeonameValue`       | `Geonames`              |
| `INT`                          | `hasValue`          | `IntValue`           | `Spinbox`, `SimpleText` |
| `REGION_PREVIEW`               | `hasRegionPreview`  | `RegionPreviewValue` | `RegionPreview`         |
| `TEXT_ONE_LINE`                | `hasValue`          | `TextValue`          | `SimpleText`            |
| `TEXT_MULTI_LINE`              | `hasValue`          | `TextValue`          | `Textarea`              |
| `TEXT_FORMATTED`               | `hasValue`          | `TextValue`          | `Richtext`              |
| `TIME`                         | `hasValue`          | `TimeValue`          | `TimeStamp`             |
| `URI`                          | `hasValue`          | `UriValue`           | `SimpleText`            |
| `HAS_COMMENT`                  | `hasComment`        | `TextValue`          | `Richtext`              |
| `SEQNUM`                       | `seqnum`            | `IntValue`           | `Spinbox`, `SimpleText` |
| `LINK_TO_CLASS`                | `hasLinkTo`         | a class              | `Searchbox`             |
| `IS_PART_OF_COLLECTION`        | `isPartOf`          | a class              | `Searchbox`             |
| `HAS_REPRESENTATION`           | `hasRepresentation` | `Representation`     | `Searchbox`             |
| `ControlledVocabularyProperty` | `hasValue`          | `ListValue`          | `List`                  |

For `DECIMAL`, `INT` and `SEQNUM`, `dsp-vre` selects the GUI element.

| JSON project file                                               | Proposed field                                 |
|-----------------------------------------------------------------|------------------------------------------------|
| `ontologies[].name`, `label`, `comment`                         | `Ontology`: same names                         |
| `resources[].labels`, `comments`                                | `Class.label_comments`                         |
| `resources[].super` (project class)                             | `Class.ontology_super_classes`                 |
| `resources[].super` (external class)                            | `Class.external_mapping`                       |
| `resources[].super: StillImageRepresentation` (and other files) | `ClassWithFile.file_type`                      |
| `cardinalities[].propname`, `cardinality`                       | `Cardinality.property`, `cardinality`          |
| `cardinalities[].gui_order`                                     | `Cardinality.property_display_order`           |
| `properties[].labels`, `comments`                               | `Property.label_comments`                      |
| `properties[].super` (project property)                         | `Property.ontology_super_properties`           |
| `properties[].super` (external property)                        | `Property.external_mapping`                    |
| `properties[].subject`                                          | `Property.subject_class`                       |
| `properties[].super`, `object`, `gui_element`                   | `dsp_type`                                     |
| `properties[].object` (class name)                              | `ObjectProperty.object_class`                  |
| `properties[].gui_attributes: {"hlist": ...}`                   | `ControlledVocabularyProperty.vocabulary_name` |

### Access Restrictions

An access restriction hides data from users outside the project.
The default is public. Thus, the user names only the items that have a restriction.
A restriction can only make an item more restricted than its parent.
For example, a public property on a private class is not possible.

On the server, a restriction is a default object access permission (DOAP).
The server applies a DOAP only to data that it creates after the DOAP.
A restriction does not change data that exists.

The levels give these rights:

| Level        | `ADMIN` | `EDITOR` | `WRITER` | `READER` | Known and unknown users |
|--------------|---------|----------|----------|----------|-------------------------|
| Public       | `CR`    | `D`      | `M`      | `V`      | `V`                     |
| Private      | `CR`    | `D`      | `M`      | `V`      | None                    |
| Limited view | `CR`    | `D`      | `M`      | `V`      | `RV`                    |

A restriction applies to one of these targets:

- A class: `private_classes`.
- A property, on all classes: `private_properties`.
- A property on one class: `private_class_properties`.
- The file of a `ClassWithFile`: `file_restrictions`.
  The resource stays public. Only the file is private or has a limited view.

```python
class FileRestrictionType(Enum):
    PRIVATE = auto()
    LIMITED_VIEW = auto()


@dataclass(frozen=True)
class FileRestriction:
    class_name: str
    restriction: FileRestrictionType


@dataclass(frozen=True)
class ClassProperty:
    class_name: str
    property_name: str


@dataclass(frozen=True)
class AccessRestrictions:
    private_classes: set[str]
    private_properties: set[str]
    private_class_properties: set[ClassProperty]
    file_restrictions: set[FileRestriction]
```

`dsp-vre` checks these rules and returns a failure for each item that does not obey them:

- Each class and property name exists in the project.
- `FileRestriction.class_name` is a `ClassWithFile`.
- `LIMITED_VIEW` is only on a `ClassWithFile` of the type `STILL_IMAGE`, `VIDEO` or `AUDIO`.
- Each class has a maximum of one `FileRestriction`.

The Data model domain has three operations for restrictions:

- `create`: sets the restrictions of a project that has none.
- `update`: adds restrictions.
- `delete`: removes the named restrictions.

The restrictions are a separate input, and not fields of `Class` and `Property`. The reasons are:

- A DOAP belongs to the project, not to the ontology.
- The user can set restrictions on an existing ontology without an update of the data model.
- Few items have a restriction. Fields on each class and property add noise for all other items.

The cost of this decision:

- `dsp-vre` must check that each name exists, because the restriction is not part of the class.
- A read of the data model returns the ontologies and the restrictions as two objects.

| JSON project file (`project`)                      | Proposed field                                           |
|----------------------------------------------------|----------------------------------------------------------|
| `default_permissions: "public"`                    | `Project.embargo = False` (Default)                      |
| `default_permissions: "private"`                   | `Project.embargo = True`                                 |
| `default_permissions_overrule.private` (class)     | `AccessRestrictions.private_classes`                     |
| `default_permissions_overrule.private` (property)  | `AccessRestrictions.private_properties`                  |
| `default_permissions_overrule.limited_view: [...]` | `FileRestriction(..., FileRestrictionType.LIMITED_VIEW)` |
| `default_permissions_overrule.limited_view: "all"` | `dsp-tools` adds each image, video and audio class       |
| Not available                                      | `private_class_properties`                               |
| Not available                                      | `FileRestrictionType.PRIVATE`                            |

Open decisions:

- Embargo: during the mocked embargo, all data is private.
  The place that keeps the restrictions until the embargo ends depends on the server design of the embargo.
  For the moment the only record stays the project json file.
- Roles replace groups. A restriction does not refer to a group.
  The full permission model (ADR principle 9) is future work.

## Vocabularies

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

## Not Supported

`dsp-vre` does not support these parts of the JSON project file:

| JSON project file                                                    | Reason                                                     |
|----------------------------------------------------------------------|------------------------------------------------------------|
| `prefixes`                                                           | Replaced by the [References](#references) rule.            |
| `gui_attributes` other than `hlist`                                  | `dsp-tools create` ignores them today.                     |
| `gui_element`: `Radio`, `Pulldown`                                   | `dsp-tools create` does not support them today.            |
| `resources[].super`: `Resource`                                      | `Class` is always a sub-class of `Resource`.               |
| `resources[].super`: `Representation`, `DDDRepresentation`, `Region` | Out of scope for the first release. No file ingest for 3D. |
| A label without a comment                                            | Each language has a label and a comment (`LabelComments`). |
| `groups`, `users[].groups`                                           | Replaced by project roles.                                 |
