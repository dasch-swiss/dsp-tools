# Update Legal Metadata Command

## Purpose

The `update-legal` command converts legal metadata in XML files from the old format (text properties)
to the new format (bitstream attributes). This migration is necessary because:

- **Old format**: Legal metadata (authorship, copyright, license) stored as `<text-prop>` elements within resources
- **New format**: Legal metadata stored as attributes directly on `<bitstream>` or `<iiif-uri>` elements

This command automates the migration while handling validation, error correction, and authorship deduplication.

## Command Usage

```bash
dsp-tools update-legal \
  --authorship_prop=":hasAuthor" \
  --copyright_prop=":hasCopyright" \
  --license_prop=":hasLicense" \
  --authorship_default="Project Member" \
  --copyright_default="University" \
  --license_default="CC BY" \
  --fixed_errors="data_legal_errors.csv" \
  data.xml
```

See [docs/special-workflows/update-legal.md](../../../../docs/special-workflows/update-legal.md) for user documentation.

## Architecture Overview

### Data Flow Pipeline

The command follows a multi-stage pipeline:

1. **Parse & Validate**: Parse XML file and validate property names exist
2. **Extract Metadata**: For each resource with media, extract legal metadata using priority system
3. **Validation**: Check for missing/invalid values
4. **Error Handling**: If errors exist, write CSV for manual correction
5. **Update XML**: If no errors, apply metadata as attributes and write updated XML
6. **Iteration**: User fixes CSV and reruns command until all errors resolved

### Priority System

Metadata values are resolved using this priority order:

1. **CSV corrections** (from `--fixed_errors` file)
2. **XML properties** (extracted from text-prop elements)
3. **Default values** (from `--*_default` flags)
4. **None** (triggers validation error)

## Module Responsibilities

### [core.py](core.py)

Main orchestration and validation logic:

- `update_legal_metadata()`: Entry point that coordinates entire workflow
- `_validate_flags()`: Ensures property names exist in XML
- `_update_xml_tree()`: Iterates through resources, collects metadata once per resource, decides whether to apply changes
- `_has_problems()`: Checks if metadata contains FIXME markers or missing values
- `_update_counter()`: Tracks statistics for final report

Key patterns:

- Uses functional approach with pure helper functions
- Clear separation: collection (read-only) vs application (mutations)
- Single-pass metadata collection eliminates duplicate work
- Authorship deduplication via `auth_text_to_id` dictionary (maps authorship text to unique ID)

### [models.py](models.py)

Data structures and configuration:

- `LegalProperties`: Configuration for XML property names (e.g., `:hasAuthor`)
- `LegalMetadata`: Represents legal metadata for a single resource (license, copyright, authorships)
- `LegalMetadataDefaults`: Default values with automatic license parsing
- `Problem`: Represents validation error for CSV export
- `UpdateCounter`: Statistics tracker for final report

Important notes:

- `LegalMetadataDefaults.__init__()` automatically validates and parses license strings
  using `xmllib.find_license_in_string()`
- All dataclasses use frozen=True for immutability where appropriate

### [csv_operations.py](csv_operations.py)

CSV I/O for error handling workflow:

- `ProblemAggregator`: Converts problems to DataFrame with dynamic authorship columns
- `read_corrections_csv()`: Parses CSV corrections into `dict[resource_id, LegalMetadata]`
- `write_problems_to_csv()`: Writes validation errors to CSV with helpful FIXME markers
- `is_fixme_value()`: Checks if value starts with "FIXME:" prefix

**CSV format:**

- Fixed columns: `file`, `resource_id`, `license`, `copyright`
- Dynamic columns: `authorship_1`, `authorship_2`, ... (as many as needed)
- Sorted by resource_id for easy navigation

**Error prevention:**

- Refuses to overwrite existing CSV unless `--fixed_errors` flag provided
- Helpful error message suggests correct flag usage

### [xml_operations.py](xml_operations.py)

XML manipulation and metadata application:

- `collect_metadata()`: Pure function that collects metadata from CSV, XML, or defaults (read-only)
- `apply_metadata_to_resource()`: Applies metadata as attributes and removes old text properties (mutations)
- `_resolve_metadata_values()`: Implements priority system (CSV > XML > defaults)
- `_extract_license_from_xml()`: Extracts license and validates with `xmllib.find_license_in_string()`
- `_extract_copyright_from_xml()`: Extracts copyright, detects duplicates
- `_extract_authorships_from_xml()`: Collects all authorship values
- `_apply_metadata_to_element()`: Applies metadata as attributes on media element
- `_remove_text_properties()`: Removes old text-prop elements
- `add_authorship_definitions_to_xml()`: Creates `<authorship>` definitions at root level
- `write_final_xml()`: Writes updated XML with statistics

**Authorship deduplication:**

- Multiple resources can share same authorship (e.g., "Jane Doe, Alice Jenkins")
- `auth_text_to_id` dictionary tracks unique authorships and assigns sequential IDs
- Authorship definitions added to root as `<authorship id="authorship_0">` elements
- Media elements reference via `authorship-id="authorship_0"` attribute

**Multiple value detection:**

- If multiple copyright values found: returns `"FIXME: Multiple copyrights found. Choose one: ..."`
- If multiple license values found: returns `"FIXME: Multiple licenses found. Choose one: ..."`
- This triggers CSV export for manual resolution

## Architectural Improvements

### Separation of Collection and Application

The codebase follows a clear pattern separating read operations from write operations:

**Collection Phase (`collect_metadata()`):**

- Pure function with no side effects
- Reads from CSV, XML properties, and defaults
- Returns `LegalMetadata` object
- Can be called safely without modifying the XML tree
- Executes exactly once per resource

**Application Phase (`apply_metadata_to_resource()`):**

- Mutates the XML tree in-place
- Applies metadata as attributes on media elements
- Removes old text properties
- Manages authorship deduplication dictionary
- Only called for valid resources (no problems)

**Benefits:**

- **Performance**: Eliminates duplicate XPath queries (~50% reduction for valid resources)
- **Clarity**: Clear contract - collection is read-only, application mutates
- **Safety**: Impossible to accidentally mutate during problem detection
- **Testability**: Each phase can be tested independently

## Key Algorithms

### Authorship Deduplication

Problem: Multiple resources may share the same authorship (e.g., "Jane Doe, Alice Jenkins").

Solution:

1. Maintain `auth_text_to_id: dict[str, int]` throughout tree traversal
2. When applying authorship to media element:
   - Join all authorship values with ", " separator
   - Check if this text already has an ID
   - If not, assign next sequential ID
   - Add `authorship-id="authorship_{id}"` attribute to media element
3. After tree traversal, create `<authorship>` definitions at root level
4. Each definition contains `<author>` child elements

Result: Shared authorships stored once at root, referenced by multiple resources.

### FIXME Value Detection

Problem: Need to distinguish between missing values and values that need manual correction.

Solution:

- Use "FIXME:" prefix for values that need correction
- `is_fixme_value()` checks for this prefix
- During extraction:
    - Multiple values: `"FIXME: Multiple X found. Choose one: A, B"`
    - Invalid license: `"FIXME: Invalid license: courtesy of museum"`
- During validation: FIXME values treated same as missing values
- During CSV reading: FIXME values converted back to None

Result: Clear distinction between "missing" and "needs correction" in CSV workflow.

### License Parsing

Problem: License strings come in many formats (`CC BY`, `CC-BY-4.0`, `http://rdfh.ch/licenses/cc-by-4.0`).

Solution:

- Use `xmllib.find_license_in_string()` to parse license text into standardized License enum
- If parsing fails, return `"FIXME: Invalid license: {text}"`
- In defaults, parse license string during `__init__()` to fail fast if invalid

Result: All licenses normalized to standard IRIs.

## Error Handling Strategy

### Iterative CSV Correction Workflow

1. **First run**: User provides property names and defaults
   - Command extracts metadata using priority system
   - Validates all values
   - If errors found: writes CSV with FIXME markers
   - No XML output created

2. **Manual correction**: User fixes CSV
   - Replaces FIXME markers with correct values
   - Can add missing values
   - Can choose between multiple values
   - **Important**: Can modify ANY column (not just FIXME ones) - see "CSV Override Behavior" below

