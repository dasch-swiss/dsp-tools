# SHACL Shape Playbook

This is a playbook for **adding a new validation ("SHACL shape")** to the `validate-data` command.
Everything you need is here or linked. The ordered steps below are not a rigid procedure — they are the
**most efficient, fool-proof path** to the goal, sequenced so the cheapest feedback comes first. Deviate
if you have a good reason, but the ordering is what keeps you from building a lot on a wrong assumption.

This file is the *how do I add a new check* companion to [`CLAUDE.md`](./CLAUDE.md), which describes
how the existing code is structured.

## What you are building, and when you are done

**Context.** `dsp-tools` uploads research data to the DSP. `validate-data` runs SHACL validation
*before* the upload, so problems in the data are caught early — without waiting for a long upload that
may fail near the end. Every shape therefore exists to catch a real data problem and report it with an
informative, actionable message, so the user can correct the data before uploading.

**Goal.** A new SHACL shape that makes wrong data fail validation with a clear, actionable message and
lets correct data pass — with the smallest possible change to the report-processing code.

**The one mental model that drives everything:** when validation runs, SHACL emits a *report graph* in
which every failure is a `sh:ValidationResult` carrying a **`sh:sourceConstraintComponent`** (which kind
of constraint fired). Our Python code reads that component to decide which user message to show. So the
central question of the whole second half of this playbook is: *which component does my shape trigger,
and is it already handled?* If it is, you write almost no Python.

**Done looks like:** one violating resource fails with exactly one clear message; one correct resource
passes; the firing component is handled (or newly wired through); the unit and e2e suites are green; and
a review subagent (Step 7) has confirmed the change reuses existing code and stays simple.

---

## Before you start — confirm these, to avoid rework

Front-load the decisions that are expensive to get wrong, then work autonomously. Do **not** interrupt
mid-implementation for them.

- **Severity — confirm with the developer, unless it is already specified.** Whether a check is a
  violation, warning, or info is a policy decision you cannot derive, and it *routes the rest of your
  work*: it decides which test file and which e2e assertion list the data goes into (violations vs.
  warnings/info, see Step 6). Getting it wrong late means redoing the test wiring. If the severity is
  already given (in the prompt, a PRD, or an implementation plan), use it and do not ask again.
  Add the chosen value to the shape's `sh:severity`:
    - `sh:Violation` — **always blocks** upload on every server. For wrong data.
    - `sh:Warning` — **non-blocking on a test server, blocks on production**. Primarily for data that is
      only temporarily missing.
    - `sh:Info` — just a nudge; the upload will work on **all** servers.
- **Purpose, if it is not clear from the code.** If you cannot tell from the ontology and the code what
  the check is *for*, ask — a shape built on a misunderstood intent is the classic source of wasted work.

Everything else you **research and propose; you do not ask unless it is absolutely necessary**: derive
the datatype, the target
value/resource, and whether a property is mandatory or repeatable from the project ontology JSON, the
`knora-api` definitions, and the XML test data. Surface a choice for confirmation **only if it stays
genuinely ambiguous after that research** — e.g. the property is a `knora-api` concept like
`valueHasOrder`, whose datatype/cardinality is a DSP-behaviour decision rather than a project-ontology
lookup (and may even require a parser change before the value appears in the data graph at all).

> **Golden rule (this is the fail-fast core):** never write the shape first. Always write the **test
> data** first (at least one resource that must fail, one that must pass), *then* build the shape, *then*
> run it, and *only then* — if needed — touch Python. Cheap, objective feedback before expensive work.


---

## 1. The pipeline in one picture

```text
XML data ─────────────► RDF data graph -┐
                                        ├──► Docker SHACL CLI ──► report graph ──► user messages
project ontology ──► SHACL shapes ──────┘        (3 runs)
                     (static TTL + dynamically generated, merged)
```

- Shapes come from **two sources** that are **merged**: static Turtle files plus shapes generated at
  runtime by SPARQL. Merge happens in `prepare_data/prepare_data.py` `_create_graphs` into two graphs:
  `content_shapes` and `cardinality_shapes`.
