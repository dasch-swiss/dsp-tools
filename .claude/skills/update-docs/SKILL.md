---
name: update-docs
description: >-
  This skill should be used whenever a change to dsp-tools alters user-facing behavior (new or
  modified), to decide IF the docs under `docs/` need updating and, if so, WHERE. Trigger it for
  changes to a value type, gui_element, property, or JSON project-definition section; the XML
  data-file format; a CLI command or what it does; the public `xmllib` API; or domain vocabulary
  (permissions, licenses). Also trigger on outcome-phrased work like "add support for a new value",
  "change what an existing command does", "add an xmllib helper", or "we changed the behaviour, do
  the docs need updating?". It gates whether docs are actually warranted (user-facing does NOT mean
  documented — don't bloat the docs) and maps every place a warranted change must land.
allowed-tools: Read, Edit, Glob, Grep
---

# Documenting user-facing changes

This is the playbook for the question **"I changed something users can observe — do the docs need
updating, and where?"** This skill makes the evaluation explicit so nothing gets half-documented.

Two steps: **(1)** decide *whether* docs are warranted at all, then **(2)** if yes, find *every* place
the change must land. Do them in order — most user-facing changes stop at step 1.

> Scope: user-facing documentation lives under `docs/` (published to docs.dasch.swiss). This skill is
> **docs-only** — it does not cover the code, tests, or schemas your change also needs. Developer docs
> (`docs/developers/`) follow different rules, noted at the end.

---

## Step 1 — Does this change need docs at all?

**User-facing does NOT mean documented. The default is "no docs change." We do not want to bloat the
docs.** Only update docs when the change alters something a user must *know to model or use the tool
correctly*.

**Needs a docs update:**

- The **set of commands** and what each is *for* (not every flag).
- The **JSON project-definition format** — a new/changed value type, gui_element, property, or section.
- The **XML data-file format** — a new/changed element, attribute, or rule.
- The **public `xmllib` API** — a new/changed public function or method (via its docstring; see below).
- The **domain vocabulary users choose from** — permissions, licenses, value types, gui_elements.

**Does NOT need a docs update (user-facing, but leave the docs alone):**

- A new/changed **CLI flag** — flags are **not** listed exhaustively.
- An internal behavior improvement with the **same user-visible contract**.
- Performance work, refactors, error-message wording tweaks.
- A **bugfix** that restores already-documented intended behavior.
    - **Exception:** if the docs described the *old, buggy* behavior, fix the docs to match reality.

If the answer is "no", stop here. If "yes", go to Step 2.

---

## Step 2 — Where does it land?

First check the **worked examples** below for the common recurring changes. If none matches, use the
**Directory Overview** to pick the docs area(s) your change touches.

### How to write it (the one editorial rule)

User-facing pages (**everything except `docs/developers/`**) describe **what the user experiences** — the
behavior, the format, the choices they make. They do **not** explain the internal mechanism. If a
sentence you are about to write explains *how it works under the hood*, it belongs in `docs/developers/`
or nowhere.

### Worked example — a new (or changed) value type

The `RegionPreviewValue` case. A value type surfaces in the ontology, in the XML data file, and in xmllib.

- [ ] `docs/data-model/json-project/ontologies.md` — **three spots**:
    - [ ] If a new base property is introduced (e.g. `hasRegionPreview`): add it to the
      "following DSP base properties are available" list.
    - [ ] Add a row to the `hasValue | <Object> | <gui_element>` table.
    - [ ] Add the `#### <NewValue>` object-type section: description, `"object": "<NewValue>"`, a
      *gui_elements* list, and a JSON `Example`. **← the spot that was missed for `RegionPreviewValue`.**
- [ ] `docs/data-file/xml-data-file.md` — add a `### <new-prop>` section: the element, its attributes,
  its constraints, an XML example, and a cross-link to the ontology section. Document any child element
  too (e.g. `<region-preview>` inside `<region-preview-prop>`).
- [ ] `docs/data-model/json-project/caveats.md` — only if the value relates to a DSP base
  resource/property; update that resource's predefined-property list or description.
- [ ] Coupled: the allowed `object` / `gui_element` in `ontologies.md` must match the JSON schemas
  (`src/dsp_tools/resources/schema/project.json`, `properties-only.json`) and the XSD
  (`src/dsp_tools/resources/schema/data.xsd`). Keep the doc table in sync with them.

