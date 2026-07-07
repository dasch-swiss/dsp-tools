# Code Review Checklist

Agent reference card for the **review phase**. Pair with `CONVENTIONS.md` (work phase).

## Always check

### Build & history

- [ ] `just lint` passes (ruff format + check, mypy, yamllint, markdownlint, darglint, vulture)
- [ ] Unit / integration / e2e tests cover the changed behaviour
- [ ] Commits and PR title follow Conventional Commits (`feat:` / `fix:` / `docs:` / …)

### Naming

- [ ] Project-wide overridable values are named with the `default_*` prefix; directly applied
      values are not — renaming after merge is a cross-repo breaking change
- [ ] If a `default_*` value is not auto-applied in some flow (e.g. `xmlupload`), the user docs
      of that flow say so explicitly

### JSON schemas

- [ ] Fields with a fixed set of allowed values are schema `enum`s, not free strings with a
      documented constraint
- [ ] IRI-valued fields have a `pattern` (precedent: `enabled_licenses` in `project.json`)

### Test data

- [ ] New features are exercised in the **systematic** test data, not only in standalone
      ad-hoc fixtures
- [ ] New test-project shortcodes come from the team's shortcode register, not invented

### E2E wiring

- [ ] A new e2e command suite is registered in all three places: `test/e2e/commands/<command>/`,
      a `just e2e-test-<command>` recipe, and a job in `.github/workflows/tests-e2e.yml`
      — otherwise it silently never runs in CI

### Architecture boundaries

- [ ] xmllib does not import dsp-tools internals and has no knowledge of the JSON project file
- [ ] User-facing docs and docstrings describe user input (XML elements, JSON fields), not
      xmllib internals
- [ ] New RDF-mapped properties are threaded through the validate-data pipeline and have an
      explicit cardinality in `api-shapes.ttl` (the generic resource shape is closed)

### Docs

- [ ] User documentation (mkdocs) updated where behaviour changed; statements about the same
      feature do not contradict each other across pages
- [ ] `CLAUDE.md` / `CONVENTIONS.md` / `REVIEW.md` updated if a convention changed

## Skip

- Formatting-only diffs (enforced by `ruff format` / `yamlfmt`)
- `CHANGELOG.md` and release commits (managed by release automation)
- Generated or vendored sources