- Validation shells out to a Docker image (`daschswiss/shacl-cli`) —
  `shacl_cli_validator.py`, orchestrated by `validation/get_validation_report.py` `get_validation_report`.
  There are **three separate SHACL runs**: the ontology, the cardinality shapes, and the content shapes.
  A shape placed in the wrong graph is simply never evaluated. It is important that cardinality constraints
  go into the cardinality shapes graph, otherwise you may get wrong errors. Same with content.
- The report graph is turned into user messages by `process_validation_report/`, in this order:
  `query_validation_result.py` → `reformat_validation_results.py` → `get_user_validation_message.py`.

---

## 2. Step 1 — Write the test data first (one fail, one pass)

Test data lives in `testdata/validate-data/`. The main set is `core_validation/` (project shortcode
`9999`). A suffix convention marks intent: `*_correct.xml` must **pass**, `*_violation.xml` must
**fail**. Most themes have both, but not every file is paired (e.g. `value_type_violation.xml` and
`unique_value_violation.xml` have no `_correct` partner).

Hard rules (they are enforced by the tests, so follow them):

- Add **one violating resource** to the relevant `*_violation.xml` and **one correct resource** to the
  matching `*_correct.xml`. Reuse an existing file if your check fits its theme (cardinality, content,
  value types, file values, dsp-inbuilt).
  If it is extensive with a lot of test data or does not fit into a file, create a new one.
- **One resource must produce exactly one user-facing violation.** Do not stack two unrelated errors
  on one resource — the e2e tests assert an exact count, so a resource with two problems breaks the
  1-to-1 mapping the whole suite relies on.
- The violating resource's `id` is a **descriptive slug** naming the violation, with an XML comment
  explaining it. Tests assert on that `id` (as `res_id`) and on the focus node `http://data/<id>`.

Example (violating), from `core_validation/cardinality_violation.xml`:

```xml
<!-- This class does not have a cardinality for the property -->
<resource label="Int card does not exist" restype=":CardOneResource" id="prop_does_not_have_card">
    <integer-prop name=":testIntegerSimpleText">
        <integer>1</integer>
    </integer-prop>
</resource>
```

If your check needs a new property or class, add it to the ontology in
`core_validation/core-validation-project-9999.json` (the catch-all class is
`ClassWithEverything`, which always has 0-1 or 0-n cardinality).
Try to re-use properties and classes if possible.
For edge cases there are dedicated projects: `special_characters/`, `inheritance/`,
`erroneous_ontology/` (ontology-level checks).

There is also `core_validation/every_violation_combination_once.xml`, an aggregate file exercising
every report shape once.
This is only if you create a new shape that also creates a new ConstraintComponentViolation,
otherwise you can leave this alone. **If you add a resource there, you must update two lists** in
`test/e2e/commands/validate_data/test_core_violations.py` (see Step 6).

---

## 3. Step 2 — Decide where the shape lives (prefer static)

