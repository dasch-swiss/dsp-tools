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
- Comments describe the code as it is, not how it evolved — no references to refactors or "recently changed".
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

- `CLAUDE.md` — repository overview, commands, architecture, working agreements.
- `src/dsp_tools/utils/CLAUDE.md` — utils-vs-commands boundary rules.
- `src/dsp_tools/commands/create/CLAUDE.md` — the `create` pipeline in detail.
- `src/dsp_tools/xmllib/CLAUDE.md` — xmllib public-API layering.
- `docs/developers/` — developer documentation (mkdocs).
- `docs/developers/architecture/error-handling.md` — exception hierarchy and catch-vs-fail rules.
- `testdata/USED_SHORTCODE_SHORTNAMES.md` — the shortcode/shortname register.
