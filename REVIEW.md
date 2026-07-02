# Code Review Checklist

Agent reference card for the **review phase**. Pair with `CONVENTIONS.md` (work phase).
Flag anything below that a change violates.

## Always Check

### Build & history

- [ ] `just lint` passes (ruff check + ruff format + yamllint + markdownlint)
- [ ] `just mypy` passes; all new code is fully type-annotated
- [ ] Relevant tests pass and cover the change (unit for logic, integration/E2E for user-facing behaviour)
- [ ] Commits follow [Conventional Commits](https://www.conventionalcommits.org/) — style matches recent `git log`
- [ ] Relevant `CLAUDE.md` files updated when behaviour/structure changed; `CONVENTIONS.md` / `REVIEW.md`
      updated when a convention changed

### Architecture & code

- [ ] No command imports from another command — shared logic is in `utils/`, shared HTTP routes in `clients/`
- [ ] Behaviour lives in stateless functions; classes only bundle data (`@dataclass`)
- [ ] HTTP goes through `utils/request_utils.py` (no raw requests, no retry logic in `clients/`)
- [ ] `pathlib.Path` used throughout — no `os.path`, no paths passed as strings
- [ ] Names are evergreen (no `new`/`improved`/`enhanced`); comments describe code as-is, not its history
- [ ] No redundant conversions — e.g. don't wrap an already-`list` value in `list(...)`; don't re-parse /
      re-iterate a structure that is already being iterated
- [ ] Control flow is as flat as the logic allows (early returns kept where they clarify; a helper that only
      applies to one branch lives in that branch, not the shared tail)

### JSON Schema

- [ ] Fields with a fixed, known value set are modelled as `enum` in `resources/schema/project.json`
      (not a bare `string` or loose `pattern`)

### Tests

- [ ] **Every new feature/behaviour is actually tested — flag it when it is not.**
- [ ] Assertions are bare (no custom failure messages)
- [ ] RDF-graph tests assert the *whole* graph (type, label, `attachedToProject`, all values), not only the
      one new triple
- [ ] `validate-data` changes add **both** a conforming and a violating test case (happy + error paths)
- [ ] New test data prefers extending the **systematic** test project over a new standalone `feature-XXXX`
      file; new shortcodes/shortnames are added to `testdata/USED_SHORTCODE_SHORTNAMES.md` and follow its
      file-naming convention (`[shortname]-project-[shortcode].json`, `[free]-[shortcode].xml`, invalid → `F…`)
- [ ] E2E `just` recipes stay one-per-file/logical-group — a new e2e file gets its own recipe (and its own CI
      invocation), not appended to an unrelated recipe

### Docs

- [ ] `docs/` updated where user-facing behaviour or the XML/JSON format changed

## Skip

- Formatting-only diffs (enforced by `just lint`)
- `CHANGELOG.md` and version-bump commits (managed by release tooling)
- Generated / vendored files