> New shapes always live in the `api-shapes:` namespace (`http://api.knora.org/ontology/knora-api/shapes/v2#`),
> which also defines validation-only properties absent from `knora-api` (e.g. `api-shapes:dateHasStart`).
> For the `dash:` constraint components, see the [DASH reference](https://datashapes.org/constraints.html).

Ask: **does the check depend on anything project-specific?**

- **No → write it as a STATIC shape** in `src/dsp_tools/resources/validate_data/`. Prefer this. Use it
  when the target/path/allowed-values are fixed `knora-api`/`api-shapes` concepts that exist for every
  project: value content (datatypes, regexes, ranges), file formats, DSP built-in resources
  (`LinkObj`, `Region`, `AudioSegment`, `VideoSegment`).
    - Easiest option, **zero wiring**: append your shape to an already-loaded file —
      `api-shapes.ttl` (content checks) or `api-shapes-resource-cardinalities.ttl` (cardinality checks).
      For an ontology-level check, add to `validate-ontology.ttl`.
    - A brand-new `.ttl` file must be loaded and merged in `prepare_data/prepare_data.py`
      `_create_graphs`, into the **correct** graph: content vs. cardinality. Wrong graph = never runs.
- **Yes → write it as a DYNAMIC shape** in `sparql/`. Use it when the check depends on the **project
  ontology** (user-defined classes/properties, whose IRIs are unknown until runtime), on project
  **lists/licenses**, or on **permission ids declared in the XML**.
    - The mechanism is a SPARQL `CONSTRUCT` query run over the fetched ontology graph that *emits*
      SHACL triples. Study and copy the closest existing generator:
        - `sparql/cardinality_shacl.py` — `CONSTRUCT` over OWL cardinality restrictions.
        - `sparql/value_shacl.py` — binds project properties to value-type / list / text shapes.
        - `sparql/legal_info_shacl.py` — templates a Turtle string with interpolated license IRIs.
    - Wire a new generator into `sparql/construct_shacl.py` `construct_shapes_graphs`, adding its output
      to the `content` or `cardinality` graph.

**Key pattern — combine both.** Dynamic shapes usually do **not** duplicate logic; they *reference a
reusable static NodeShape by IRI*. For example, for each project text property whose gui element is
`SimpleText`, `value_shacl.py` generates a `<prop>_PropShape` PropertyShape
(`sh:path <prop> ; sh:node api-shapes:SimpleTextValue_ClassShape`), where that NodeShape is defined
statically in `api-shapes.ttl` (`Textarea` and `Richtext` map to other class shapes). So a very
common move is: **add a reusable static shape, then add/extend a SPARQL generator that binds the
project's properties to it.**

**Write a useful `sh:message` in the shape.** For many components the shape's message is shown verbatim
to the user (see the table in Step 4), so a useful message here often means **zero or little Python
changes**. A useful message is *actionable*: the user must be able to understand and fix the problem
without any further investigation. State what is wrong *and* what is expected, in the terms the user
knows (the XML and ontology names, not internal SHACL/RDF jargon).

- **Good:** `"Only positive numbers are allowed for this property, you entered a negative number."`
- **Bad:** `"Invalid input for this property"` — the user has to investigate what "invalid" means.

### Shape authoring conventions

**A new property only fires if it is attached via `sh:property`.** A `sh:PropertyShape` that is defined
but never referenced by a `sh:property` on a node shape is simply never evaluated. So when you add a
check for a new property on a value, you must add it as a `sh:property` on the relevant node shape,
otherwise nothing happens.

**Named IRI shape vs. inline blank node.** A property shape can either have its own IRI or be an
anonymous blank node (`[ ... ]`) inlined under `sh:property`:

- If the shape should be **re-usable across multiple classes**, or is going to be **referenced by the
  dynamically generated shapes**, give it its own IRI (a *named* shape), e.g.
  `api-shapes:hasComment_PropertyShape`.
- If it is only applicable to a **single class**, inline it directly as a **blank node**. This is
  easier to read.

**One shape may validate several things — but only if the message stays easy to construct.** Combining
constraints in one property shape is fine when a single `sh:message` clearly covers every way it can
fail. It becomes a problem when the combination makes the message too vague to act on.

**OK** — a min/max count *and* a datatype in one shape: the message covers both, and the user will not
have a hard time figuring out what went wrong.

```ttl
[
    a           sh:PropertyShape ;
    sh:path     knora-api:decimalValueAsDecimal ;
    sh:datatype xsd:decimal ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
    sh:severity sh:Violation ;
    sh:message  "A DecimalValue requires exactly one valid decimal"
] .
```

**Split it** — when several constraints could fire for unrelated reasons and one message cannot cover
them without becoming confusing. For example a range check (`sh:minInclusive` + `sh:maxInclusive`) *and*
a datatype *and* a cardinality on `knora-api:valueHasOrder`, plus the separate
`api-shapes:ValueHasOrder_NoGap_Shape` and `api-shapes:ValueHasOrder_MissingWhenSomeOrdered_Shape`, would
be very hard to identify from a single message. Keep the distinct concerns as separate shapes, each with
its own targeted message:

```ttl
[
    a               sh:PropertyShape ;
    sh:path         knora-api:valueHasOrder ;
    sh:datatype     xsd:integer ;
    sh:minInclusive "0"^^xsd:int ;
    sh:maxInclusive "2147483647"^^xsd:int ; # maximum allowed number for this datatype
    sh:severity     sh:Violation ;
    sh:message      "The order on the value must be a positive integer."
] ,
[
    a           sh:PropertyShape ;
    sh:path     knora-api:valueHasOrder ;
    sh:minCount 0 ;
    sh:maxCount 1 ;
    sh:severity sh:Violation ;
    sh:message  "A value may have a maximum of 1 order triple."
] .
```

If in doubt whether a combined shape's message stays clear enough, ask.

---

## 4. Step 3 — Run it and find which constraint component fires

You must learn which `sh:sourceConstraintComponent` your shape triggers, because that decides whether
you touch Python at all. This you will find more difficult to anticipate, therefore just try it out first.

Full loop (requires **Docker running**): run `validate-data` on your test file with
`--save-graphs <dir>` (CLI flag defined in `cli/create_parsers.py`, consumed in `validate_data.py`).
Open the saved report `.ttl`, find the `sh:ValidationResult` whose `sh:focusNode` is your resource, and
read its `sh:sourceConstraintComponent`. Alternatively assert it directly, the way
`test_core_violations.py::TestWithReportGraphs::test_extract_identifiers_of_resource_results` does.
Note that a violation may trigger a main violation which is identifiable by the resource id or value id and a `sh:detail`.
In that case the information of both is relevant for further processing.

> **If nothing fires and the tests still pass, your SHACL shape did not trigger properly. 
> This likely means the shape is broken.** Check, in order:
> the shape is in the correct graph (content vs. cardinality); the property shape is actually attached
> to its node shape via `sh:property` (a `sh:PropertyShape` that nothing references is never evaluated);
> `sh:targetClass` / `sh:path` use the exact IRIs the data uses.

---

## 5. Step 4 — Two outcomes

Look up your component in the table below.

- **The component is already handled** → the user usually already gets a good message.
  **No report-processing code changes.** Just add your test data (Step 1) and adjust the e2e
  assertions (Step 6). Caveats that can still force small code changes even when reusing a component:
    - the property is checked against a set in `constants.py`
      (`FILE_VALUE_PROPERTIES`, `LEGAL_INFO_PROPS`, `FILEVALUE_DETAIL_INFO`) — a new property may need
      adding/excluding there;
    - your shape emits a `sh:detail` (nested result) with a structure the matched handler does not
      expect;
    - the component is `sh:ClassConstraintComponent`, which sub-routes to value-type vs. link-target
      vs. generic — a new use may land in the wrong branch.
- **The component is new** (not in the code) → it currently falls into the `case _` fallback, becomes
  an `UnexpectedComponent`, and **fails validation** with an "unknown violation types were found"
  message (`validate_data.py` `_get_validation_status` treats these as failures). Follow the checklist
  in Step 5.

### Constraint-component reference map

Dispatch lives in `process_validation_report/query_validation_result.py`: `_query_one_without_detail`
(results with no `sh:detail`) and `_query_one_with_detail`.
"Message shown" = whether the shape's own `sh:message` reaches the user (true when the resulting
`ProblemType` is in `PROBLEM_TYPES_IGNORE_STR_ENUM_INFO`, so the enum label is suppressed).

