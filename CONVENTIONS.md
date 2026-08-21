# Conventions

Agent reference card for the **work phase**. Pair with `REVIEW.md` (review phase).
Authoritative detail lives in `CLAUDE.md` and the per-module `CLAUDE.md` files under `src/dsp_tools/`;
developer docs live in `docs/developers/`. This card collects the conventions that are otherwise
only enforced in review.

## Stack

Python 3.12+, `uv` for environments and dependencies, `just` as task runner. CLI tool that talks to the
DSP-API (a remote/local Scala service). Linting: `ruff` (format + check), `mypy` (strict),
`yamllint`/`yamlfmt`, `markdownlint`, `darglint` (Google-style docstrings), `vulture`. Tests: `pytest`
(unit / integration / e2e with testcontainers). Line length: 120.

## Code Conventions

### Functions over stateful classes

- Prefer **stateless functions** for behaviour. Use classes only to bundle data, via `@dataclass`.
- Do not write classes that carry both a lot of state and behaviour.
- Utilities (`src/dsp_tools/utils/`) are stateless with clear input/output contracts.

### Module boundaries

- **Commands never import from other commands.** Shared logic goes to `src/dsp_tools/utils/`;
  shared HTTP-route interaction goes to `src/dsp_tools/clients/`. See `src/dsp_tools/utils/CLAUDE.md`.
- HTTP clients (`clients/`) are generic and reusable, and contain **no retry logic** (that lives in
  `utils/request_utils.py`).
- Never make raw HTTP requests — always go through `utils/request_utils.py` for consistent logging,
  sanitisation, error handling, and retries.
- **xmllib is the public API** for programmatic XML creation (see `src/dsp_tools/xmllib/CLAUDE.md`).
  It must not import dsp-tools internals and does not know the JSON project file — dependencies point
  from dsp-tools *into* xmllib, never the other way.
- **User-facing docs and docstrings do not cite xmllib internals** — describe user input in the user's
  terms (XML elements, JSON fields), not in terms of library code.
- **New RDF-mapped properties must be threaded through the validate-data pipeline**
  (`get_rdf_like_data()` → property type → SHACL shape in
  `src/dsp_tools/resources/validate_data/api-shapes.ttl`). The generic resource shape is closed: a new
  property needs an explicit cardinality declaration or xmlupload fails validation.

### Types and paths

- All new code is fully type-annotated (mypy runs strict). Run `just mypy`; use `dmypy restart` if it misbehaves.
- Always use `pathlib.Path`, never `os.path`, and never pass paths around as strings.
- Use modern Python syntax and patterns.

### Naming and comments

- Names are **evergreen**: never `new`/`improved`/`enhanced`. What is new today is old tomorrow.
  This holds in prose as much as in identifiers: a format or workflow called "the new format" carries
  a name that expires the day the migration ends. Name what it *is* — `text-property-based`,
  `attribute-based`.
- Comments are **evergreen** too, in all formats, and in `docs/` prose. State what the code does and
  why it must be that way, as a standing fact; never describe a change, an incident, or a previous state.
    - The test: **can a reader holding only this file tell whether the comment is still true?**
      A historical claim is true only against a baseline that is not written down, so when the baseline
      moves the comment turns **false** rather than merely obscure, and nothing flags it. Agents compound
      this — they read comments as directives, so `the important one` becomes a ranking nobody decided.
    - Grep for `no longer`, `used to`, `previously`, `formerly`, `recently`, `anymore`, `at the moment`,
      `currently`, `we changed/switched/moved`, `until now`, `new in`, `the old/new <thing>`,
      `the important one`, and incidents/releases cited as the reason for a setting. These are
      candidates, not verdicts — apply the test. Three kinds pass it routinely: `used to` meaning
      *employed to* ("a parser used to parse the arguments"); a marker whose baseline **is** written
      down nearby (`xmllib-docs/advanced-set-up.md` says warnings are no longer printed, directly
      beneath the `.env` snippet that causes it); and `now`/`currently`/`before` describing execution
      order or live server state, where the baseline is the program state.
    - **Claims about the outside world take a date, not the present tense** — another service, a
      third-party library, another team's product. No phrasing makes these checkable from this file, so
      give them a date or a link to the authority that settles them. An undated `currently` is the worst
      option: it looks current and cannot be verified.
      `docs/developers/code-quality-tools/python-see-also.md` ("As of mid-2023, …") is the form to copy,
      not to repair.
    - **Rewrite, don't delete** — the rationale is the valuable half. But flipping the tense is not the
      fix and often yields a false statement: `used to fail the whole run` → `fails the whole run` is
      simply wrong, because the setting being documented is what prevents it. Restate *why the code has
      to be this way*: *"we switched to a set because the list lookup was too slow"* →
      *"a set, not a list: membership is checked once per row, so a linear lookup is too slow here"*.
      Where the reason genuinely **is** a past event (a compatibility shim, a workaround kept for old
      servers), state the durable consequence and add a followable pointer — `see #1787`. That is not
      the same as citing an incident *instead of* a reason that was statable in the present tense; the
      ban above is on the substitution, not on the pointer.
