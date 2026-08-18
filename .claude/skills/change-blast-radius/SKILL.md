---
name: change-blast-radius
description: >-
  Use this skill during FEATURE WORK in dsp-tools to map a change's blast radius across the whole suite —
  the full list of places that must be touched — either before you start (planning) or against a drafted
  change (audit). Trigger it for "where do I need to change things for this feature", "I'm adding a field
  to the project JSON / data model", "I added a new value type / gui_element / section", "add a new CLI
  command or sub-command", "add an xmllib helper", "I changed the schema — what else needs updating?",
  "did I implement X everywhere?", "map the blast radius of this change", or "audit my change for missed
  subsystems". It reports the places only (read-only) and delegates the detailed work to other agents. Do
  NOT use it for small refactors, renames, performance tweaks, or code-quality-only edits that keep the
  same contract.
---

# Change Blast-Radius Playbook

This is the planning playbook for one question: **"I'm doing (feature) work — anywhere in dsp-tools, where
does this change have to touch?"** It exists because a change can reach almost every subsystem yet silently
miss one.

**This skill only *identifies* the places that must change.** It does not make the edits and does not
prescribe how to change each place — that is delegated to the developer and to other (sub-)agents.
It is **read-only**: it reads code and git history and reports; it never edits.

The ground-truth map of the suite lives in the repo's **`CONVENTIONS.md`** — the section *"dsp-tools
subsystem inventory (blast-radius reference)"*. That inventory is the single source of truth; this skill
drives the *analysis* against it so the walk-through happens for sure. When the inventory is wrong or
incomplete, fix it **there**, not here.

## When to use / when to skip

**Use it for feature work** — anything that adds or changes observable behaviour or a format: a new field,
a new value type, a new command or sub-command, a new section of the project file.
Run it **before** starting (to plan every place) or **after** drafting (to audit a diff for gaps).

**Skip it** for small refactors, performance tweaks, or code-quality-only edits that keep the same
user-visible and cross-module contract — these have no cross-suite blast radius worth mapping.

## Phase 1 — Gate

Confirm this is feature work. If it is a pure refactor / code-quality change with an unchanged contract,
stop and say so. Otherwise, continue.

## Phase 2 — Classify

Pick the playbook that fits. Infer the change from the working-tree diff if one exists, otherwise from the
described intent:

- **(A) JSON project-definition change** — a new/changed field, attribute, `gui_element`, or section of the
  JSON project file (the `data_license` archetype).
- **(B) XML data-file change** — a new/changed element, attribute, or rule of the XML data file.
- **(C) Generic** — anything else (new command/sub-command, new client, new `xmllib` helper, …). Walk the
  inventory directly.

A change can be both **A** and **B** — run both checklists.

## Phase 3 — Trace (sub-agent fan-out)

This is classic sub-agent work. Fan out read-only Explore sub-agents **in parallel** to locate every touch
point in **live code** — do not trust this document's paths blindly; the code moves. Give each agent:

1. the chosen playbook's checklist (below) plus the `CONVENTIONS.md` inventory, and
2. **one or two precedent siblings to trace** — grep an existing, analogous thing across the whole repo and
   use its locations as a checklist.

Trace **two** precedents and union their locations, because a single precedent can carry its own blind
spot.

## Phase 4 — Report (hard stop)

Return one consolidated table, then stop. Do **not** implement.

| Touch point | Anchor file(s) | Applies? | Status | Note |
|-------------|----------------|----------|--------|------|

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

## Playbook A — JSON project-definition change

The project and ontology checklist (verify each against live code in Phase 3):

- [ ] **Schema** — `src/dsp_tools/resources/schema/project.json` (and `properties-only.json` /
  `resources-only.json` / `lists-only.json` if the field lives in one of those sections). Model a fixed
  value set as an `enum`; give an IRI-valued field a `pattern` (see `CONVENTIONS.md`).
- [ ] **create** — parse in `commands/create/parsing/parse_project.py`; model in
  `commands/create/models/parsed_project.py`; serialise in `commands/create/serialisation/project.py`; send
  in `commands/create/create_on_server/project.py` (mind the project-create payload vs. the separate
  `LegalInfoClient` path — `data_license` goes via legal-info, `enabled_licenses` via the create payload).
- [ ] **get** (round-trip) — `commands/get/legacy_models/project.py` (`fromJsonObj` +
  `createDefinitionFileObj`); permissions via `commands/get/get_permissions.py`.