| `sh:sourceConstraintComponent`                                                                               | Resulting `ViolationType`                      | User `ProblemType`       | Shape `sh:message` shown?                           |
|--------------------------------------------------------------------------------------------------------------|------------------------------------------------|--------------------------|-----------------------------------------------------|
| `sh:PatternConstraintComponent`                                                                              | `PATTERN`                                      | `INPUT_REGEX`            | via `expected`                                      |
| `sh:MinCountConstraintComponent`                                                                             | `MIN_CARD` (or `GENERIC` for legal-info props) | `MIN_CARD` / `GENERIC`   | partially                                           |
| `sh:MaxCountConstraintComponent`                                                                             | `MAX_CARD`                                     | `MAX_CARD`               | via `expected`                                      |
| `sh:LessThanOrEqualsConstraintComponent`                                                                     | `GENERIC` (or dropped for unparsable dates)    | `GENERIC`                | yes                                                 |
| `dash:ClosedByTypesConstraintComponent`                                                                      | `NON_EXISTING_CARD` / `FILE_VALUE_PROHIBITED`  | same                     | no                                                  |
| `dash:CoExistsWithConstraintComponent`                                                                       | `SEQNUM_IS_PART_OF` / `GENERIC`                | `GENERIC`                | yes                                                 |
| `sh:ClassConstraintComponent`                                                                                | `VALUE_TYPE` / `LINK_TARGET` / `GENERIC`       | matching                 | mixed                                               |
| `sh:InConstraintComponent`                                                                                   | `GENERIC`                                      | `GENERIC`                | yes                                                 |
| `sh:DatatypeConstraintComponent`                                                                             | `GENERIC`                                      | `GENERIC`                | yes                                                 |
| `sh:SPARQLConstraintComponent`                                                                               | `GENERIC`                                      | `GENERIC`                | yes                                                 |
| `sh:MinInclusiveConstraintComponent` / `MaxInclusiveConstraintComponent` / `MinExclusiveConstraintComponent` | `GENERIC`                                      | `GENERIC`                | yes                                                 |
| `sh:LessThanConstraintComponent`                                                                             | `GENERIC`                                      | `GENERIC`                | yes                                                 |
| `dash:SingleLineConstraintComponent`                                                                         | `GENERIC`                                      | `GENERIC`                | yes                                                 |
| `sh:OrConstraintComponent`                                                                                   | `GENERIC` (value as string)                    | `GENERIC`                | yes                                                 |
| `sh:NotConstraintComponent`                                                                                  | `FILE_VALUE_PLACEHOLDER`                       | `FILE_VALUE_PLACEHOLDER` | yes                                                 |
| anything else                                                                                                | —                                              | —                        | falls into `case _` → `UnexpectedComponent` (fails) |