- Docstrings (Google-style) only for high-level functions or where the name cannot carry the intent.
  Lower-level and test functions are self-explanatory and need none.
- **`default_*` prefix** marks a **project-wide value that can be overridden per resource**
  (precedent: `default_permissions`, `default_data_authorship`). A field that applies directly and cannot
  be overridden does not take the prefix. These names are cross-repo API (JSON project files, XML uploads,
  dsp-api payload keys) — get them right before merging; renaming afterwards is a breaking change.
- "Default" does **not** imply auto-application. If a `default_*` value is only a suggestion in some flows
  (e.g. not applied during `xmlupload`), say so explicitly in the user docs of every feature that touches it.

### Dependencies

- Never `pip install` globally. Add deps with `uv add <pkg>` (or `uv add --dev <pkg>`); install with
  `uv sync --all-extras --dev`.

### JSON Schema (project definition)

- The project-definition schema is `src/dsp_tools/resources/schema/project.json`.
- When a field accepts only a **fixed, known set of values**, model it as an `enum` (not a free `string` or
  a loose `pattern`) so validation fails client-side with an actionable message. Hard requirement, not a
  style choice.
- **IRI-valued fields get a `pattern`** even when not enumerable
  (precedent: `enabled_licenses` in `src/dsp_tools/resources/schema/project.json`).

## dsp-tools subsystem inventory (blast-radius reference)

The map of the whole suite: when you do **feature work**, a change usually has to fan out across several of
these subsystems. Use the **`change-blast-radius`** skill to walk this inventory against your change —
before you start (to plan) or against a drafted diff (to audit) — so nothing is silently missed, the way
`excel2json` was missed when `data_license` was added. This table is the single source of truth the skill
and reviewers reuse; keep it current when a subsystem is added, moved, or renamed.

| Subsystem | Path | Role & cross-cutting wiring |
| --- | --- | --- |
| CLI | `src/dsp_tools/cli/` | Command wiring in **three places**: `create_parsers.py` (argparse), `call_action.py` (dispatch), `call_action_files_only.py` (thin file-only wrappers). A new command touches all three. |
| clients | `src/dsp_tools/clients/` | Generic, reusable HTTP clients (no retry logic). |
| create | `src/dsp_tools/commands/create/` | JSON project file → server. Pipeline `parsing/` → `models/` → `serialisation/` → `create_on_server/`. Legal metadata (`data_license`, …) is sent via `LegalInfoClient`; `enabled_licenses` via the create payload. |
| get | `src/dsp_tools/commands/get/` | Server → JSON project file (round-trip). Project modelling in `legacy_models/project.py`; permissions in `get_permissions.py`. **No `get/CLAUDE.md` exists.** |
| excel2json | `src/dsp_tools/commands/excel2json/` | Excel → JSON project file. Project metadata in `models/json_header.py` + `json_header.py`. **`_sort_project_dict` in `project.py` raises `UnreachableCodeError` on any key not in its `ordered_keys` list** — a new top-level field must be added there or it errors at runtime. This is where `data_license` was missed. See `excel2json/CLAUDE.md` ("Column Processing Pattern"). |
| validate-data | `src/dsp_tools/commands/validate_data/` | SHACL validation before upload. New RDF-mapped properties must be threaded through the pipeline and get an explicit cardinality in `resources/validate_data/api-shapes.ttl`. Adding a shape → use the `add-shacl-shape` skill. |
| xmlupload | `src/dsp_tools/commands/xmlupload/` | XML data → server. `make_rdf_graph/`, `models/processed/`, `prepare_xml_input/`, `xmlupload.py`. |
| other commands | `src/dsp_tools/commands/` | `id2iri`, `update_legal`, `mapping`, `start_stack` / `stop_stack`. |
| xmllib (public API) | `src/dsp_tools/xmllib/` | Public library for programmatic XML creation. Must not import dsp-tools internals; exports live in `xmllib/__init__.py`. |
| utils / xml parsing | `src/dsp_tools/utils/` | Shared stateless helpers; XML parsing in `utils/xml_parsing/`. All HTTP goes through `utils/request_utils.py`. |
| schema | `src/dsp_tools/resources/schema/` | `project.json`, `properties-only.json`, `resources-only.json`, `lists-only.json` (project definition) and `data.xsd` (XML data file). |
| docs | `docs/` | User-facing docs (mkdocs). Whether and where to update them is gated by the **`update-docs`** skill. |
| test data + tests | `testdata/`, `test/` | `test/unittests`, `test/integration`, `test/e2e`, `test/legacy_e2e`. Prefer extending the systematic project/XML over new fixtures; register shortcodes in `testdata/USED_SHORTCODE_SHORTNAMES.md`. E2E needs the **three-place wiring** (test dir + `just` recipe + `tests-e2e.yml` job). |
| external: `0854-daschland-scripts` | <https://github.com/dasch-swiss/0854-daschland-scripts> | DaSCH's **demo importer** (separate repo → separate PR). Depends on `dsp-tools` + the public `xmllib` API, with its own project ontology + generated XML. May need a companion PR when a change touches **`xmllib`, `excel2json`, `create`, or `xmlupload`** — **not** for validate-data-only changes. `change-blast-radius` flags it only; it does not trace it. |

