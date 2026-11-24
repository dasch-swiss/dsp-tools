---
status: proposed
date: 2026-11-11
---

# Interface of `create` in `dsp-vre`

## Summary

This document proposes the input dataclasses for the `create` operation in `dsp-vre`.
For each dataclass, it gives the intent, the code and the related keys of the JSON project file.
The principles come from the [ADR for the public interface](adr/0001-public-interface.md).
The steps of `create` are in [dsp-vre-to-tools-map.md](../../../docs/dsp-tools-split/dsp-vre-to-tools-map.md).
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
- References are typed objects, for example `ClassRef`, not strings.
  Names and identifiers of one item stay strings, for example a username or a shortcode.
- Multilingual texts have their own class, for example `Labels`.
- Variants are a union of dataclasses with a type alias, one dataclass for each variant.
  Each variant has only the fields that it needs. There is no inheritance.
- Enums are only for a small closed set without data, for example `CardinalityNumber`.
  Enums are plain `Enum`, not `StrEnum`. The mapping to server values is internal.
- Factory functions are the intended way to build the objects, as in `xmllib`.
  The name of a factory matches the name of its dataclass, for example `properties.integer` and `IntegerProperty`.

### Validation

The types cannot express all rules, for example "a link to a class with a file needs a class with a file".
Each dataclass has a `validate()` method that returns a tuple of problems. It does not raise.
The user can call `validate()` before an action.

Each action calls `validate()` on all objects of its input, for example `add_data_model`.
The action then checks the rules across objects on the complete input, for example "each reference resolves".
If there are problems, the action raises one exception that holds all problems.
The action then writes nothing to the server.

Programming errors raise, for example invalid input, a wrong type or a call of a stub.
Runtime conditions are results, for example a rejection by the server (ADR principle 11).

## Operations

Each domain has its own operations, named by their intent:

| Domain       | Operation                                 |
|--------------|-------------------------------------------|
| Projects     | `create_project`, `set_legal_settings`    |
| Permissions  | `add_user`, `add_group`, `add_membership` |
| Data Model   | `add_data_model`, `set_visibility`        |
| Vocabularies | `add_vocabulary`                          |

One aggregate operation sets up a complete project in one call:

```python
result = set_up_project(
    conn,
    project=Project(shortcode="0854", shortname="daschland", ...),
    legal_settings=ProjectLegalSettings(...),
    vocabularies=(vocabulary_1,),
    data_models=(data_model_1, data_model_2),
    groups=(...),
    users=(...),
    memberships=(...),
)
```

The aggregate has these advantages:

- `dsp-vre` knows the order of the steps, not `dsp-tools`.
- `dsp-vre` checks the references across domains before the first write.
- The call has one progress stream and one result.

An operation for one kind of item fails if the item exists.
The aggregate skips the items that exist, as `dsp-tools create` does today.
Its result reports the skipped items (ADR principle 7).

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
If `dsp-tools` wants stricter rules, it checks them before it calls `dsp-vre`.

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

biblio.cls("Book")  # ClassRef(data_model="biblio", name="Book")
biblio.prop("hasAuthor")  # PropertyRef(data_model="biblio", name="hasAuthor")
```

A vocabulary belongs to the project, thus `VocabularyRef` has no data model.
A user reference and a group reference are the name only.

`dsp-vre` has no prefixes.
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
`dsp-vre` always gets a password.
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

### Group

`Group` is a custom group of the project, as in `dsp-tools` today.
A group has members only. A visibility does not refer to a group.
Permission levels on groups are future work (ADR principle 9).

```python
@dataclass(frozen=True, kw_only=True)
class Group:
    name: str
    descriptions: Descriptions | None = None
```

### Project Membership

`ProjectMembership` connects a user to the project.
It sets the project role of the user and the custom groups of the user.
A user has one project role in a project.
It is separate from `User`, because a user can exist before the project and be a member of many projects.
The project is an argument of the function, not a field of the dataclass.

The project role states what the person can do.
`dsp-vre` then sets the necessary rights on the server.

The names of the roles are open for a discussion with product management.

```python
class ProjectRole(Enum):
    READ = auto()
    WRITE = auto()
    ADMIN = auto()


@dataclass(frozen=True, kw_only=True)
class ProjectMembership:
    username: str
    role: ProjectRole
    groups: tuple[str, ...] = ()