### Worked example — a new (or changed) CLI command

- [ ] `docs/index.md` — add/update a row in the "List of CLI Commands" table (**alphabetical**):
  command, one-line description + example, and a link to its doc section.
- [ ] The command's own doc page — the file matching its area:
    - data-model command → `docs/data-model/data-model-cli.md`
    - data-file command → `docs/data-file/data-file-commands.md`
    - workflow command → `docs/special-workflows/*.md`
    - stack command → `docs/local-stack.md`
- [ ] Coupled (outside `docs/`): add the page to the `mkdocs.yml` nav if it is new; update the
  "DSP-TOOLS provides the following functionalities" command list near the top of the root `CLAUDE.md`.

### Worked example — a new (or changed) public xmllib function

`docs/xmllib-docs/*` pages are **auto-generated** (each starts with a `::: xmllib.<module>` directive)
from code docstrings — so the "docs" are mostly in the code:

- [ ] Write a complete docstring on the function/method — it is **rendered verbatim on the site**.
- [ ] Export it in `src/dsp_tools/xmllib/__init__.py` — an unexported symbol will **not** appear.
- [ ] It then appears automatically on the matching page: a free function on
  `general-functions.md` / `value-checkers.md` / `value-converters.md` (per its module); a `Resource`
  method on `resource.md`; a method on an existing base-resource class (e.g. `RegionResource`,
  `VideoSegmentResource`) on its `dsp-base-resources/<name>.md` page.
- [ ] A new module/class needing its own page → create `docs/xmllib-docs/<name>.md` containing a single
  `::: xmllib.<module>` directive **and** add it to the `mkdocs.yml` nav.
- [ ] If it is a headline feature, also mention it in the hand-written `docs/xmllib-docs/overview.md`.

---

## Directory Overview (use when no worked example matches)

Top-level files:

- `index.md` — Landing page: install instructions, "Where To Start?", and the **full CLI command table**.
- `local-stack.md` — `start-stack` / `stop-stack` command docs.
- `permissions-guide.md` — Guide to DSP permissions.
- `changelog.md` — Only `{% include-markdown "../CHANGELOG.md" %}`. **Release-generated — never edit by hand.**

Directories:

- `assets/` — Non-prose assets: `images/` (screenshots), `data_model_templates/lists/` (Excel templates),
  `style/theme.css`.
- `data-file/` — The XML **data** file and the commands that consume it.
    - `xml-data-file.md` — **THE** XML data-file format reference: every `<*-prop>` value element, the
      base resources (`<region>`, …), permissions, value order.
    - `data-file-commands.md` — `xmlupload`, `validate-data`, `id2iri`, `resume-xmlupload`.
    - `excel2xml-module.md` — the deprecated `excel2xml` helper module.
- `data-model/` — The JSON project / data model and the commands that create it.
    - `data-model-cli.md` — `create`, `get`, `mapping config`, `mapping update`.
    - `excel2json.md` — `excel2json` / `excel2lists` / `excel2resources` / `excel2properties` (+ `old-*`).
    - `json-project/overview.md` — Structure of the JSON project file.
    - `json-project/ontologies.md` — **THE** ontology reference: base properties, the
      `hasValue | object | gui_element` table, and a `#### <ValueType>` section per value type.
    - `json-project/caveats.md` — Caveats about DSP base resources/properties (Region, LinkObj, …).
- `developers/` — Contributor/maintainer docs. **Exception to the editorial rule: these DO explain
  mechanism.** architecture/, code-quality-tools/, decision-log.md, index.md, mkdocs.md, packaging.md,
  start-stack.md, user-data.md.
- `special-workflows/` — Multi-step workflow guides: `workflow-xmlupload.md`
  (`upload-files` / `ingest-files` / `ingest-xmlupload`), `migration.md`, `update-legal.md`, `env-set-up.md`.
- `xmllib-docs/` — The `xmllib` Python API reference. **Almost every page is mkdocstrings-generated**
  (starts with `::: xmllib.<module>`) from **code docstrings** — edit the docstring and the
  `xmllib/__init__.py` exports, *not* the `.md` file. Hand-written exceptions: `overview.md`,
  `advanced-set-up.md`.

---

## Keep this skill current

When you add a **new directory under `docs/`**, add a line for it in the Directory Overview above. When a
new *kind* of user-facing change starts recurring, add a worked example for it.
