# Used Shortcodes and Shortnames for End-to-End Tests

Shortcodes and shortnames must be unique in DSP.

We have many different projects in our test data.
This is an inventory of the used shortcodes and shortnames for projects
that are primarily used for e2e tests with a running stack.

All the shortcodes for invalid projects start with an `F`

File naming conventions:

- Project JSON files should be called `[shortname]-project-[shortcode].json`
- Any XML data files that use this ontology should be named `[free-to-choose]-[shortcode].xml`

## Valid Projects

| Shortcode | Shortname           | File Path                                                                 | Where                         |
|-----------|---------------------|---------------------------------------------------------------------------|-------------------------------|
| 0001      | e2e-ingest          | testdata/dsp-ingest-data/e2e-sample-project/e2e-ingest-project-0001.json  | `ingest-xmlupload`            |
| 0002      | circular-reference  | testdata/json-project/circular-reference-project-0002.json                | required for an XML           |
| 8888      | test                | testdata/json-project/create-project.json                                 | `create`                      |
| 4125      | e2e-tp              | testdata/json-project/generic-e2e-project.json                            | `create`, `get`, `xmlupload`  |
| 4127      | limited-view-tp     | testdata/json-project/limited-view-project.json                           | NEVER!                        |
| 0006      | list-lookup         | testdata/json-project/list-lookup-project.json                            | `xmllib` integration          |
| 4124      | minimal-tp          | testdata/json-project/minimal-project.json                                | `create`                      |
| 4123      | systematic-tp       | testdata/json-project/systematic-project.json                             | `create`, `xmlupload`         |
| 9991      | erroneous-ontology  | testdata/validate-data/erroneous_ontology/erroneous-onto-project.json     | `validate-data `              |
| 9999      | test                | testdata/validate-data/generic/feature-complete-project.json              | `validate-data `, `xmlupload` |
| 9990      | complex-inheritance | testdata/validate-data/inheritance/complex-inheritance-project.json       | `validate-data `              |
| 0002      | special             | testdata/validate-data/special_characters/special-characters-project.json | `validate-data `              |

## Invalid Projects

| Shortcode | Shortname           | File Path                                                              | Where    |
|-----------|---------------------|------------------------------------------------------------------------|----------|
| F001      | circular-onto       | testdata/invalid-testdata/json-project/circular-ontology.json          | `create` |
| F002      | duplicate-listnames | testdata/invalid-testdata/json-project/duplicate-listnames.json        | `create` |
| F003      | duplicate-property  | testdata/invalid-testdata/json-project/duplicate-property.json         | `create` |
| F004      | duplicate-resource  | testdata/invalid-testdata/json-project/duplicate-resource.json         | `create` |
| F005      | invalid-super-prop  | testdata/invalid-testdata/json-project/invalid-super-property.json     | `create` |
| F006      | nonexisting-card    | testdata/invalid-testdata/json-project/nonexisting-cardinality.json    | `create` |
| F007      | nonexist-super-prop | testdata/invalid-testdata/json-project/nonexisting-super-property.json | `create` |
| F008      | nonexist-super-res  | testdata/invalid-testdata/json-project/nonexisting-super-resource.json | `create` |
