[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Permissions Guide

DSP has a two-layer permission system.
The first layer sets **project-wide defaults** in the JSON project definition file.
The second layer lets you **override those defaults per resource or property** in the XML data file.
Understanding both layers — and how they interact — gives you fine-grained control over who can see what.

## The Building Blocks

### Built-in User Groups

Every user on DSP belongs to one or more built-in groups:

| Group           | Who is in it                                                     |
| --------------- | ---------------------------------------------------------------- |
| `UnknownUser`   | Anyone not logged in                                             |
| `KnownUser`     | Logged-in users who are **not** members of the project           |
| `ProjectMember` | Logged-in users who belong to the project                        |
| `ProjectAdmin`  | Project administrators                                           |
| `Creator`       | The user who created the specific resource or value (DEPRECATED) |
| `SystemAdmin`   | System-level administrators                                      |

You can also define your own [project-specific groups (aka custom groups)](./data-model/json-project/overview.md#groups)
in the JSON project file.

### Rights Hierarchy

A group can hold exactly one right, and each right includes all the rights below it:

| Right | Name                  | What it allows                                                                   |
| ----- | --------------------- | -------------------------------------------------------------------------------- |
| `CR`  | Change Right          | Modify permissions; permanently erase resources                                  |
| `D`   | Delete                | Mark a resource/value as deleted (original is preserved)                         |
| `M`   | Modify                | Edit a resource/value                                                            |
| `V`   | View                  | View at full quality                                                             |
| `RV`  | Restricted View       | Images: view at reduced resolution or with a watermark; Video/Audio: No download |
| —     | _(no right assigned)_ | No access at all                                                                 |

> `CR` implies `D`, which implies `M`, which implies `V`, which implies `RV`.

## Layer 1: Project-Wide Defaults (JSON)

The JSON project file sets a baseline that applies to every resource and value
unless an explicit override is provided in the XML file.

### `default_permissions`

Choose one of two project-wide stances:

```json
"default_permissions": "public"
```

or

```json
"default_permissions": "private"
```

- **`public`**: `UnknownUser` and `KnownUser` can view everything. This is the open-access default.
- **`private`**: Only `ProjectMember` and `ProjectAdmin` can view anything.
  Everything is locked down by default for `UnknownUser` and `KnownUser`.

### `default_permissions_overrule` (only when `default_permissions` is `"public"`)

When your project is public, you may still want to restrict certain classes or properties.
Use `default_permissions_overrule` to carve out exceptions:

```json
"default_permissions": "public",
"default_permissions_overrule": {
    "private": [
        "my-onto:SensitiveDocument",
        "my-onto:hasPrivateNote"
    ],
    "limited_view": "all"
}
```

The two available restriction levels are:

- **`private`**: A list of class or property names.
    - For a **class**: resources of that class are invisible to `UnknownUser` and `KnownUser`.
    - For a **property**: the property's content is hidden, but the rest of the resource remains public.
- **`limited_view`**: A list of image classes whose images are blurred/watermarked for outsiders.
  Only the image is affected — the rest of the resource stays public.
  Use the special value `"all"` to apply this to every `StillImageRepresentation` subclass,
  including ones created in the future.

> We have to adapt DSP-TOOLS to also allow audio/video for `limited_view`.

```json
"default_permissions": "public",
"default_permissions_overrule": {
    "private": [
        "my-onto:InternalCorrespondence",
        "my-onto:hasSSN"
    ],
    "limited_view": [
        "my-onto:HighResPhoto",
        "my-onto:ArchiveScan"
    ]
}
```

## Layer 2: Per-Resource Overrides (XML)

The XML data file lets you override the project defaults for individual resources, values,
and multimedia assets. This layer uses two constructs: **permission IDs** and the **`permissions` attribute**.

### Defining Permission IDs With `<permissions>`

At the top of the XML file, before any `<resource>` elements,
you can define named permission sets using `<permissions>` elements.

The three canonical IDs cover the most common access patterns:

```xml
<permissions id="public">
    <allow group="UnknownUser">V</allow>
    <allow group="KnownUser">V</allow>
    <allow group="ProjectMember">D</allow>
    <allow group="ProjectAdmin">CR</allow>
</permissions>

<permissions id="limited_view">
    <allow group="UnknownUser">RV</allow>
    <allow group="KnownUser">RV</allow>
    <allow group="ProjectMember">D</allow>
    <allow group="ProjectAdmin">CR</allow>
</permissions>

<permissions id="private">
    <allow group="ProjectMember">D</allow>
    <allow group="ProjectAdmin">CR</allow>
</permissions>
```

Any group omitted from a `<permissions>` block has **no access at all** to that resource/value.

You can also reference project-specific groups:

```xml
<permissions id="editors-only">
    <allow group="my-project:editors">M</allow>
</permissions>
```

### Applying Permissions With the `permissions` Attribute

Use the IDs you defined as a `permissions` attribute on `<resource>` elements or value elements:

```xml
<resource label="Board minutes 2024" restype=":Meeting" id="meeting_001" permissions="private">
    <text-prop name=":hasTitle">
        <text encoding="utf8" permissions="public">Board Meeting, January 2024</text>
    </text-prop>
    <text-prop name=":hasMinutes">
        <text encoding="utf8" permissions="private">... confidential content ...</text>
    </text-prop>
</resource>
```

Notice that `<resource permissions="private">` only sets the resource's own permission.
**Properties do not inherit from their resource** — each value
must have its own `permissions` attribute if you want to control access at that level.

If you omit the `permissions` attribute entirely, the project defaults apply.

## Putting It All Together

Here is a scenario with a mixed public/private project:

**JSON project file** — project is public, but images are watermarked and one class is locked down:

```json
"default_permissions": "public",
"default_permissions_overrule": {
    "private": [
        "archive:InternalMemo"
    ],
    "limited_view": "all"
}
```

**XML data file** — individual overrides on top of those defaults:

```xml
<!-- Permission IDs defined once at the top -->
<permissions id="public">
    <allow group="UnknownUser">V</allow>
    <allow group="KnownUser">V</allow>
    <allow group="ProjectMember">D</allow>
    <allow group="ProjectAdmin">CR</allow>
</permissions>
<permissions id="limited_view">
    <allow group="UnknownUser">RV</allow>
    <allow group="KnownUser">RV</allow>
    <allow group="ProjectMember">D</allow>
    <allow group="ProjectAdmin">CR</allow>
</permissions>
<permissions id="private">
    <allow group="ProjectMember">D</allow>
    <allow group="ProjectAdmin">CR</allow>
</permissions>

<!-- A photo: the resource is public, the image is served with watermark -->
<resource label="Stadtansicht 1910" restype=":Photo" id="photo_001" permissions="public">
    <bitstream
        license="http://rdfh.ch/licenses/cc-by-4.0"
        copyright-holder="City Archive"
        authorship-id="authorship_1"
        permissions="limited_view">
            photos/stadtansicht_1910.tif
    </bitstream>
    <text-prop name=":hasCaption">
        <text encoding="utf8" permissions="public">View of the old town, ca. 1910</text>
    </text-prop>
</resource>

<!-- An internal memo: resource and all its values are locked down -->
<resource label="Budget note 2024-03" restype=":InternalMemo" id="memo_042" permissions="private">
    <text-prop name=":hasContent">
        <text encoding="utf8" permissions="private">... confidential ...</text>
    </text-prop>
</resource>
```

## Quick Reference

| Question                                                    | Where to set it                                           |
| ----------------------------------------------------------- | --------------------------------------------------------- |
| Should the whole project be public or private by default?   | `default_permissions` in JSON                             |
| Should certain classes or properties be exceptions?         | `default_permissions_overrule` in JSON                    |
| Should a specific resource differ from the project default? | `permissions` attribute on `<resource>` in XML            |
| Should a specific value differ from its resource?           | `permissions` attribute on the value element in XML       |
| Does a resource share its permissions with its values?      | **No.** Each value needs its own `permissions` attribute. |

## Further Reading

- [JSON project overview — `default_permissions`](./data-model/json-project/overview.md#default_permissions)
- [JSON project overview — `default_permissions_overrule`](./data-model/json-project/overview.md#default_permissions_overrule)
- [XML data file — defining permissions](./data-file/xml-data-file.md#defining-permissions-with-the-permissions-element)
- [XML data file — using permissions](./data-file/xml-data-file.md#using-permissions-with-the-permissions-attribute)
