# Conventions

Agent reference card for the **work phase**. Pair with `REVIEW.md` (review phase).
Detailed developer docs live in `docs/developers/`; module-specific guidance in `CLAUDE.md`
and `src/dsp_tools/xmllib/CLAUDE.md`. This card collects the conventions that are otherwise
only enforced in review.

## Stack

Python 3.12+, `uv` for environments and dependencies, `just` as command runner.
Linting: `ruff` (format + check), `mypy` (strict), `yamllint`/`yamlfmt`, `markdownlint`,
`darglint` (Google-style docstrings), `vulture`. Tests: `pytest` (unit / integration / e2e
with testcontainers). Line length: 120.

## Naming

- **`default_*` prefix** marks a **project-wide value that can be overridden per resource**
  (precedent: `default_permissions`, `default_data_authorship`). A field that applies directly
  and cannot be overridden does not take the prefix. Get this right before merging — these names
  are cross-repo API (JSON project files, XML uploads, dsp-api payload keys); the initial
  `data_authorship` had to be renamed across four repositories after merge.
- "Default" does **not** imply auto-application. If a `default_*` value is only a suggestion in
  some flows (e.g. not applied during `xmlupload`), say so explicitly in the user docs of every
  feature that touches it.

## JSON schemas

- **Restricted-value fields are enums, not free strings.** If only a fixed set of values is
  allowed (e.g. a set of license IRIs), model it as an `enum` in the JSON schema so validation
  fails client-side with an actionable message. This is a hard requirement, not a style choice.
- **IRI-valued fields get a `pattern`** even when not enumerable
  (precedent: `enabled_licenses` in `src/dsp_tools/resources/schema/project.json`).

## Test data

- **Systematic test data contains every supported feature.** New features extend the systematic
  fixtures (`testdata/`, e.g. the systematic JSON project and XML data files) — do not add
  standalone one-off fixtures for a new feature and leave the systematic data untouched.
- **Test-project shortcodes come from the team's shortcode register** — do not invent one.
  Ask the reviewers where the register lives before allocating.
  <!-- TODO(reviewers): link the shortcode register location here. -->

## Testing

- Test locations: unit → `test/unittests/`, integration → `test/integration/`,
  e2e (testcontainers) → `test/e2e/`.
- **E2E tests are not auto-discovered by CI.** Each e2e command suite is wired explicitly:
  a test directory under `test/e2e/commands/`, a `just e2e-test-<command>` recipe in the
  `justfile`, and a matching job in `.github/workflows/tests-e2e.yml`. A new e2e test that is
  not registered in all three places silently never runs.

## Architecture boundaries

- **xmllib is the public API** for programmatic XML creation
  (see `src/dsp_tools/xmllib/CLAUDE.md`). It must not import dsp-tools internals and it does not
  know the JSON project file — dependencies point from dsp-tools *into* xmllib, never the other
  way.
- **User-facing docs and docstrings do not cite xmllib internals** — user input is described in
  the user's terms (XML elements, JSON fields), not in terms of library code.
- **New RDF-mapped properties must be threaded through the validate-data pipeline**
  (`get_rdf_like_data()` → property type → SHACL shape in
  `src/dsp_tools/resources/validate_data/api-shapes.ttl`). The generic resource shape is
  closed: a new property needs an explicit cardinality declaration or xmlupload fails
  validation.

## Commit conventions

[Conventional Commits](https://www.conventionalcommits.org/), enforced by the
"Check PR Title" workflow: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`;
breaking changes use `!`.

## PR reviewers

Request review from the maintainers listed in `CLAUDE.md`
(BalduinLandolt, Nora-Olivia-Ammann, Notheturtle, seakayone, jnussbaum).

## Where to go for depth

- `CLAUDE.md` — architecture overview, commands, testing strategy
- `src/dsp_tools/xmllib/CLAUDE.md` — xmllib public-API layering
- `docs/developers/` — developer documentation (mkdocs)
- `REVIEW.md` — review-phase checklist