```

The roles give these rights:

| Role    | Project data | Create resources | Data model, users, legal info, permissions | Current implementation |
|---------|--------------|------------------|--------------------------------------------|------------------------|
| `ADMIN` | `CR`         | Yes              | Yes                                        | `:admin`               |
| `WRITE` | `D`          | Yes              | No                                         | `:member`              |
| `READ`  | `V`          | No               | No                                         | -                      |

`CR` includes delete and the change of permissions. `D` includes delete, but not the change of permissions.
A user with `READ` can see private data of the project.

DSP-API has no read level.
Until it has one, `dsp-vre` creates a standardised custom group for `READ` in each project.
The fixed group makes the later change to a server level simple.
The group only works where it is part of the permission.
Thus, each default permission and each explicit permission must include it,
also the permissions that `xmlupload`, DSP-APP or the API set.

| JSON project file (`project`)     | Proposed field                       |
|-----------------------------------|--------------------------------------|
| `users[].username`, `email`       | `User`: same names                   |
| `users[].givenName`, `familyName` | `User.given_name`, `family_name`     |
| `users[].password`                | `User.password`                      |
| `users[].password: null`          | `User.password` from the environment |
| `users[].lang`                    | `User.language`                      |
| `users[].projects: [":admin"]`    | `ProjectRole.ADMIN`                  |
| `users[].projects: [":member"]`   | `ProjectRole.WRITE`                  |
| `users[].projects: ["other:..."]` | Not supported in `dsp-vre`           |
| `groups[].name`, `descriptions`   | `Group`: same names                  |
| `users[].groups`                  | `ProjectMembership.groups`           |

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
    classes: tuple[ResourceClass, ...] = ()
    properties: tuple[Property, ...] = ()
```

### Resource Classes

`ResourceClass` is a class of the data model.
It is a union with one dataclass for each file type, and `PlainClass` for a class without a file.
On the server, `PlainClass` is a sub-class of `knora-api:Resource`.
A class with a file is a sub-class of a `knora-api` representation.
The user selects the dataclass. The user does not select the `knora-api` super-class.

The intent is to separate two kinds of super-classes:

- `project_super_classes`: classes of the same project. They give inheritance, which is visible in DSP.
- `external_mappings`: classes of external ontologies, for example CIDOC CRM. They give meaning only.

The order of `cardinalities` is the display order of the properties in the user interface.

Only a class with a file has `file_visibility`.
Only `ImageClass`, `VideoClass` and `AudioClass` accept `FileVisibility.LIMITED_VIEW`.

`part_of` makes the class a part of a compound object, for example a page of a book.
Only `ImageClass` has `part_of`, because DSP shows a compound object as a sequence of images.
The target of `part_of` is a `PlainClass`.
DSP-API accepts any resource as a part and as a target. `dsp-vre` is stricter.
`dsp-vre` then creates the `isPartOf` link property and the `seqnum` property for the class,
and their cardinalities of `1`.
The naming pattern of these two properties is not decided.

```python
@dataclass(frozen=True, kw_only=True)
class PlainClass:
    name: str
    labels: Labels
    comments: Comments | None = None
    project_super_classes: tuple[ClassRef, ...] = ()
    external_mappings: tuple[ExternalIri, ...] = ()
    cardinalities: tuple[Cardinality, ...] = ()
    visibility: Visibility = Visibility.PUBLIC


@dataclass(frozen=True, kw_only=True)
class DocumentClass:
    # ... the fields of PlainClass
    file_visibility: FileVisibility | None = None


@dataclass(frozen=True, kw_only=True)
class ImageClass:
    # ... the fields of PlainClass
    file_visibility: FileVisibility | None = None
    part_of: ClassRef | None = None


type ResourceClass = (
    PlainClass | CompressedArchiveClass | AudioClass | DocumentClass | VideoClass | ImageClass | TextClass
)
```

The factories build the classes:

```python
classes.plain("Book", labels=Labels(en="Book"))
classes.image("Page", labels=Labels(en="Page"), part_of=biblio.cls("Book"))
classes.image("Photo", labels=Labels(en="Photo"), file_visibility=FileVisibility.LIMITED_VIEW)
```

| Factory                      | Dataclass                | `knora-api` super-class     |
|------------------------------|--------------------------|-----------------------------|
| `classes.plain`              | `PlainClass`             | `Resource`                  |
| `classes.compressed_archive` | `CompressedArchiveClass` | `ArchiveRepresentation`     |
| `classes.audio`              | `AudioClass`             | `AudioRepresentation`       |
| `classes.document`           | `DocumentClass`          | `DocumentRepresentation`    |
| `classes.video`              | `VideoClass`             | `MovingImageRepresentation` |
| `classes.image`              | `ImageClass`             | `StillImageRepresentation`  |
| `classes.text`               | `TextClass`              | `TextRepresentation`        |

`validate()` checks this rule:

- `LIMITED_VIEW` is only on `ImageClass`, `VideoClass` or `AudioClass`.

`dsp-vre` checks these rules on the complete input:

