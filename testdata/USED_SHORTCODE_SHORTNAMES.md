# Used Shortcodes and Shortnames for End-to-End Tests

Shortcodes and shortnames must be unique in DSP.

We have many different projects in our test data,
this is an inventory of the used shortcodes and names for projects that are used for e2e tests with a running stack.

## Valid Projects

| Shortcode | Shortname          | File Path                                                                 | Where                         |
|-----------|--------------------|---------------------------------------------------------------------------|-------------------------------|
| 4126      | e2e-ingest-tp      | testdata/dsp-ingest-data/e2e-sample-project/project.json                  | `ingest-xmlupload`            |
| 8888      | test               | testdata/json-project/create-project.json                                 | `create`                      |
| 0001      | list-lookup        | testdata/json-project/test-list-lookup.json                               | `xmllib` integration          |
| 4125      | e2e-tp             | testdata/json-project/test-project-e2e.json                               | `get`                         |
| 4124      | limited-view-tp    | testdata/json-project/test-project-limited-view.json                      | NEVER!                        |
| 4124      | minimal-tp         | testdata/json-project/test-project-minimal.json                           | `create`                      |
| 4123      | systematic-tp      | testdata/json-project/test-project-systematic.json                        | `create`, `xmlupload`         |
| 0700      | simcir             | testdata/json-project/test_circles_onto.json                              | NEVER!                        |
| 9991      | erroneous-ontology | testdata/validate-data/erroneous_ontology/project_erroneous_ontology.json | `validate-data `              |
| 9999      | test               | testdata/validate-data/generic/project.json                               | `validate-data `, `xmlupload` |
| 9990      | test-inheritance   | testdata/validate-data/inheritance/project_inheritance.json               | `validate-data `              |
| 0002      | special            | testdata/validate-data/special_characters/project_special_characters.json | `validate-data `              |

## Invalid Projects

| Shortcode | Shortname           | File Path                                                              | Where    |
|-----------|---------------------|------------------------------------------------------------------------|----------|
| 1233      | circular-onto       | testdata/invalid-testdata/json-project/circular-ontology.json          | `create` |
| 4124      | minimal-tp          | testdata/invalid-testdata/json-project/duplicate-listnames.json        | `create` |
| 4124      | minimal-tp          | testdata/invalid-testdata/json-project/duplicate-property.json         | `create` |
| 4124      | minimal-tp          | testdata/invalid-testdata/json-project/duplicate-resource.json         | `create` |
| 4124      | invalid-super-prop  | testdata/invalid-testdata/json-project/invalid-super-property.json     | `create` |
| 4123      | nonexisting-card    | testdata/invalid-testdata/json-project/nonexisting-cardinality.json    | `create` |
| 4123      | nonexist-super-prop | testdata/invalid-testdata/json-project/nonexisting-super-property.json | `create` |
| 4123      | nonexist-super-res  | testdata/invalid-testdata/json-project/nonexisting-super-resource.json | `create` |