The recurring cross-cutting rules that go with this map — the **e2e three-place wiring**, the JSON-schema
**`enum`/`pattern`** rules, the **`default_*` prefix**, and **RDF-mapped property → validate-data**
threading — are detailed in the sections above and under "Testing Conventions" below.

## Testing Conventions

- **Every feature is tested.** Logic (parsers, serialisers, mappers, validators) gets unit tests;
  user-facing behaviour gets an integration/E2E round-trip. "It compiles / runs" is not coverage.
- Assertions are bare — no custom messages. Pytest reports enough on failure.
  Correct: `assert "id" in nodes[0]`. Incorrect: `assert "id" in nodes[0], f"..."`.
- **RDF-graph tests assert the *whole* graph, not just the triple under test.** When a test builds a graph
  (e.g. `_add_one_resource`, `_make_resource`), assert every triple that should be present (type, label,
  `attachedToProject`, the value(s) …) — asserting only the one new triple hides regressions in the rest.
- Test locations: unit → `test/unittests/`; integration → `test/integration/`; E2E (testcontainers) →
  `test/e2e/`; legacy E2E (needs a running stack) → `test/legacy_e2e/`.

### Test data (`testdata/`)

- **Prefer extending the systematic test data over adding a new project file.** The systematic project
  (`testdata/json-project/systematic-project-4123.json` + `testdata/xml-data/test-data-systematic-4123.xml`)
  is meant to exercise *all* features. Add a new feature there rather than creating a dedicated
  `feature-XXXX.json/.xml`, to avoid an abundance of near-duplicate test files.
- **Shortcodes and shortnames are registered.** Every project shortcode/shortname used in e2e test data is
  listed in `testdata/USED_SHORTCODE_SHORTNAMES.md`; they must be unique. Add an entry when you introduce one,
  and follow the file-naming convention recorded there:
    - project JSON: `[shortname]-project-[shortcode].json`
    - XML data: `[free-to-choose]-[shortcode].xml`
    - invalid-project shortcodes start with `F`.
- **`validate-data` test data covers all paths — happy *and* error.** For a validation feature, add both a
  conforming case and a violating case (see the `*_correct.xml` / `*_violation.xml` pairs under
  `testdata/validate-data/core_validation/`).

### E2E wiring

- **E2E tests are not auto-discovered by CI.** Each e2e command suite is wired explicitly in three places:
  a test directory under `test/e2e/commands/`, a `just e2e-test-<command>` recipe in the `justfile`, and a
  matching job in `.github/workflows/tests-e2e.yml`. A new e2e test not registered in all three silently
  never runs.
- **One `just` e2e recipe per test file / logical group** — do not append an unrelated test file to an
  existing recipe. Isolated recipes make it possible to re-run just the failing suite.
- **A new GitHub workflow is not a required check automatically.** Adding a workflow only makes it run; it
  does not gate merging. A repo admin must mark it as a required status check in the repo settings (branch
  protection / rulesets). Agents and tools cannot change repo settings — flag this step to the user when
  adding a workflow.

## Commit Conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/), enforced by the "Check PR Title"
workflow — check recent `git log` for the prevailing style. Common prefixes in this repo: `feat:`, `fix:`,
`chore:`, `docs:`, `test:`, `refactor:`, `build:`. Breaking changes use `!`.

## Before committing

- `just lint` (ruff check + ruff format check + yamllint + markdownlint) is clean.
- `just mypy` is clean.
- Relevant tests pass (`just unittests` / `just integration-tests` / `just e2e-tests`).
- All markdown complies with `.markdownlint.yml`.
- Update the relevant `CLAUDE.md` (root and/or per-module) when behaviour or structure changes, and update
  `CONVENTIONS.md` / `REVIEW.md` when a convention itself changes.

## Where to go for depth

- **"dsp-tools subsystem inventory (blast-radius reference)"** (this file) — the cross-suite touch-point
  map; walk it with the `change-blast-radius` skill on any feature work.
- `CLAUDE.md` — repository overview, commands, architecture, working agreements.
- `src/dsp_tools/utils/CLAUDE.md` — utils-vs-commands boundary rules.
- `src/dsp_tools/commands/create/CLAUDE.md` — the `create` pipeline in detail.
- `src/dsp_tools/xmllib/CLAUDE.md` — xmllib public-API layering.
- `docs/developers/` — developer documentation (mkdocs).
- `docs/developers/architecture/error-handling.md` — exception hierarchy and catch-vs-fail rules.
- `testdata/USED_SHORTCODE_SHORTNAMES.md` — the shortcode/shortname register.