- The target of `part_of` is a `PlainClass`.
- Each reference resolves.
- The visibility rules in [Permissions](#permissions).

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

The factories are a short form:

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

### Properties

`Property` is a union with one dataclass for each value type.
The dataclass states the intent, for example a text with many lines.
`dsp-vre` then selects the correct `knora-api` super-property, value type and GUI element.

The dataclass replaces the combination of `super`, `object` and `gui_element` in the JSON project file.

As with classes, `project_super_properties` gives inheritance and `external_mappings` gives meaning only.

`LinkProperty.target` is the class that a link points to.
`None` means that the link can point to any resource.
`VocabularyProperty.vocabulary` is the controlled vocabulary of the property.

```python
@dataclass(frozen=True, kw_only=True)
class TextOneLineProperty:
    name: str
    labels: Labels
    comments: Comments | None = None
    subject_class: ClassRef | None = None
    project_super_properties: tuple[PropertyRef, ...] = ()
    external_mappings: tuple[ExternalIri, ...] = ()
    visibility: Visibility = Visibility.PUBLIC


@dataclass(frozen=True, kw_only=True)
class LinkProperty:
    # ... the fields of TextOneLineProperty
    target: ClassRef | None = None


@dataclass(frozen=True, kw_only=True)
class VocabularyProperty:
    # ... the fields of TextOneLineProperty
    vocabulary: VocabularyRef


type Property = (
    BooleanProperty
    | ColorProperty
    | DateProperty
    | DecimalProperty
    | GeolocationProperty
    | GeonameProperty
    | IntegerProperty
    | RegionPreviewProperty
    | TextOneLineProperty
    | TextMultiLineProperty
    | TextFormattedProperty
    | TimeProperty
    | UriProperty
    | CommentProperty
    | LinkProperty
    | LinkToClassWithFileProperty
    | VocabularyProperty
)
```

The factories build the properties:

```python
properties.text_one_line("title", labels=Labels(en="Title", de="Titel"))
properties.link("hasAuthor", target=biblio.cls("Person"), labels=Labels(en="Author"))
properties.vocabulary("hasGenre", vocabulary=VocabularyRef(name="genres"), labels=Labels(en="Genre"))
```

`dsp-vre` checks these rules on the complete input:

- The `target` of `LinkToClassWithFileProperty` is a class with a file, or `None`.
- Each reference resolves.

The table shows which dataclass replaces which combination in the JSON project file.

| Factory                              | Dataclass                     | `super`             | `object`                               | `gui_element`   |
|--------------------------------------|-------------------------------|---------------------|----------------------------------------|-----------------|
| `properties.boolean`                 | `BooleanProperty`             | `hasValue`          | `BooleanValue`                         | `Checkbox`      |
| `properties.color`                   | `ColorProperty`               | `hasColor`          | `ColorValue`                           | `Colorpicker`   |
| `properties.date`                    | `DateProperty`                | `hasValue`          | `DateValue`                            | `Date`          |
| `properties.decimal`                 | `DecimalProperty`             | `hasValue`          | `DecimalValue`                         | `Spinbox`       |
| `properties.geolocation`             | `GeolocationProperty`         | `hasValue`          | `GeolocationValue`                     | `Geolocation`   |
| `properties.geoname`                 | `GeonameProperty`             | `hasValue`          | `GeonameValue`                         | `Geonames`      |
| `properties.integer`                 | `IntegerProperty`             | `hasValue`          | `IntValue`                             | `Spinbox`       |
| `properties.region_preview`          | `RegionPreviewProperty`       | `hasRegionPreview`  | `RegionPreviewValue`                   | `RegionPreview` |
| `properties.text_one_line`           | `TextOneLineProperty`         | `hasValue`          | `TextValue`                            | `SimpleText`    |
| `properties.text_multi_line`         | `TextMultiLineProperty`       | `hasValue`          | `TextValue`                            | `Textarea`      |
| `properties.text_formatted`          | `TextFormattedProperty`       | `hasValue`          | `TextValue`                            | `Richtext`      |
| `properties.time`                    | `TimeProperty`                | `hasValue`          | `TimeValue`                            | `TimeStamp`     |
| `properties.uri`                     | `UriProperty`                 | `hasValue`          | `UriValue`                             | `SimpleText`    |
| `properties.comment`                 | `CommentProperty`             | `hasComment`        | `TextValue`                            | `Richtext`      |
| `properties.link`                    | `LinkProperty`                | `hasLinkTo`         | a class, or `Resource`                 | `Searchbox`     |
| `properties.link_to_class_with_file` | `LinkToClassWithFileProperty` | `hasRepresentation` | a class with file, or `Representation` | `Searchbox`     |
| `properties.vocabulary`              | `VocabularyProperty`          | `hasValue`          | `ListValue`                            | `List`          |

`DecimalProperty` and `IntegerProperty` always use `Spinbox`, as in DSP-APP.
The JSON project file also allows `SimpleText`. This is a breaking change.

| JSON project file                                               | Proposed field                             |
|-----------------------------------------------------------------|--------------------------------------------|
| `ontologies[].name`, `label`, `comment`                         | `DataModel`: same names                    |
| `resources[].labels`, `comments`                                | `labels`, `comments` of the class          |
| `resources[].super` (project class)                             | `project_super_classes` of the class       |
| `resources[].super` (external class)                            | `external_mappings` of the class           |
| `resources[].super: Resource`                                   | `classes.plain`                            |
| `resources[].super: StillImageRepresentation` (and other files) | `classes.image` (and other file factories) |
| `cardinalities[].propname`, `cardinality`                       | `cardinalities.<factory>(PropertyRef)`     |
| `cardinalities[].gui_order`                                     | Order of `cardinalities` of the class      |
| `properties[].super: isPartOf`, `seqnum`                        | `ImageClass.part_of`                       |
| `properties[].labels`, `comments`                               | `labels`, `comments` of the property       |
| `properties[].super` (project property)                         | `project_super_properties` of the property |
| `properties[].super` (external property)                        | `external_mappings` of the property        |
| `properties[].subject`                                          | `subject_class` of the property            |
| `properties[].super`, `object`, `gui_element`                   | `properties.<factory>`                     |
| `properties[].object` (class name)                              | `target` of the link property              |
| `properties[].object: Resource`, `Representation`               | `target = None`                            |
| `properties[].gui_attributes: {"hlist": ...}`                   | `VocabularyProperty.vocabulary`            |

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

| Target                    | Field                          |
|---------------------------|--------------------------------|
| All data of the project   | `Project.visibility`           |
| A class and its file      | `visibility` of the class      |
| The file of a class       | `file_visibility` of the class |
| A property on all classes | `visibility` of the property   |
| A property on one class   | `Cardinality.visibility`       |

The default value is always valid.
With the default, the effective level is the most restricted level of the item and its parents.
For example, a public property on a private class is private.
`Visibility.PUBLIC` is the default, thus an explicit `PUBLIC` has the same effect.

An explicit value that is less restricted than its parent is a problem.
`dsp-vre` checks these rules on the complete input:

- A class with `visibility=PRIVATE` has no `file_visibility`. The private class already makes the file private.
- If `Project.visibility` is `PRIVATE`, no class has `file_visibility` `PUBLIC` or `LIMITED_VIEW`.

On the server, a visibility is a default object access permission (DOAP).
The server applies a DOAP only to data that it creates after the DOAP.
Thus, a visibility is the default for new data. It does not change data that exists.

A file is a value of the resource, and Sipi uses only the permissions of the file value.
Thus, for a private class, `dsp-vre` also creates a DOAP for the file value.
The user does not see this DOAP.

`set_visibility` sets the visibility of an item in an existing data model.
It needs no update of the data model. Its signature is not decided.

| JSON project file (`project`)                      | Proposed field                                                               |
|----------------------------------------------------|------------------------------------------------------------------------------|
| `default_permissions: "public"`                    | `Project.visibility = PUBLIC` (default)                                      |
| `default_permissions: "private"`                   | `Project.visibility = PRIVATE`                                               |
| `default_permissions_overrule.private` (class)     | `visibility = PRIVATE` of the class                                          |
| `default_permissions_overrule.private` (property)  | `visibility = PRIVATE` of the property                                       |
| `default_permissions_overrule.limited_view: [...]` | `file_visibility = LIMITED_VIEW` of the class                                |
| `default_permissions_overrule.limited_view: "all"` | `dsp-tools` sets it on each image, video and audio class of a public project |
| Not available                                      | `Cardinality.visibility`                                                     |
| Not available                                      | `FileVisibility.PRIVATE`                                                     |

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

`dsp-vre` does not support these parts of the JSON project file.
They are the exceptions to the parity rule in the ADR.

| JSON project file                                                       | Reason                                                                     |
|-------------------------------------------------------------------------|----------------------------------------------------------------------------|
| `prefixes`                                                              | Replaced by the [References](#references) rule.                            |
| `gui_attributes` other than `hlist`                                     | `dsp-tools create` ignores them today.                                     |
| `gui_element`: `Radio`, `Pulldown`                                      | `dsp-tools create` does not support them today.                            |
| `gui_element: SimpleText` for `IntValue`, `DecimalValue`                | `DecimalProperty` and `IntegerProperty` always use `Spinbox`.              |
| `resources[].super`: `Representation`, `DDDRepresentation`, `Region`    | Out of scope for the first release. No file ingest for 3D.                 |
| `isPartOf`, `seqnum` other than on an image class, with cardinality `1` | DSP shows a compound object as a sequence of images. See `part_of`.        |
| `isPartOf` with a target that has a file                                | The target of a compound object is a `PlainClass`.                         |
| `users[].projects` of other projects                                    | `dsp-tools create` ignores them today. The project is a function argument. |
