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
| `CR`  | Change Rights         | Change the access permissions on a resource or value                             |
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
    <allow group="ProjectAdmin">CR</allow>
    <allow group="my-project:editors">M</allow>
</permissions>
```

Any group omitted from the block has no access at all to that resource or value.

## Permission Use Cases

This section walks through common research data management scenarios and shows how to configure
DSP's two-layer permission system for each one.

### 1. Fully Open Access

**Situation**: All project data should be freely accessible to anyone — logged in or not.
Typical for openly licensed, publicly funded research.

**Access goals**:

- `UnknownUser` → View
- `KnownUser` → View
- `ProjectMember` → Delete
- `ProjectAdmin` → Change Right (CR)

**Layer 1 — JSON** (project-wide default):

```json
"default_permissions": "public"
```

**Layer 2 — XML** (per-resource overrides):

No `permissions` attribute is required on resources or values.
The JSON default applies automatically:

```xml
<resource label="Letter 1842-03-12" restype=":Letter" id="letter_001">
    <text-prop name=":hasContent">
        <text encoding="utf8">Dear Sir, ...</text>
    </text-prop>
</resource>
```

### 2. Fully Private Project (Embargo)

**Situation**: Data must stay invisible to the outside world — for example, during an active
research phase before publication or while under a data-sharing embargo.

**Access goals**:

- `UnknownUser` → no access
- `KnownUser` → no access
- `ProjectMember` → Delete
- `ProjectAdmin` → Change Right (CR)

**Layer 1 — JSON**:

```json
"default_permissions": "private"
```

No XML overrides are needed. All resources and values are locked down by default.

> **Note**: Individual resources can still be made public by adding `permissions="public"` in
> the XML — useful if a small subset of your data has already been cleared for release while
> the rest remains under embargo.

### 3. Private Project With External Academic Access

**Situation**: The project data should not be visible to the general public, but selected
external academics need read access. The actual project team must retain editing rights.

The external academics are added as `ProjectMember`, giving them project-level access.
Because `ProjectMember` is repurposed as a viewer role here, a custom group (e.g. `editors`)
is defined for the actual team.

**Access goals**:

- `UnknownUser` → no access
- `KnownUser` → no access
- `ProjectMember` (external academics) → View
- `my-project:editors` (actual team) → Delete
- `ProjectAdmin` → Change Right (CR)

**Layer 1 — JSON**:

Define the custom group alongside the private default:

```json
"default_permissions": "private",
"groups": [
    {
        "name": "editors",
        "descriptions": {"en": "Team members with editing rights"}
    }
]
```

After project creation, the `ProjectAdmin` adds the actual team to the `editors` group
via DSP-APP, and adds external academics as `ProjectMember`.

**Permissions script (after project creation)**:

Since custom groups are a rare edge case, their rights cannot be configured in the JSON.
The server's Administrative Permissions and Default Object Access Permissions (DOAPs) need
adjustment. Write a Python script using the `dsp-permissions-script` template that makes the
following changes:

- **Administrative Permissions**: remove `ProjectResourceCreateAllPermission` from `ProjectMember`.
- **DOAPs**: degrade `ProjectMember` from `D` to `V`.
- **DOAPs**: grant `D` to the `my-project:editors` custom group.

**Layer 2 — XML** (per-resource overrides):

After running the permissions-scripts, no `permissions` attribute is required on resources or values in the XML.
The defaults set by the permissions-scripts apply automatically:

```xml
<resource label="Letter 1842-03-12" restype=":Letter" id="letter_001">
    <text-prop name=":hasContent">
        <text encoding="utf8">Dear Sir, ...</text>
    </text-prop>
</resource>
```

### 4. Public Project With Watermarked Images

**Situation**: All metadata is freely accessible, but image files are served watermarked or at
reduced resolution for outsiders because the images are still under copyright.

**Access goals**:

- `UnknownUser` / `KnownUser` → Restricted View on images (watermark or reduced resolution)
- `ProjectMember` → Delete
- `ProjectAdmin` → Change Right (CR)
- Metadata (text properties, etc.) → fully public

**Layer 1 — JSON**:

```json
"default_permissions": "public",
"default_permissions_overrule": {
    "limited_view": "all"
}
```

`"all"` applies restricted view to every `StillImageRepresentation` subclass,
including classes added in the future.

**Layer 2 — XML**:

No `permissions` attribute is needed on image resources or their bitstreams.
The JSON overrule handles restricted view automatically:

```xml
<resource label="Stadtansicht 1910" restype=":Photo" id="photo_001">
    <bitstream
        license="http://rdfh.ch/licenses/cc-by-4.0"
        copyright-holder="City Archive"
        authorship-id="authorship_1">
            photos/stadtansicht_1910.tif
    </bitstream>
    <text-prop name=":hasCaption">
        <text encoding="utf8">View of the old town, ca. 1910</text>
    </text-prop>
