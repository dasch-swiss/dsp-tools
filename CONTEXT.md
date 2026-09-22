# DSP-TOOLS

A CLI and library for building a DSP project's data model on a server and bulk-importing data into it. One
cohesive domain — this file covers the whole repo; there is no per-context split.

## Language

### Project & data model

**Project**:
A DSP server's top-level unit of organization: a container bundling metadata (shortcode, shortname), one or
more ontologies, and optionally groups, users, and lists.

**Ontology**:
A formal, network-structured set of resource classes and properties with logical dependencies between them,
defined in a project's JSON file.
_Avoid_: "data model" as a synonym for one ontology — see Flagged ambiguities.

**Resource class**:
A type defined in an ontology: the template for a kind of real-world entity, declaring its properties and
their cardinalities.
_Avoid_: "resource" alone when the class/instance distinction matters.

**Resource instance**:
A concrete `<resource>` element in an XML data file, with real values, that DSP creates as one object on the
server.
_Avoid_: "resource" alone when the class/instance distinction matters.

**Property**:
A data field declared on a resource class in the ontology, with a data type and a cardinality.

**Value**:
The concrete instance of a property's data held by one resource instance (for example a `TextValue` or
`IntValue`).

**Cardinality**:
The declared minimum and maximum number of times a property may occur on a resource class's instances
(`1`, `0-1`, `1-n`, `0-n`).

**List** / **ListNode**:
A list is a controlled vocabulary defined in a project's `lists` section, flat or hierarchical. A ListNode is
one node in that tree.

### XML data & upload

**Bitstream**:
A file or media asset attached to a resource instance via the `<bitstream>` XML element, used only on
`*Representation` resource classes.
_Avoid_: none — "multimedia asset" and "multimedia file" are common, acceptable informal aliases.

**Richtext**:
A `TextValue` gui_element for longer text carrying DSP's standard markup, written in the XML file as
`<text encoding="xml">`. Standoff is the underlying markup mechanism Richtext relies on; it is DSP-API's
concept, defined in DSP-API's own docs, not here.

**Stash**:
A property value — a link value or a standoff-bearing richtext value — held back temporarily during
`xmlupload` because it would create a circular reference between resources not yet created, then re-applied
in a second pass once every resource exists.

**Upload** vs **Ingest**:
Upload moves raw files to the server (`upload-files`) without processing them. Ingest is the separate, later
server-side step (`ingest-files`) that processes uploaded files and produces a mapping from original paths to
internal filenames, which `ingest-xmlupload` then uses to create the actual resources.
_Avoid_: using "ingest" and "upload" interchangeably — the split workflow depends on keeping them distinct.
The plain `xmlupload` command still does both under one roof for simpler cases.

### Identifiers

**Shortcode**:
A project's unique 4-hex-character identifier, assigned by DaSCH.

**Shortname**:
A project's unique, human-readable slug (`xsd:NCNAME` form).

**IRI**:
DSP's actual, internal resource identifier (`http://rdfh.ch/...`).

**ARK**:
DSP's citable, stable external identifier for a resource — DaSCH promises an ARK stays resolvable long
term, a promise an IRI does not carry. A resource's ARK is minted by the server once dsp-tools has created
it; dsp-tools' own code never mints one. The one ARK-related mechanism inside dsp-tools is migration: the
XML `ark` attribute on `<resource>` carries a pre-existing legacy (version-0) salsah.org ARK, converted
once, one-way, into the resource's IRI (`ark2iri.py`) so a migrated resource keeps its old citable URL
alive.
_Avoid_: assuming dsp-tools generates ARKs, or that ARK "resolves to" an IRI at runtime — it only ever
converts a pre-existing legacy one, for migration.

### Permissions & legal metadata

**Permission**:
A right (`RV`, `V`, `M`, `D`, `CR`) granted to a group over a resource or value, declared via the XML
`<permissions>` element.

**DOAP (Default Object Access Permission)**:
The project-level default permission set, configured server-side, that applies automatically to new
resources and values unless a permission is given explicitly per XML element.
_Avoid_: using "DOAP" and "Permission" interchangeably — DOAP is specifically the project-wide default, not
any permission.

**License**, **Copyright**, **Authorship**:
A resource's or file's legal metadata. License is a Creative Commons license IRI, which must be one of the
project's `enabled_licenses`. Copyright names the copyright holder. Authorship names the natural person(s)
who authored the work.
_Avoid_: conflating a resource record's authorship with its multimedia asset's authorship — these are two
separate `authorship-id` attributes, one on `<resource>` and one on `<bitstream>`/`<iiif-uri>`.

### Command groups

**Group A command**:
A CLI command safe to fail fast with a traceback, because it runs in a controlled environment (a local
stack, staging) before production use: `create`, `get`, `xmlupload`, `upload-files`, `ingest-files`,
`ingest-xmlupload`, `resume-xmlupload`.

**Group B command**:
A CLI command, or `xmllib`, that must aggregate every problem it finds into one user-facing report rather
than stopping at the first error, because it runs locally against user-owned files: the `excel2json` family,
`id2iri`, `update-legal`, `validate-data`, `start-stack`/`stop-stack`, `xmllib`.

## Relationships

- A **Project** has one or more **Ontologies**, and optionally **Lists**, groups, and users.
- An **Ontology** defines **Resource classes**, each with **Properties** and their **Cardinalities**.
- A **Resource instance** is created from a **Resource class** and holds the **Values** its **Properties**'
  **Cardinalities** require — zero, one, or many per property.
- A **Resource instance** may reference a **Bitstream**, which carries its own License/Copyright/Authorship,
  separate from the resource's own.
- A **DOAP** supplies the default **Permission** for a resource or value unless the XML gives one explicitly.
- A resource is created by exactly one of two independent workflows: the single `xmlupload` command
  (**Upload**, **Ingest**, and resource creation together), or the split `upload-files` → `ingest-files` →
  `ingest-xmlupload` sequence (the same three steps, run and resumable independently).
- A **Stash** exists only for the duration of an `xmlupload` run, holding values whose target
  **Resource instance** does not exist yet.

## Example dialogue

> **Dev:** "The e2e test uploads a **Resource instance** and its **Bitstream** — do we need to set
> **Authorship** twice?"
> **Reviewer:** "Yes — the resource's own `authorship-id` and the bitstream's `authorship-id` are separate.
> They're often the same person, but the schema tracks them independently."

## Flagged ambiguities

- "Data model" is used informally in the docs for a project's full set of **Ontologies** — resolved: keep
  "ontology" as the precise, single-JSON-object term; "data model" stays acceptable only as loose,
  collective prose.
- "Standoff" has no local definition in dsp-tools — resolved: it is DSP-API's concept, referenced here only
  through **Richtext**, and not redefined in this repo.
- "ARK" risked being reduced to "dsp-tools' legacy migration conversion" — resolved: ARK is DSP's general,
  citable, stable external identifier; dsp-tools' only role is the one-way conversion of a pre-existing
  legacy salsah.org ARK into an IRI during migration, never minting a new one.
