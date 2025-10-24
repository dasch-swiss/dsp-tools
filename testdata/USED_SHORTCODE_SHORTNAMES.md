# Used Shortcodes and Shortnames for End-to-End Tests

Shortcodes and shortnames must be unique in DSP.

We have many different projects in our test data,
this is an inventory of the used shortcodes and names for projects that are used for e2e tests with a running stack.

## Used in e2e Tests With a Stack

| Shortcode | Shortname          | File Path                                                                 | CLI              |
|-----------|--------------------|---------------------------------------------------------------------------|------------------|
| 4126      | e2e-ingest-tp      | testdata/dsp-ingest-data/e2e-sample-project/project.json                  |                  |
| 8888      | test               | testdata/json-project/create-project.json                                 |                  |
| 0001      | list-lookup        | testdata/json-project/test-list-lookup.json                               |                  |
| 4125      | e2e-tp             | testdata/json-project/test-project-e2e.json                               |                  |
| 4124      | limited-view-tp    | testdata/json-project/test-project-limited-view.json                      |                  |
| 4124      | minimal-tp         | testdata/json-project/test-project-minimal.json                           |                  |
| 4123      | systematic-tp      | testdata/json-project/test-project-systematic.json                        |                  |
| 0700      | simcir             | testdata/json-project/test_circles_onto.json                              |                  |
| 9991      | erroneous-ontology | testdata/validate-data/erroneous_ontology/project_erroneous_ontology.json | `validate-data ` |
| 9999      | test               | testdata/validate-data/generic/project.json                               | `validate-data ` |
| 9990      | test-inheritance   | testdata/validate-data/inheritance/project_inheritance.json               | `validate-data ` |
| 0002      | special            | testdata/validate-data/special_characters/project_special_characters.json | `validate-data ` |

## Invalid Projects

| Shortcode | Shortname           | File Path                                                              |
|-----------|---------------------|------------------------------------------------------------------------|
| 1233      | circular-onto       | testdata/invalid-testdata/json-project/circular-ontology.json          |
| 4124      | minimal-tp          | testdata/invalid-testdata/json-project/duplicate-listnames.json        |
| 4124      | minimal-tp          | testdata/invalid-testdata/json-project/duplicate-property.json         |
| 4124      | minimal-tp          | testdata/invalid-testdata/json-project/duplicate-resource.json         |
| 4124      | invalid-super-prop  | testdata/invalid-testdata/json-project/invalid-super-property.json     |
| 4123      | nonexisting-card    | testdata/invalid-testdata/json-project/nonexisting-cardinality.json    |
| 4123      | nonexist-super-prop | testdata/invalid-testdata/json-project/nonexisting-super-property.json |
| 4123      | nonexist-super-res  | testdata/invalid-testdata/json-project/nonexisting-super-resource.json |
