# Excel2JSON Module

This module converts Excel files into JSON project files for DSP-TOOLS.

## Module Structure

### Core Functions

- `excel2json/project.py` - Main entry point that orchestrates the conversion of Excel files to complete JSON project files
- `excel2json/properties.py` - Converts property definitions from Excel to JSON format
- `excel2json/resources.py` - Converts resource class definitions from Excel to JSON format
- `excel2json/json_header.py` - Processes project metadata from Excel
- `excel2json/lists.py` - Handles list definitions (hierarchical vocabularies)

### Models

- `models/ontology.py` - Data models for ontology elements (OntoProperty, OntoResource, etc.)
- `models/json_header.py` - Data models for project header information
- `models/input_error.py` - Error handling and validation models
- `lists/models/` - Models specific to list processing

### Utilities

- `utils.py` - Shared utility functions for Excel processing
- `lists/utils.py` - List-specific utilities
- `lists/compliance_checks.py` - Validation logic for list structures

## Key Design Patterns

### Excel Processing Pipeline

1. **Read and Clean** - Excel files are read and cleaned using pandas
2. **Validate Structure** - Column presence and data integrity checks  
3. **Parse Rows** - Individual rows converted to model objects
4. **Serialize** - Model objects converted to JSON format
5. **Validate Output** - JSON schema validation against DSP specifications

### Error Handling

- Comprehensive error collection during parsing
- Position tracking for Excel cell-level error reporting
- Structured error models for different error types
- Non-blocking validation (collect all errors before failing)

### Optional Columns

- If the user has omitted optional Excel columns, the python code adds these columns to the pandas df,
  using the `add_optional_columns()` utility
- Missing optional columns are added as empty to maintain consistent DataFrame structure
- Optional fields in models are handled with `foo | None` types

## Testing Strategy

### Unit Tests

- Test individual parsing functions with minimal data
- Mock DataFrame inputs for isolated testing
- Test error conditions and edge cases
- Test model serialization/deserialization

### Integration Tests

- Test with real Excel files from testdata
- End-to-end conversion validation
- JSON schema compliance testing

## Column Processing Pattern

When adding new optional columns:

1. **Define Column** - Add column name to expected columns list
2. **Add to Optional** - Use `add_optional_columns()` to handle missing optional columns
3. **Parse in Row Handler** - Extract value in `_get_*_from_row()` functions
4. **Update Model** - Add field to corresponding dataclass model
5. **Serialize** - Include in `serialise()` method when present
6. **Test** - Unit and integration tests for new functionality

## Common Patterns

### Reading Excel Files

```python
df_dict = read_and_clean_all_sheets(excel_file)
df = add_optional_columns(df, optional_columns)
```

### Parsing Optional Values

```python
value = None if pd.isna(row["optional_column"]) else str(row["optional_column"]).strip()
```

### Model Serialization

```python
def serialise(self) -> dict[str, Any]:
    result = {"required_field": self.required_field}
    if self.optional_field:
        result["optional_field"] = self.optional_field
    return result
```
