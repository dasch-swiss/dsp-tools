---
status: proposed
date: 2026-11-11
---

# Interface of `create` in `dsp-vre-lib`

## Summary

This document proposes the input dataclasses for the `create` operation in `dsp-vre-lib`.
For each dataclass, it gives the intent, the code and the related keys of the JSON project file.
The principles come from [ADR-dsp-vre-lib.md](ADR-dsp-vre-lib.md).
The steps of `create` are in [dsp-vre-lib-to-tools-map.md](dsp-vre-lib-to-tools-map.md).
The sections follow the order of the domains in the ADR.

## Design Rules

The dataclasses follow these rules:

1. A dataclass shows only fields that the user can or must fill.
2. The types make each object structurally sound. The factories help the user to build correct objects.
3. The names do not use `dsp-tools` terms or old `knora` terms.
4. The names describe the intent, for example they do not refer to the GUI ontology.
5. The names use the DaSCH domain terms, for example "data model" and "compound object".
6. "Permissions" is the term for the VRE. "Access rights" is reserved for the future archive.

The code follows these conventions:

- All dataclasses are `frozen=True, kw_only=True`. Optional fields have a default.
- Collections are tuples. An empty tuple is the default, not `None`.
- The public types contain no `Mapping`, `dict` or `list`.
- Small values have their own class, for example `Labels` and `ClassRef`, not strings.
- Enums are plain `Enum`, not `StrEnum`. The mapping to server values is internal.
- One dataclass for each concept. There are no sub-classes and no union of one class for each variant.
- Factory functions are the intended way to build the objects, as in `xmllib`.
  The factories hide the internal enums, for example the value type of a property.

### Validation

The types cannot express all rules, for example "a file visibility needs a file".
Each dataclass has a `validate()` method that returns a tuple of problems. It does not raise.
`dsp-vre-lib` calls `validate()` before each action, for example before `add_data_model`.
The user can call `validate()` earlier.
Rules across objects, for example "each reference resolves", are checked on the complete input of the action.

Programming errors raise, for example a wrong type or a call of a stub.
Runtime conditions are results, for example a rejection by the server (ADR principle 11).

## Operations

Each domain has its own operations, named by their intent:

| Domain                | Operation                              |
|-----------------------|----------------------------------------|
| Projects              | `create_project`, `set_legal_settings` |
| Users and Permissions | `add_user`, `add_membership`           |
| Data Model            | `add_data_model`, `set_visibility`     |
| Vocabularies          | `add_vocabulary`                       |

One aggregate operation sets up a complete project in one call:

```python
result = set_up_project(
    conn,
    project=Project(shortcode="0854", shortname="daschland", ...),
    legal_settings=ProjectLegalSettings(...),
    vocabularies=(vocabulary_1,),
    data_models=(data_model_1, data_model_2),
    users=(...),
    memberships=(...),
)
```

The aggregate has these advantages:

- `dsp-vre-lib` knows the order of the steps, not `dsp-tools`.
- `dsp-vre-lib` checks the references across domains before the first write.
- The call has one progress stream and one result.

The names of the operations are working names.
The result types are in the ADR.

Not in this document:

- Connection: it has no `create` input.
- Data: `xmlupload` creates data, not `create`.

## Shared Types

### Language, Labels and Comments

`Language` is the closed set of languages that DSP supports.

`Labels` holds a maximum of one label for each language.
`Comments` and `Descriptions` have the same fields as `Labels`.
`validate()` checks that there is a minimum of one language and no empty string.

Comments are optional, as in `dsp-tools` today.
If `dsp-tools` wants stricter rules, it checks them before it calls `dsp-vre-lib`.

```python
class Language(Enum):
    EN = auto()
    DE = auto()
    FR = auto()
    IT = auto()
    RM = auto()


@dataclass(frozen=True, kw_only=True)
class Labels:
    en: str | None = None
    de: str | None = None
    fr: str | None = None
    it: str | None = None
    rm: str | None = None


Labels(en="Book", de="Buch")
```

| JSON project file              | Proposed field                   |
|--------------------------------|----------------------------------|
| `labels: {"en": "..."}`        | `Labels(en="...")`               |
| `comments: {"en": "..."}`      | `Comments(en="...")`             |
| `descriptions: {"en": "..."}`  | `Descriptions(en="...")`         |
| Language code as a free string | Field of `Labels`, or `Language` |