The two classification enums: `ViolationType` (internal) in `models/validation.py`, `ProblemType`
(user-facing, its string value is the label) in `models/input_problems.py`, bridged by
`RESULT_TO_PROBLEM_MAPPER` in `validate_data/mappers.py` (the parent of `process_validation_report/`).
Note: some recognised components are intentionally dropped (`return None`) — e.g. a date range where
the date is an unparsable string; that is a deliberate suppression, not the unknown-component path.

**Note on `sh:detail`.** The resulting type can also depend on whether the result carries a
`sh:detail` (nested result), not just on the component. For example `sh:MinCountConstraintComponent`
**with a `sh:detail`** resolves to `VALUE_TYPE`, not `MIN_CARD`. The no-detail and with-detail cases
are dispatched separately by `_query_one_without_detail` / `_query_one_with_detail`.

---

## 6. Step 5 (new component only) — wire it through the pipeline

Do these in order. The "reuse GENERIC" fast path handles most cases; only add a new user category if
none of the existing `ProblemType`s fit.

1. **Dispatch** — `query_validation_result.py`: add a `case SH.<X>ConstraintComponent:` in
   `_query_one_without_detail` (and/or `_query_one_with_detail` if your shape emits a `sh:detail`).
   For a simple value constraint you can reuse the existing helper
   `_query_general_violation_info(base_info.result_bn, base_info, results_and_onto, ViolationType.<Y>)`;
   it copies `sh:resultMessage`, `sh:value`, and `sh:resultPath` into a `ValidationResult`.
2. **`ViolationType`** — `models/validation.py`: add a member **only if** no existing one fits
   (`GENERIC` fits any plain value constraint).
3. **Reformat** — `reformat_validation_results.py`: add your `ViolationType` to a `case` in
   `_reformat_one_validation_result`. If it behaves like a generic value error, add it to the existing
   `MAX_CARD | NON_EXISTING_CARD | PATTERN | VALUE_TYPE` group. **If you skip this, you get an
   `UnreachableCodeError` at runtime** (the `case _` fallback) — the compiler will not warn you.
4. **`ProblemType`** — `models/input_problems.py`: add a member whose string value is the user-facing
   label — **only if** you need a new user category.
5. **Mapper** — `validate_data/mappers.py` (parent of `process_validation_report/`): add the
   `ViolationType.<Y>: ProblemType.<Z>` entry to `RESULT_TO_PROBLEM_MAPPER`.
6. **Message shaping (optional)** — `get_user_validation_message.py`: add your `ProblemType` to
   `PROBLEM_TYPES_IGNORE_STR_ENUM_INFO` to show the shape's `sh:message` instead of the enum label; add
   a case in `_get_expected_prefix` for an "Expected …" prefix; special-case `_shorten_input` if the
   input value must not be truncated.
