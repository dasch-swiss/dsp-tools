# Implementation Plan for default_permissions_overrule Feature

## Phase 1: Tests (TDD Approach)

- [x] Write unit tests for default_permissions_overrule in properties - Test parsing and serialization
- [x] Write unit tests for default_permissions_overrule in resources - Test parsing and serialization  
- [ ] Write integration tests - Test with actual Excel files

## Phase 2: Model Updates

- [ ] Update OntoProperty model - Add `default_permissions_overrule` field (Optional[str])
- [ ] Update OntoResource model - Add `default_permissions_overrule` field (Optional[str])
- [ ] Update serialization methods - Include field in JSON output when present

## Phase 3: Excel Parsing

- [ ] Update column definitions - Add optional `default_permissions_overrule` column to both files
- [ ] Update _get_prop_from_row - Parse new column in properties.py
- [ ] Update _get_resource_from_row - Parse new column in resources.py

## Phase 4: Validation

- [ ] Add validation - Ensure values are "private" or "limited_view" (resources only)

## Implementation Notes

Based on the documentation:

- For properties: only "private" is allowed  
- For resources: "private" or "limited_view" allowed
- Column is optional in both Excel files
- Field only appears in JSON when present (not empty)

## Files to modify

- `src/dsp_tools/commands/excel2json/models/ontology.py`
- `src/dsp_tools/commands/excel2json/properties.py`
- `src/dsp_tools/commands/excel2json/resources.py`
- `test/unittests/commands/excel2json/test_properties.py`
- `test/unittests/commands/excel2json/test_resources.py`
- `test/integration/commands/excel2json/test_properties.py`
- `test/integration/commands/excel2json/test_resources.py`