</resource>
```

> **After project creation**: Log in to DSP-APP and choose whether restricted view means a
> **watermark** or a **reduced resolution** for your project's images.
> This setting cannot be configured in DSP-TOOLS.

### 5. Public Project With Audio/Video Restricted to Streaming Only

**Situation**: All metadata is freely accessible, but audio or video files must not be
downloadable by outsiders — for example, in an oral history archive with copyright-restricted
recordings.

For audio and video, Restricted View (`RV`) means the file can be played in the browser but
cannot be downloaded. Unlike images, the JSON `limited_view` setting does not yet cover
audio/video, so restricted view must be applied via an XML `permissions` attribute on each
bitstream.

<!--TODO: Rewrite this section once https://linear.app/dasch/issue/DEV-6308/ is resolved -->

**Access goals**:

- `UnknownUser` / `KnownUser` → Restricted View on A/V bitstreams (streaming only, no download)
- `ProjectMember` → Delete
- `ProjectAdmin` → Change Right (CR)
- Metadata → fully public

**Layer 1 — JSON**:

```json
"default_permissions": "public"
```

**Layer 2 — XML**:

Define a `limited_view` permission ID and apply it to audio/video bitstreams.
The resource itself and its text properties carry no `permissions` attribute
and remain fully public:

```xml
<permissions id="limited_view">
    <allow group="ProjectAdmin">CR</allow>
    <allow group="ProjectMember">D</allow>
    <allow group="KnownUser">RV</allow>
    <allow group="UnknownUser">RV</allow>
</permissions>

<resource label="Interview Meier 2019" restype=":AudioRecording" id="audio_001">
    <bitstream
        license="http://rdfh.ch/licenses/cc-by-nc-4.0"
        copyright-holder="Research Project"
        authorship-id="authorship_1"
        permissions="limited_view">
            audio/interview_meier_2019.mp3
    </bitstream>
    <text-prop name=":hasTitle">
        <text encoding="utf8">Interview with M. Meier, July 2019</text>
    </text-prop>
</resource>
```

### 6. Property-Level Confidentiality

**Situation**: Resources are publicly visible, but certain properties must be hidden from
outsiders — for example, donor names, curatorial notes, or personal data in an archive.

**Access goals**:

- `archive:hasDonorName` → invisible to `UnknownUser` and `KnownUser`
- All resources + all other properties → publicly visible
- `ProjectMember` → Delete
- `ProjectAdmin` → Change Right (CR)

**Layer 1 — JSON**:

```json
"default_permissions": "public",
"default_permissions_overrule": {
    "private": [
        "archive:hasDonorName"
    ]
}
```

**Layer 2 — XML**:

No `permissions` attribute is needed. The JSON overrule hides the sensitive property
automatically for `UnknownUser` and `KnownUser`:

```xml
<resource label="Letter 1901-07-04" restype=":Letter" id="letter_042">
    <text-prop name=":hasContent">
        <text encoding="utf8">Dear friend, ...</text>
    </text-prop>
    <text-prop name=":hasDonorName">
        <text encoding="utf8">Müller family archive</text>
    </text-prop>
</resource>
```

### 7. Mixed Batched Publication

**Situation**: Research is released incrementally. Some resources are already published and
publicly visible; others are still in progress and must remain private until cleared for release.

**Access goals**:

- Published resources → fully public
- In-progress resources → visible to `ProjectMember` / `ProjectAdmin` only

**Layer 1 — JSON**:

```json
"default_permissions": "public"
```

**Layer 2 — XML**:

Published resources carry no `permissions` attribute and inherit the public default.
In-progress resources use `permissions="private"`:

```xml
<permissions id="private">
    <allow group="ProjectAdmin">CR</allow>
    <allow group="ProjectMember">D</allow>
</permissions>

<!-- Already published — no permissions attribute needed -->
<resource label="Survey results 2022" restype=":Report" id="report_2022">
    <text-prop name=":hasTitle">
        <text encoding="utf8">Survey Results 2022</text>
    </text-prop>
</resource>

<!-- Still in progress — explicitly private -->
<resource label="Survey results 2023" restype=":Report" id="report_2023" permissions="private">
    <text-prop name=":hasTitle">
        <text encoding="utf8" permissions="private">Survey Results 2023</text>
    </text-prop>
</resource>
```

> **Note**: Properties do not inherit permissions from their resource.
> If a resource is marked private, its values must each carry `permissions="private"` as well.


## Further Reading

- [JSON project overview — `default_permissions`](./data-model/json-project/overview.md#default_permissions)
- [JSON project overview — `default_permissions_overrule`](./data-model/json-project/overview.md#default_permissions_overrule)
- [JSON project overview — `groups`](./data-model/json-project/overview.md#groups)
- [XML data file — defining permissions](./data-file/xml-data-file.md#defining-permissions-with-the-permissions-element)
- [XML data file — using permissions](./data-file/xml-data-file.md#using-permissions-with-the-permissions-attribute)
