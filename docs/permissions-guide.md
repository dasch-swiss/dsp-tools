[![PyPI version](https://badge.fury.io/py/dsp-tools.svg)](https://badge.fury.io/py/dsp-tools)

# Permissions Guide

DSP has a two-layer permission system.
The first layer sets **project-wide defaults** in the JSON project definition file.
The second layer lets you **override those defaults per resource or property** in the XML data file.
Understanding both layers — and how they interact — gives you fine-grained control over who can see what.

## The Building Blocks

### Built-in User Groups

Every user on DSP belongs to exactly one built-in group:

| Group           | Who is in it                                           |
| --------------- | ------------------------------------------------------ |
| `SystemAdmin`   | System-level administrators                            |
| `ProjectAdmin`  | Project administrators                                 |
| `ProjectMember` | Logged-in users who belong to the project              |
| `KnownUser`     | Logged-in users who are **not** members of the project |
| `UnknownUser`   | Anyone not logged in                                   |

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

> `CR` implies `D`, which implies `M`, which implies `V`.
> `RV` is a separate, more restrictive access level — it does not follow from `V`.

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
    <allow group="ProjectAdmin">CR</allow>
    <allow group="ProjectMember">D</allow>
    <allow group="KnownUser">V</allow>
    <allow group="UnknownUser">V</allow>
</permissions>

<permissions id="limited_view">
    <allow group="ProjectAdmin">CR</allow>
    <allow group="ProjectMember">D</allow>
    <allow group="KnownUser">RV</allow>
    <allow group="UnknownUser">RV</allow>
</permissions>

<permissions id="private">
    <allow group="ProjectAdmin">CR</allow>
    <allow group="ProjectMember">D</allow>
</permissions>
```

Any group omitted from a `<permissions>` block has **no access at all** to that resource/value.

The IDs `public`, `limited_view`, and `private` are conventions, not reserved keywords.
Any name is valid; these three are used across DSP-TOOLS documentation and tooling
because they cover the most common access patterns.
Treating them as a shared vocabulary keeps projects readable and consistent across the DSP ecosystem.

### Applying Permissions With the `permissions` Attribute

Use the IDs you defined as a `permissions` attribute on `<resource>` elements or value elements:

```xml
<resource label="Board minutes 2024" restype=":Meeting" id="meeting_001" permissions="public">
    <text-prop name=":hasTitle">
        <text encoding="utf8" permissions="public">Board Meeting, January 2024</text>
    </text-prop>
    <text-prop name=":hasMinutes">
        <text encoding="utf8" permissions="private">... confidential content ...</text>
    </text-prop>
</resource>
```

Notice that `<resource permissions="public">` only sets the resource's own permission.
**Properties do not inherit from their resource** — each value
must have its own `permissions` attribute if you want to control access at that level.

If you omit the `permissions` attribute entirely, the project defaults apply.

## Custom Groups

In addition to the built-in groups, you can define project-specific groups in the JSON project file.
Custom groups are additional membership tiers that sit between `ProjectMember` and `ProjectAdmin`:
they let you grant finer-grained rights to a subset of project members.

A custom group cannot hold fewer rights than `ProjectMember`, and cannot hold more rights than
`ProjectAdmin`.

### Defining Custom Groups in JSON

Add a `groups` array to your JSON project file:

```json
"groups": [
  {
    "name": "editors",
    "descriptions": {"en": "Editors for the project"}
  }
]
```

The `name` and `descriptions` fields are mandatory.

### Using Custom Groups in XML

Reference a custom group as `project-shortname:groupname` in a `<permissions>` block:

```xml
<permissions id="editors_only">
    <allow group="my-project:editors">M</allow>
    <allow group="ProjectAdmin">CR</allow>
</permissions>
```

Any group omitted from the block has no access at all to that resource or value.

## Further Reading

- [JSON project overview — `default_permissions`](./data-model/json-project/overview.md#default_permissions)
- [JSON project overview — `default_permissions_overrule`](./data-model/json-project/overview.md#default_permissions_overrule)
- [JSON project overview — `groups`](./data-model/json-project/overview.md#groups)
- [XML data file — defining permissions](./data-file/xml-data-file.md#defining-permissions-with-the-permissions-element)
- [XML data file — using permissions](./data-file/xml-data-file.md#using-permissions-with-the-permissions-attribute)