### References

The user refers to items by their local names (ADR principle 4).
A reference is a typed object, not a string:

```python
@dataclass(frozen=True, kw_only=True)
class ClassRef:
    data_model: str
    name: str


@dataclass(frozen=True, kw_only=True)
class PropertyRef:
    data_model: str
    name: str


@dataclass(frozen=True, kw_only=True)
class VocabularyRef:
    name: str


@dataclass(frozen=True, kw_only=True)
class ExternalIri:
    iri: str
```

The typed references have these advantages:

- A malformed reference fails when the object is built.
- The type checker finds a class where a property is necessary.
- A copy of a data model under a new name can change each reference safely.

A helper binds the name of the data model:

```python
biblio = refs("biblio")

biblio.cls("Book")        # ClassRef(data_model="biblio", name="Book")
biblio.prop("hasAuthor")  # PropertyRef(data_model="biblio", name="hasAuthor")
```

A vocabulary belongs to the project, thus `VocabularyRef` has no data model.
A user reference is the username only.

`dsp-vre-lib` has no prefixes.
`dsp-tools` uses the `prefixes` of the JSON project file to change prefixed external names into full IRIs.

## Projects

### Project

A system admin creates the project.
`Project` holds the identity, the description and the visibility of the project.

`visibility=Visibility.PRIVATE` makes all data of the project private.
On the server, it is a project-wide default permission.
It is the approximation of a private project until DSP-API supports private projects.
See [Permissions](#permissions).

```python
@dataclass(frozen=True, kw_only=True)
class Project:
    shortcode: str
    shortname: str
    longname: str
    descriptions: Descriptions | None = None
    keywords: tuple[str, ...] = ()
    visibility: Visibility = Visibility.PUBLIC
```

Embargo and archive access rights need support in DSP-API first. They are not in this interface.

### Legal Information

A project admin sets the legal information.
`ProjectLegalSettings` is separate from `Project`.

`License` is the closed set of licenses that the server supports.
`License` needs an update with each API version that changes the licenses.

```python
class License(Enum):
    CC_BY_4_0 = auto()
    CC_BY_SA_4_0 = auto()
    # ... one member for each license of the server


@dataclass(frozen=True, kw_only=True)
class ProjectLegalSettings:
    enabled_licenses: tuple[License, ...] = ()
    data_license: License | None = None
    data_copyright_holder: str | None = None
    default_data_authorship: tuple[str, ...] = ()
```

| JSON project file (`project`)                                                          | Proposed field                     |
|----------------------------------------------------------------------------------------|------------------------------------|
| `shortcode`, `shortname`, `longname`, `keywords`                                       | `Project`: same names              |
| `descriptions: {"en": "..."}`                                                          | `Project.descriptions`             |
| `default_permissions`                                                                  | `Project.visibility`               |
| `enabled_licenses`, `data_license`, `data_copyright_holder`, `default_data_authorship` | `ProjectLegalSettings`: same names |
| License as a free string                                                               | `License`                          |

## Users and Permissions

### User

`User` is a person who can log in.
`dsp-vre-lib` always gets a password.
If the JSON project file has no password, `dsp-tools` reads it from the environment variable `DSP_USER_PASSWORD`.

```python
@dataclass(frozen=True, kw_only=True)
class User:
    username: str
    email: str
    given_name: str
    family_name: str
    password: str
    language: Language = Language.EN
```

### Project Membership

`ProjectMembership` connects a user to the project and sets the permission of the user.
A user has one permission in a project.
It is separate from `User`, because a user can exist before the project and be a member of many projects.
The project is an argument of the function, not a field of the dataclass.

The user does not see groups. The permission states what the person can do.
`dsp-vre-lib` then sets the necessary rights on the server.

The names of the levels are open for a discussion with product management.

```python
class ProjectPermission(Enum):
    READ = auto()
    WRITE = auto()
    ADMIN = auto()


@dataclass(frozen=True, kw_only=True)
class ProjectMembership:
    username: str
    permission: ProjectPermission
```

The levels give these rights:

| Level   | Project data | Create resources | Data model, users, legal info, permissions | Current implementation |
|---------|--------------|------------------|--------------------------------------------|------------------------|
| `ADMIN` | `CR`         | Yes              | Yes                                        | `:admin`               |
| `WRITE` | `D`          | Yes              | No                                         | `:member`              |
| `READ`  | `V`          | No               | No                                         | -                      |

`CR` includes delete and the change of permissions. `D` includes delete, but not the change of permissions.
A user with `READ` can see private data of the project.

DSP-API has no read level.
Until it has one, `dsp-vre-lib` creates a standardised custom group for `READ` in each project.
The fixed group makes the later change to a server level simple.
The group only works where it is part of the permission.
Thus, each default permission and each explicit permission must include it,
also the permissions that `xmlupload`, DSP-APP or the API set.

### Fallback: Groups

If the permission levels are rejected, `dsp-vre-lib` uses the classical groups of DSP-API.
Then the interface has a `Group`, and `GroupMembership` has the groups of the user:

```python
@dataclass(frozen=True, kw_only=True)
class Group:
    name: str
    descriptions: Descriptions | None = None


@dataclass(frozen=True, kw_only=True)
class GroupMembership:
    username: str
    is_project_admin: bool = False
    groups: tuple[str, ...] = ()
```

| JSON project file (`project`)     | Proposed field                       |
|-----------------------------------|--------------------------------------|
| `users[].username`, `email`       | `User`: same names                   |
| `users[].givenName`, `familyName` | `User.given_name`, `family_name`     |
| `users[].password`                | `User.password`                      |
| `users[].password: null`          | `User.password` from the environment |
| `users[].lang`                    | `User.language`                      |
| `users[].projects: [":admin"]`    | `ProjectPermission.ADMIN`            |
| `users[].projects: [":member"]`   | `ProjectPermission.WRITE`            |
| `users[].projects: ["other:..."]` | Not supported in `dsp-vre-lib`       |
| `groups[]`, `users[].groups`      | No field (fallback only)             |

## Data Model

### DataModel

`DataModel` holds the classes and the properties of one data model.
The label is one string and the comment is optional.
They are not `Labels` and `Comments`, because the server supports only one language for a data model.

```python
@dataclass(frozen=True, kw_only=True)
class DataModel:
    name: str
    label: str
    comment: str | None = None
    classes: tuple[Class, ...] = ()
    properties: tuple[Property, ...] = ()
```

### Class

`Class` is a class of the data model.
On the server, a class without a file is a sub-class of `knora-api:Resource`.
A class with a file is a sub-class of a `knora-api` representation.
The user selects the file type. The user does not select the `knora-api` super-class.

The intent is to separate two kinds of super-classes:

- `project_super_classes`: classes of the same project. They give inheritance, which is visible in DSP.
- `external_mappings`: classes of external ontologies, for example CIDOC CRM. They give meaning only.

`part_of` makes the class a part of a compound object, for example a page of a book.
Only a class with the file type `IMAGE` can be a part, because DSP shows a compound object as a sequence of images.
The target of `part_of` is a class without a file, for example made by `classes.plain`.
DSP-API accepts any resource as a part and as a target. `dsp-vre-lib` is stricter.
`dsp-vre-lib` then creates the `isPartOf` link property and the `seqnum` property for the class,
and their cardinalities of `1`.
The naming pattern of these two properties is not decided.

The order of `cardinalities` is the display order of the properties in the user interface.

```python
class FileType(Enum):
    COMPRESSED_ARCHIVE = auto()
    AUDIO = auto()
    DOCUMENT = auto()
    VIDEO = auto()
    IMAGE = auto()
    TEXT = auto()


@dataclass(frozen=True, kw_only=True)
class Class:
    name: str
    labels: Labels
    comments: Comments | None = None
    file: FileType | None = None
    project_super_classes: tuple[ClassRef, ...] = ()
    external_mappings: tuple[ExternalIri, ...] = ()
    part_of: ClassRef | None = None
    cardinalities: tuple[Cardinality, ...] = ()
    visibility: Visibility = Visibility.PUBLIC
    file_visibility: FileVisibility | None = None
```

The factories set the file type:

```python
classes.plain("Book", labels=Labels(en="Book"))
classes.image("Page", labels=Labels(en="Page"), part_of=biblio.cls("Book"))
classes.image("Photo", labels=Labels(en="Photo"), file_visibility=FileVisibility.LIMITED_VIEW)
```

Only `classes.image` has the parameter `part_of`.

| Factory                      | `FileType`           | `knora-api` super-class     |
|------------------------------|----------------------|-----------------------------|
| `classes.plain`              | -                    | `Resource`                  |
| `classes.compressed_archive` | `COMPRESSED_ARCHIVE` | `ArchiveRepresentation`     |
| `classes.audio`              | `AUDIO`              | `AudioRepresentation`       |
| `classes.document`           | `DOCUMENT`           | `DocumentRepresentation`    |
| `classes.video`              | `VIDEO`              | `MovingImageRepresentation` |
| `classes.image`              | `IMAGE`              | `StillImageRepresentation`  |
| `classes.text`               | `TEXT`               | `TextRepresentation`        |

`Class.validate()` checks these rules:

- `file_visibility` needs a `file`.
- `LIMITED_VIEW` needs the file type `IMAGE`, `VIDEO` or `AUDIO`.
- `part_of` needs the file type `IMAGE`.

`dsp-vre-lib` checks these rules on the complete input:

- The target of `part_of` is a class without a file.
- Each reference resolves.
- A class with `visibility=PRIVATE` has no `file_visibility`. The private class already makes the file private.

### Cardinality

`Cardinality` connects a property to a class.

```python
class CardinalityNumber(Enum):
    ZERO_OR_ONE = auto()
    ONE = auto()
    ZERO_OR_MORE = auto()
    ONE_OR_MORE = auto()


@dataclass(frozen=True, kw_only=True)
class Cardinality:
    property: PropertyRef
    cardinality: CardinalityNumber
    visibility: Visibility = Visibility.PUBLIC
```

The factories hide `CardinalityNumber`:

```python
cardinalities.one(biblio.prop("hasTitle"))
cardinalities.zero_or_more(biblio.prop("hasNote"), visibility=Visibility.PRIVATE)
```

| Factory                      | JSON project file |
|------------------------------|-------------------|
| `cardinalities.zero_or_one`  | `0-1`             |
| `cardinalities.one`          | `1`               |
| `cardinalities.zero_or_more` | `0-n`             |
| `cardinalities.one_or_more`  | `1-n`             |

The names of the factories can change after the implementation.

### Property

`Property` is one dataclass for all properties.
`value_type` states the intent, for example a text with many lines.
`dsp-vre-lib` then selects the correct `knora-api` super-property, value type and GUI element.

The value type replaces the combination of `super`, `object` and `gui_element` in the JSON project file.
The factories set `value_type`. The user does not set it directly.

As with classes, `project_super_properties` gives inheritance and `external_mappings` gives meaning only.

`target` is the class that a link points to.
`None` means that the link can point to any resource.
`vocabulary` is the controlled vocabulary of a vocabulary property.

```python
class ValueType(Enum):
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
    LINK = auto()
    LINK_TO_CLASS_WITH_FILE = auto()
    VOCABULARY = auto()


@dataclass(frozen=True, kw_only=True)
class Property:
    name: str
    labels: Labels
    comments: Comments | None = None
    value_type: ValueType
    target: ClassRef | None = None
    vocabulary: VocabularyRef | None = None
    subject_class: ClassRef | None = None
    project_super_properties: tuple[PropertyRef, ...] = ()
    external_mappings: tuple[ExternalIri, ...] = ()
    visibility: Visibility = Visibility.PUBLIC
```

The factories set only the fields that the value type needs:

```python
properties.text_one_line("title", labels=Labels(en="Title", de="Titel"))
properties.link("hasAuthor", target=biblio.cls("Person"), labels=Labels(en="Author"))
properties.vocabulary("hasGenre", vocabulary=VocabularyRef(name="genres"), labels=Labels(en="Genre"))
```

`Property.validate()` checks these rules:

- Only `LINK` and `LINK_TO_CLASS_WITH_FILE` have a `target`.
- Only `VOCABULARY` has a `vocabulary`, and it must have one.

`dsp-vre-lib` checks these rules on the complete input:

- For `LINK_TO_CLASS_WITH_FILE`, `target` is a class with a file, or `None`.
- Each reference resolves.

The table shows which factory replaces which combination in the JSON project file.

| Factory                              | `value_type`              | `super`             | `object`                               | `gui_element`   |
|--------------------------------------|---------------------------|---------------------|----------------------------------------|-----------------|
| `properties.boolean`                 | `BOOLEAN`                 | `hasValue`          | `BooleanValue`                         | `Checkbox`      |
| `properties.color`                   | `COLOR`                   | `hasColor`          | `ColorValue`                           | `Colorpicker`   |
| `properties.date`                    | `DATE`                    | `hasValue`          | `DateValue`                            | `Date`          |
| `properties.decimal`                 | `DECIMAL`                 | `hasValue`          | `DecimalValue`                         | `Spinbox`       |
| `properties.geolocation`             | `GEOLOCATION`             | `hasValue`          | `GeolocationValue`                     | `Geolocation`   |
| `properties.geoname`                 | `GEONAME`                 | `hasValue`          | `GeonameValue`                         | `Geonames`      |
| `properties.integer`                 | `INT`                     | `hasValue`          | `IntValue`                             | `Spinbox`       |
| `properties.region_preview`          | `REGION_PREVIEW`          | `hasRegionPreview`  | `RegionPreviewValue`                   | `RegionPreview` |
| `properties.text_one_line`           | `TEXT_ONE_LINE`           | `hasValue`          | `TextValue`                            | `SimpleText`    |
| `properties.text_multi_line`         | `TEXT_MULTI_LINE`         | `hasValue`          | `TextValue`                            | `Textarea`      |
| `properties.text_formatted`          | `TEXT_FORMATTED`          | `hasValue`          | `TextValue`                            | `Richtext`      |
| `properties.time`                    | `TIME`                    | `hasValue`          | `TimeValue`                            | `TimeStamp`     |
| `properties.uri`                     | `URI`                     | `hasValue`          | `UriValue`                             | `SimpleText`    |
| `properties.comment`                 | `HAS_COMMENT`             | `hasComment`        | `TextValue`                            | `Richtext`      |
| `properties.link`                    | `LINK`                    | `hasLinkTo`         | a class, or `Resource`                 | `Searchbox`     |
| `properties.link_to_class_with_file` | `LINK_TO_CLASS_WITH_FILE` | `hasRepresentation` | a class with file, or `Representation` | `Searchbox`     |
| `properties.vocabulary`              | `VOCABULARY`              | `hasValue`          | `ListValue`                            | `List`          |

`DECIMAL` and `INT` always use `Spinbox`, as in DSP-APP.
The JSON project file also allows `SimpleText`. This is a breaking change.

| JSON project file                                               | Proposed field                             |
|-----------------------------------------------------------------|--------------------------------------------|
| `ontologies[].name`, `label`, `comment`                         | `DataModel`: same names                    |
| `resources[].labels`, `comments`                                | `Class.labels`, `comments`                 |
| `resources[].super` (project class)                             | `Class.project_super_classes`              |
| `resources[].super` (external class)                            | `Class.external_mappings`                  |
| `resources[].super: StillImageRepresentation` (and other files) | `classes.image` (and other file factories) |
| `cardinalities[].propname`, `cardinality`                       | `cardinalities.<factory>(PropertyRef)`     |
| `cardinalities[].gui_order`                                     | Order of `Class.cardinalities`             |
| `properties[].super: isPartOf`, `seqnum`                        | `Class.part_of`                            |
| `properties[].labels`, `comments`                               | `Property.labels`, `comments`              |
| `properties[].super` (project property)                         | `Property.project_super_properties`        |
| `properties[].super` (external property)                        | `Property.external_mappings`               |
| `properties[].subject`                                          | `Property.subject_class`                   |
| `properties[].super`, `object`, `gui_element`                   | `properties.<factory>`                     |
| `properties[].object` (class name)                              | `Property.target`                          |
| `properties[].object: Resource`, `Representation`               | `Property.target = None`                   |
| `properties[].gui_attributes: {"hlist": ...}`                   | `Property.vocabulary`                      |

### Permissions

A permission hides data from users outside the project.
The default is public. Thus, the user sets a visibility only on the items that need one.

```python
class Visibility(Enum):
    PUBLIC = auto()
    PRIVATE = auto()


class FileVisibility(Enum):
    PUBLIC = auto()
    PRIVATE = auto()
    LIMITED_VIEW = auto()
```

The levels give these rights:

| Level        | `ADMIN` | `WRITE` | `READ` | Known and unknown users |
|--------------|---------|---------|--------|-------------------------|
| Public       | `CR`    | `D`     | `V`    | `V`                     |
| Private      | `CR`    | `D`     | `V`    | None                    |
| Limited view | `CR`    | `D`     | `V`    | `RV`                    |

A visibility applies to one of these targets:

| Target                    | Field                    |
|---------------------------|--------------------------|
| All data of the project   | `Project.visibility`     |
| A class and its file      | `Class.visibility`       |
| The file of a class       | `Class.file_visibility`  |
| A property on all classes | `Property.visibility`    |
| A property on one class   | `Cardinality.visibility` |

An item cannot be less restricted than its parent.
The effective level is the most restricted level of the item and its parents.
For example, a public property on a private class is private.

On the server, a visibility is a default object access permission (DOAP).
The server applies a DOAP only to data that it creates after the DOAP.
Thus, a visibility is the default for new data. It does not change data that exists.

A file is a value of the resource, and Sipi uses only the permissions of the file value.
Thus, for a private class, `dsp-vre-lib` also creates a DOAP for the file value.
The user does not see this DOAP.

`set_visibility` sets the visibility of an item in an existing data model.
It needs no update of the data model. Its signature is not decided.

| JSON project file (`project`)                      | Proposed field                                        |
|----------------------------------------------------|-------------------------------------------------------|
| `default_permissions: "public"`                    | `Project.visibility = PUBLIC` (default)               |
| `default_permissions: "private"`                   | `Project.visibility = PRIVATE`                        |
| `default_permissions_overrule.private` (class)     | `Class.visibility = PRIVATE`                          |
| `default_permissions_overrule.private` (property)  | `Property.visibility = PRIVATE`                       |
| `default_permissions_overrule.limited_view: [...]` | `Class.file_visibility = LIMITED_VIEW`                |
| `default_permissions_overrule.limited_view: "all"` | `dsp-tools` sets it on each image, video, audio class |
| Not available                                      | `Cardinality.visibility`                              |
| Not available                                      | `FileVisibility.PRIVATE`                              |

Open decisions:

- A visibility does not refer to a group.
  The full permission model (ADR principle 9) is future work.

## Vocabularies

`ControlledVocabulary` is a tree of nodes. The JSON project file calls it a list.
`VocabularyNode` can have sub-nodes, thus the tree can have many levels.

```python
@dataclass(frozen=True, kw_only=True)
class ControlledVocabulary:
    name: str
    labels: Labels
    comments: Comments | None = None
    nodes: tuple[VocabularyNode, ...]


@dataclass(frozen=True, kw_only=True)
class VocabularyNode:
    name: str
    labels: Labels
    comments: Comments | None = None
    nodes: tuple[VocabularyNode, ...] = ()
```

| JSON project file (`lists`)  | Proposed field                            |
|------------------------------|-------------------------------------------|
| `lists[].name`               | `ControlledVocabulary.name`               |
| `lists[].labels`, `comments` | `ControlledVocabulary.labels`, `comments` |
| `lists[].nodes`              | `ControlledVocabulary.nodes`              |
| `nodes[].name`               | `VocabularyNode.name`                     |
| `nodes[].labels`, `comments` | `VocabularyNode.labels`, `comments`       |
| `nodes[].nodes`              | `VocabularyNode.nodes`                    |

## Not Supported

`dsp-vre-lib` does not support these parts of the JSON project file:

| JSON project file                                                    | Reason                                                         |
|----------------------------------------------------------------------|----------------------------------------------------------------|
| `prefixes`                                                           | Replaced by the [References](#references) rule.                |
| `gui_attributes` other than `hlist`                                  | `dsp-tools create` ignores them today.                         |
| `gui_element`: `Radio`, `Pulldown`                                   | `dsp-tools create` does not support them today.                |
| `gui_element: SimpleText` for `IntValue`, `DecimalValue`             | `DECIMAL` and `INT` always use `Spinbox`.                      |
| `resources[].super`: `Resource`                                      | `classes.plain` is always a sub-class of `Resource`.           |
| `resources[].super`: `Representation`, `DDDRepresentation`, `Region` | Out of scope for the first release. No file ingest for 3D.     |
| `users[].projects` of other projects                                 | The project is an argument of the function.                    |
| `groups`, `users[].groups`                                           | Replaced by project permissions (unless the fallback applies). |