- [ ] **excel2json — the historically missed spot.** Update `commands/excel2json/models/json_header.py`
  (the `Project` dataclass + `to_dict()`), `commands/excel2json/json_header.py` (`_check_project_sheet` /
  `_extract_project`), and the `ordered_keys` list in `_sort_project_dict` (`commands/excel2json/project.py`)
  — which **raises `UnreachableCodeError` on any key it does not know**, so a field added everywhere else
  errors *here* at runtime. Follow the "Column Processing Pattern" in `commands/excel2json/CLAUDE.md`.
- [ ] **validate-data** — only if the field drives SHACL (as `enabled_licenses` does):
  `commands/validate_data/prepare_data/`, `commands/validate_data/models/api_responses.py`,
  `commands/validate_data/sparql/construct_shacl.py` / `legal_info_shacl.py`. A new RDF-mapped property must
  be threaded through the pipeline (see `CONVENTIONS.md`). **Authoring a shape? run the `add-shacl-shape`
  skill.**
- [ ] **docs** — **run the `update-docs` skill**; do not decide docs here.
- [ ] **tests + test data** — prefer extending the systematic project
  (`testdata/json-project/systematic-project-4123.json`); register new shortcodes/shortnames in
  `testdata/USED_SHORTCODE_SHORTNAMES.md`; add unit + integration + e2e coverage (mind the e2e three-place
  wiring, see `CONVENTIONS.md`).
- [ ] **external** — `0854-daschland-scripts` companion-PR flag (create / excel2json / xmllib touched → see
  Phase 4).

## Playbook B — XML data-file change

The data side of the same fan-out. Checklist:

- [ ] **Schema** — `src/dsp_tools/resources/schema/data.xsd`.
- [ ] **XML parsing** — `utils/xml_parsing/get_parsed_resources.py`,
  `utils/xml_parsing/models/parsed_resource.py`.
- [ ] **xmlupload** — `commands/xmlupload/` (`make_rdf_graph/`, `models/processed/`, `prepare_xml_input/`,
  `xmlupload.py`).
- [ ] **validate-data** — the SHACL side: `commands/validate_data/prepare_data/get_rdf_like_data.py`,
  `mappers.py`, `models/rdf_like_data.py`, `resources/validate_data/api-shapes.ttl`. **Authoring a shape?
  run the `add-shacl-shape` skill.**
- [ ] **xmllib** — public API + serialisation: `xmllib/__init__.py`,
  `xmllib/internal/serialise_resource.py`, `xmllib/models/`.
- [ ] **docs** — **run the `update-docs` skill** (`docs/data-file/xml-data-file.md`).
- [ ] **tests + test data** — extend the systematic XML
  (`testdata/xml-data/test-data-systematic-4123.xml`); a `validate-data` change needs **both** a conforming
  and a violating case; add unit + integration + e2e coverage.
- [ ] **external** — `0854-daschland-scripts` companion-PR flag (xmlupload / xmllib touched → see Phase 4).

## Playbook C — Generic

For change kinds not laid out above, walk the `CONVENTIONS.md` inventory subsystem-by-subsystem and trace
the nearest precedent (e.g. an existing command when adding a command). Worked hint for a **new CLI
(sub)command** — the most common recurring case:

- [ ] **cli — the three-place wiring:** `cli/create_parsers.py` (argparse), `cli/call_action.py` (dispatch),
  and `cli/call_action_files_only.py` (thin wrapper, for file-only commands).
- [ ] **docs** — run the `update-docs` skill (the command table in `docs/index.md`, the command's own page,
  the `mkdocs.yml` nav, and the command list near the top of the root `CLAUDE.md`).
- [ ] **tests** — unit + e2e; a new e2e suite needs the **three-place wiring** (test dir under
  `test/e2e/commands/`, a `just e2e-test-<command>` recipe, and a job in `.github/workflows/tests-e2e.yml`),
  or it silently never runs.
- [ ] **external** — flag `0854-daschland-scripts` if the change touches `xmllib` / `create` / `excel2json`
  / `xmlupload` (see Phase 4).

---

## Keep this skill current

- When a **new kind of feature-work change** starts recurring, add a playbook or a worked hint for it here.
- When the suite **gains, moves, or renames a subsystem**, update the inventory in `CONVENTIONS.md` (the
  single source of truth) — not this file. This skill points at the inventory; it does not duplicate it.