3. **Second run**: User provides `--fixed_errors` flag
   - Command loads corrections from CSV
   - CSV corrections take highest priority
   - Validates again
   - If still errors: writes new CSV
   - If no errors: writes updated XML

4. **Repeat** until all errors resolved

### Validation Rules

A resource has problems if:

- License is None or FIXME value
- Copyright is None or FIXME value
- Authorships is empty list or contains FIXME value

Important: A resource must have ALL THREE components valid to avoid CSV export.

### CSV Override Behavior

**Critical implementation detail:**

When `--fixed_errors` is used, ALL non-None CSV values override XML properties and defaults for resources in that CSV.
This applies to every column, not just FIXME markers.

**Priority resolution in `_resolve_metadata_values()`:**

1. If CSV has non-None value: use it (skip XML extraction and defaults)
2. Else if XML has value: use it (skip defaults)
3. Else if defaults provided: use them
4. Else: None (triggers validation error)

**Note:** FIXME-prefixed values are converted to None during CSV reading, allowing fallback to XML/defaults.

### Error Messages

User-facing error messages:

- Missing property: Caught early in `_validate_flags()` with clear message
- Existing CSV: Suggests using `--fixed_errors` flag
- Invalid license default: Raised during `LegalMetadataDefaults.__init__()`
- FIXME markers in CSV: Provide context about what needs fixing

## Testing Considerations

### Unit Testing

Test each function in isolation:

- **Extraction functions**: Test with various XML structures (missing, single, multiple values)
- **Priority resolution**: Test all combinations of CSV/XML/defaults
- **FIXME detection**: Test all FIXME marker formats
- **CSV operations**: Test round-trip (write problems → read corrections)
- **Authorship deduplication**: Test ID assignment and reuse

### Integration Testing

Test file I/O and cross-module interactions:

- **Full workflow**: Input XML → CSV → corrected CSV → output XML
- **Property validation**: Missing properties raise correct error
- **Default values**: Applied when XML values missing
- **CSV overwrite protection**: Existing CSV prevents accidental overwrite

### E2E Testing

Test realistic scenarios:

- **Simple case**: All metadata present and valid
- **Missing values**: Some resources missing authorship/copyright/license
- **Invalid licenses**: Test "courtesy" and other invalid formats
- **Multiple values**: Resources with multiple copyright/license values
- **Shared authorships**: Multiple resources with same authorship
- **Iterative correction**: Multiple runs with CSV corrections

### Edge Cases

- Empty authorship text values (should be filtered out)
- Whitespace-only values (should be treated as empty)
- Resources without media elements (should be skipped)
- Both bitstream and iiif-uri present (first one used)
- Unicode in authorship names
- Very long authorship lists

## Common Pitfalls

1. **Forgetting `--fixed_errors` flag**: Command will refuse to overwrite existing CSV
2. **Not providing any property flags**: Caught early with validation error
3. **Property names with wrong namespace**: Caught early when no matches found
4. **Leaving FIXME markers in CSV**: Treated as missing values, triggers new CSV
5. **Invalid license default**: Fails during defaults initialization, not during execution

## Performance Considerations

- **Single-pass tree traversal**: All resources processed in one iteration
- **In-memory CSV**: Entire corrections CSV loaded into memory as dictionary
- **lxml XPath**: Efficient XPath queries for property extraction
- **Authorship deduplication**: O(1) lookup via dictionary
- **CSV sorting**: Results sorted by resource_id for easier navigation

For typical XML files (thousands of resources), performance should be near-instantaneous.

## Dependencies

- **lxml**: XML parsing and manipulation
- **pandas**: CSV I/O with proper column handling
- **xmllib**: License parsing utilities (`find_license_in_string()`)
- **dsp_tools.utils.xml_parsing**: XML parsing/validation utilities

## Future Improvements

Possible enhancements:

- Batch processing: Process multiple XML files at once
- Auto-detection: Try to guess property names from XML structure
- Validation preview: Show what would be changed without modifying XML
- Undo functionality: Revert XML back to text properties
- License suggestions: Use fuzzy matching for invalid licenses
