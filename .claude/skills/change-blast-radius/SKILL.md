---
name: change-blast-radius
description: >-
  Maps a feature change's blast radius across dsp-tools and reports every place that must be touched — the
  full list of subsystems, before you start (planning) or against a drafted change (audit). Read-only: it
  identifies the places and delegates the actual edits to the developer and to other agents.
when_to_use: >-
  Trigger it for "where do I need to change things for this feature", "I'm adding a field to the project
  JSON / data model", "I added a new value type / gui_element / section", "add a new CLI command or
  sub-command", "add an xmllib helper", "I changed the schema, what else needs updating?", "did I implement
  X everywhere?", "map the blast radius of this change", or "audit my change for missed subsystems". Not for
  small refactors, renames, performance tweaks, or code-quality-only edits that keep the same contract.
context: fork
agent: general-purpose
background: false
argument-hint: "[change-description]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent(Explore)
  - Bash(git diff:*)
  - Bash(git status:*)
  - Bash(git show:*)
  - Bash(git log:*)
disallowed-tools: Edit, Write, NotebookEdit
---

# Change Blast-Radius Playbook

This is the planning playbook for one question: **"I'm doing (feature) work — anywhere in dsp-tools, where
does this change have to touch?"** It exists because a change can reach almost every subsystem yet silently
miss one.

**This skill only *identifies* the places that must change.** It does not make the edits and does not
prescribe how to change each place — that is delegated to the developer and to other (sub-)agents.
It is **read-only** — it reads code and git history and reports; it never edits. The frontmatter enforces
this: `disallowed-tools` removes the edit tools from the pool.

This skill runs **forked**, isolated from the agent that invokes it: it receives the change to analyse as an
argument (and/or reads it from the working-tree diff), does the whole analysis in its own context, and
returns only the final report. It does **not** see the invoking conversation's history.

## Sources of truth

The **subsystem list** — which subsystems exist and how they connect — is the single source of truth in the
repo's **`CONVENTIONS.md`**, section *"dsp-tools subsystem inventory"*. This skill drives the *analysis*
against that inventory so the walk-through happens for sure. When a subsystem is added, moved, or renamed,
fix it **there**, not here.

The **leaf-path hints** in the playbooks below (the specific files within each subsystem) live **here** —
the inventory stops at directories and pipelines and does not carry them. They are hints, not gospel:
Phase 3 re-verifies every one against live code, because the code moves.

## When to use / when to skip

**Use it for feature work** — anything that adds or changes observable behaviour or a format: a new field,
a new value type, a new command or sub-command, a new section of the project file.
Run it **before** starting (to plan every place) or **after** drafting (to audit a diff for gaps).

**Skip it** for small refactors, performance tweaks, or code-quality-only edits that keep the same
user-visible and cross-module contract — these have no cross-suite blast radius worth mapping.

## Phase 1: Gate

Confirm this is feature work. If it is a pure refactor / code-quality change with an unchanged contract,
stop and say so. Otherwise, continue.

## Phase 2: Classify

Pick the playbook that fits. Derive the change from **`$ARGUMENTS`** (the change description the invoking
agent passes) and/or from the **working-tree diff** if one exists (`git diff`). Because the skill runs
forked, it cannot see the conversation history — the change description arrives as the argument.

- **(A) JSON project-definition change** — a new/changed field, attribute, `gui_element`, or section of the
  JSON project file (the `data_license` archetype).
- **(B) XML data-file change** — a new/changed element, attribute, or rule of the XML data file.
- **(C) Generic** — anything else (new command/sub-command, new client, …). Walk the inventory directly.

A change can be both **A** and **B** — run both checklists. In particular, **a new value type is an
A + B + xmllib case**: run Playbook A *and* Playbook B, including the `xmllib` row — do not let it fall into
the generic Playbook C.

## Phase 3: Trace (sub-agent fan-out)

This is classic sub-agent work. Fan out read-only Explore sub-agents **in parallel** to locate every touch
point in **live code** — do not trust this document's paths blindly; the code moves.

**Count:** run **one Explore agent per precedent per applicable playbook**. Trace **two** precedents per
playbook and union their locations, because a single precedent can carry its own blind spot — so 2 agents
for one playbook, up to 4 when the change is both A and B.

Give each agent:

1. the chosen playbook's checklist (below) plus the `CONVENTIONS.md` inventory, and
2. **one precedent sibling to trace** — grep an existing, analogous thing across the whole repo and use its
   locations as a checklist.

**Return contract:** each agent returns a **path list** (touch point → file path), not prose.

## Phase 4: Report

Return one consolidated table. **This invocation ends with the report** — it does not implement. If the user
then asks for the edits, that is a separate task.

`Status` is one of **`TODO`** (planning; place not yet touched), **`done`** / **`MISSING`** (verify mode,
read off the diff), or **`n/a`** (touch point does not apply to this change).

| Touch point                   | Anchor file(s)                                 | Status  | Note                                                                                    |
|-------------------------------|------------------------------------------------|---------|-----------------------------------------------------------------------------------------|
| excel2json ordered-keys check | `src/dsp_tools/commands/excel2json/project.py` | MISSING | new field missing from the ordered-keys list → raises `UnreachableCodeError` at runtime |

- **Planning mode** (no change yet): every applicable touch point is `TODO`.
- **Verify mode** (a diff exists): mark each row `done` / `MISSING` / `n/a` by checking the diff
  (`git diff`, `git status`, `git show`). List the `MISSING` rows first.
- **External / separate PR:** if the touched subsystems include **`xmllib`, `excel2json`, `create`, or
  `xmlupload`**, append a clearly-marked row for the demo importer **`0854-daschland-scripts`**
  (<https://github.com/dasch-swiss/0854-daschland-scripts>). It depends on `dsp-tools` and the public
  `xmllib` API and has its own project JSON + generated XML output, so it may need a **companion PR in that
  separate repo**. **Flag it only** (with the URL); do **not** trace it. Do **not** flag it for
  validate-data-only changes — `validate-data` inspects data, it does not change how data is produced.
- Hand each `TODO` / `MISSING` place to the developer or a follow-up agent for the actual edit.

---

> Paths below are given from the repo root: source files under `src/dsp_tools/…`, test data under
> `testdata/…`. Phase 3 re-verifies each against live code.

## Playbook A — JSON project-definition change

The project and ontology checklist (verify each against live code in Phase 3):

- [ ] **Schema** — `src/dsp_tools/resources/schema/project.json` (and `properties-only.json` /
  `resources-only.json` / `lists-only.json` if the field lives in one of those sections). Model a fixed
  value set as an `enum`; give an IRI-valued field a `pattern` (see `CONVENTIONS.md`).
- [ ] **create** — parse in `src/dsp_tools/commands/create/parsing/parse_project.py`; model in
  `src/dsp_tools/commands/create/models/parsed_project.py`; serialise in
  `src/dsp_tools/commands/create/serialisation/project.py`; send in
  `src/dsp_tools/commands/create/create_on_server/project.py` (mind the project-create payload vs. the
  separate legal-info path — `data_license` goes via legal-info, `enabled_licenses` via the create payload).
- [ ] **get** (round-trip) — `src/dsp_tools/commands/get/legacy_models/project.py`; permissions via
  `src/dsp_tools/commands/get/get_permissions.py`.
- [ ] **excel2json — the historically missed spot.** Update
  `src/dsp_tools/commands/excel2json/models/json_header.py`,
  `src/dsp_tools/commands/excel2json/json_header.py`, and `src/dsp_tools/commands/excel2json/project.py` —
  where the ordered-keys check **raises `UnreachableCodeError` on any key it does not know**, so a field
  added everywhere else errors *here* at runtime. Follow the "Column Processing Pattern" in
  `src/dsp_tools/commands/excel2json/CLAUDE.md`.
- [ ] **validate-data** — only if the field drives SHACL (as `enabled_licenses` does):
  `src/dsp_tools/commands/validate_data/prepare_data/`,
  `src/dsp_tools/commands/validate_data/models/api_responses.py`,
  `src/dsp_tools/commands/validate_data/sparql/construct_shacl.py` / `legal_info_shacl.py`. A new
  RDF-mapped property must be threaded through the pipeline (see `CONVENTIONS.md`). **Authoring a shape? run
  the `add-shacl-shape` skill.**
- [ ] **docs** — **run the `update-docs` skill**; do not decide docs here.
- [ ] **tests + test data** — prefer extending the systematic project
  (`testdata/json-project/systematic-project-4123.json`); register new shortcodes/shortnames in
  `testdata/USED_SHORTCODE_SHORTNAMES.md`; add unit + integration + e2e coverage (mind the e2e three-place
  wiring, see `CONVENTIONS.md`).
- [ ] **external** — `0854-daschland-scripts` companion-PR flag (see Phase 4).

## Playbook B — XML data-file change

The data side of the same fan-out. Checklist:

- [ ] **Schema** — `src/dsp_tools/resources/schema/data.xsd`.
- [ ] **XML parsing** — `src/dsp_tools/utils/xml_parsing/get_parsed_resources.py`,
  `src/dsp_tools/utils/xml_parsing/models/parsed_resource.py`.
- [ ] **xmlupload** — `src/dsp_tools/commands/xmlupload/` (`make_rdf_graph/`, `models/processed/`,
  `prepare_xml_input/`, `xmlupload.py`).
- [ ] **validate-data** — the SHACL side:
  `src/dsp_tools/commands/validate_data/prepare_data/get_rdf_like_data.py`,
  `src/dsp_tools/commands/validate_data/mappers.py`,
  `src/dsp_tools/commands/validate_data/models/rdf_like_data.py`,
  `src/dsp_tools/resources/validate_data/api-shapes.ttl`. **Authoring a shape?
  run the `add-shacl-shape` skill.**
- [ ] **xmllib** — public API + serialisation: `src/dsp_tools/xmllib/__init__.py`,
  `src/dsp_tools/xmllib/internal/serialise_resource.py`, `src/dsp_tools/xmllib/models/`.
- [ ] **docs** — **run the `update-docs` skill** (`docs/data-file/xml-data-file.md`).
- [ ] **tests + test data** — extend the systematic XML
  (`testdata/xml-data/test-data-systematic-4123.xml`); a `validate-data` change needs **both** a conforming
  and a violating case; add unit + integration + e2e coverage.
- [ ] **external** — `0854-daschland-scripts` companion-PR flag (see Phase 4).

## Playbook C — Generic

For change kinds not laid out above, walk the `CONVENTIONS.md` inventory subsystem-by-subsystem and trace
the nearest precedent (e.g. an existing command when adding a command). Worked hint for a **new CLI
(sub)command** — the most common recurring case:

- [ ] **cli — the three-place wiring:** `src/dsp_tools/cli/create_parsers.py` (argparse),
  `src/dsp_tools/cli/call_action.py` (dispatch), and `src/dsp_tools/cli/call_action_files_only.py` (thin
  wrapper, for file-only commands).
- [ ] **docs** — run the `update-docs` skill (the command table in `docs/index.md`, the command's own page,
  the `mkdocs.yml` nav, and the command list near the top of the root `CLAUDE.md`).
- [ ] **tests** — unit + e2e; a new e2e suite needs the **three-place wiring** (test dir under
  `test/e2e/commands/`, a `just e2e-test-<command>` recipe, and a job in `.github/workflows/tests-e2e.yml`),
  or it silently never runs.
- [ ] **external** — `0854-daschland-scripts` companion-PR flag (see Phase 4).

---

## Error handling

| Failure                                                                | Response                                                                                                                                                            |
|------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| The `CONVENTIONS.md` subsystem-inventory section is missing or renamed | Proceed with the three playbooks below (they still hold) and report the missing/renamed inventory so it gets fixed. Do not reconstruct the full map from this file. |
| No change description (`$ARGUMENTS` empty) and no working-tree diff    | Return a one-line report asking to re-invoke with the change description — a forked sub-agent cannot prompt the user.                                               |
| Verify mode requested but no working-tree diff exists                  | Fall back to planning mode (every touch point `TODO`) and say so; do not invent a diff to audit.                                                                    |
| A Phase 3 precedent grep returns nothing                               | Widen the search or pick a different precedent; do not conclude there are zero touch points.                                                                        |
| A fan-out sub-agent returns empty or dies                              | Note the gap in the report and re-run or trace that playbook manually; never silently drop a touch point.                                                           |

---

## Keep this skill current

- When a **new kind of feature-work change** starts recurring, add a playbook or a worked hint for it here.
- When the suite **gains, moves, or renames a subsystem**, update the inventory in `CONVENTIONS.md` (the
  single source of truth for the subsystem list) — not this file.
- When a **leaf path** in a playbook goes stale (a file moves or is renamed), fix it **here** — the
  playbooks own the leaf-path hints, and Phase 3 re-verifies them against live code on every run.