7. **Unit tests** — add a `report_<x>` + `extracted_<x>` fixture pair in
   `fixtures/validation_result.py`, a dispatch test in `test_query_validation_result.py`, and a
   reformat test in `test_reformat_validation_results.py`.
8. **Add to table above** to prevent outdated information you must also update this document.

**Minimum change set** if `GENERIC` is acceptable: steps 1, 7 and 8 only.
**Full new-category change set**: steps 1–8.

---

## 7. Step 6 — Update and run the tests

- **E2E expectations are inline `expected_*` lists** in `test/e2e/commands/validate_data/`. Append a
  `(res_id, ProblemType, ...)` tuple to the list in the matching test; violations are sorted by
  `res_id`, and there is an exact-count assertion, so a missing tuple fails loudly. Files by scenario:
    - `test_core_correct.py` — the "must pass" tests (add nothing unless your correct resource is new).
    - `test_core_violations.py` — cardinality / content / value-type / file / unique-value / dsp-inbuilt.
    - `test_core_warning_and_info.py` — warnings and info.
    - `test_edge_cases.py` — special characters, inheritance, erroneous ontology.
    - If you touched `every_violation_combination_once.xml`, update **both** lists in
      `test_core_violations.py` (`test_extract_identifiers_of_resource_results` **and**
      `test_reformat_every_constraint_once`).
- **Unit expectations**: the fixtures/tests from Step 5.7.
- **Commands**:
    - `just unittests test/unittests/commands/validate_data/` — fast, no Docker; covers the whole
      report-processing chain.
    - `just e2e-test-validate-data` — **requires Docker**; spins up a real DSP stack (testcontainers),
      creates the project, and validates the data end-to-end.
    - `just lint` — before committing.

---

## 8. Step 7 — Review before handing back

When the implementation is complete and both suites are green, **spawn a review subagent** before you
hand back.
This is the *quality* net, not the correctness check (correctness is the empirical loop in Steps 1–4).
The review must consider, but is not limited to:

- **Reuse over addition.** The report-processing query and the reformatting chain are already large and
  slow. A new component must **reuse** existing helpers (`_query_general_violation_info`, the `GENERIC`
  path) wherever it can, and must **not** grow the validation-result query when an existing path works.
- **Simplicity.** No new `ViolationType` / `ProblemType` unless an existing one genuinely does not fit.
- **Completeness.** The plumbing is covered: the project JSON and XML test data are updated, the value is
  actually parsed (a `knora-api` value may need a parser change before it appears in the data graph), and
  — if `every_violation_combination_once.xml` was touched — both lists in `test_core_violations.py` were
  updated.
- **This document.** If a new component was wired through, the Step 4 table and the checklist below were
  updated to match.

---

## 9. Quick checklist

**Before you start:** confirm **severity** with the developer (it routes test placement) and the check's
**purpose** if it is not clear from the code. Then:

1. [ ] Add one violating + one correct resource to `testdata/validate-data/…` (one error per resource,
   descriptive `id`, XML comment). Add any new property/class to the project JSON.
2. [ ] Decide static (`resources/validate_data/*.ttl`, preferred) vs. dynamic (`sparql/*.py`) or combination. Write a
   clear `sh:message`.
3. [ ] If a new static file or a new generator: wire it into `prepare_data/prepare_data.py`
   `_create_graphs` / `sparql/construct_shacl.py`, in the correct (content vs. cardinality) graph.
4. [ ] Find the firing `sh:sourceConstraintComponent` (unit fixture, or `--save-graphs` + Docker).
5. [ ] Look it up in the Step 4 table. Already handled → skip to 6. New → do Step 5 (dispatch →
   ViolationType → reformat → ProblemType → mapper → message → unit tests → update this document).
6. [ ] Add e2e `(res_id, ProblemType)` tuples in `test/e2e/commands/validate_data/`.
7. [ ] `just unittests test/unittests/commands/validate_data/`, then `just e2e-test-validate-data`
   (needs Docker), then `just lint`.
8. [ ] Spawn a review subagent (Step 7) to check reuse, simplicity, and the plumbing/completeness traps
   before handing back.
