# CLAUDE.md - xmllib Module

This file provides guidance to Claude Code when working with the `xmllib` module in dsp-tools.

## Module Overview

The `xmllib` module is the public API library for programmatic creation of DSP XML files.
It provides a type-safe, validated approach to generating XML data that conforms to DSP (DaSCH Service Platform) requirements.

## Architecture

### Core Components

#### Public API Layer (`__init__.py`)

- **Primary Interface**: All public functions and classes are exported here
- **Helper Functions**: Utilities for XML generation, validation, and formatting
- **Value Processing**: Checkers and converters for different data types

#### Models Layer (`models/`)

- **XMLRoot**: Main container for XML documents (`models/root.py`)
- **Resource**: Primary resource class for DSP resources (`models/res.py`)
- **DSP Base Resources**: Specialized resource types (`models/dsp_base_resources.py`)
- **Configuration**: Enums and options (`models/config_options.py`)
- **Licenses**: License definitions (`models/licenses/`)
- **Internal Models**: Value types and file models (`models/internal/`)

#### Utilities Layer

- **general_functions.py**: Public utility functions for XML creation
- **value_checkers.py**: Validation functions for data types
- **value_converters.py**: Data conversion utilities

#### Internal Layer (`internal/`)

- **checkers.py**: Type checking and input validation functions
- **input_converters.py**: Data conversion utilities for internal use
- **Serialization**: XML output generation (`serialise_resource.py`, `serialise_values.py`, `serialise_file_value.py`)
- **constants.py**: Constants used in several other files
- **type_aliases.py**: Type definitions and aliases
- **circumvent_circular_imports.py**: Place for functions that would produce a circular import error in other places

### Data Flow

```text
Raw Data → Validation → Resource Creation → XML Serialization
    ↓           ↓              ↓               ↓
Input Converters → Checkers → Models/Values → XML Output
    (internal/)   (internal/)      (models/)      (internal/)
```

## Key Classes and Usage Patterns

### XMLRoot - Document Container

```python
root = XMLRoot.create_new(shortcode="0000", default_ontology="onto")
root.add_resource(resource)
root.serialise_to_file("output.xml")
```

### Resource - Core Data Model

```python
resource = Resource.create_new(
    res_id="resource_1",
    restype=":Person",
    label="John Doe"
)
resource.add_simpletext(prop_name=":hasName", value="John Doe")
resource.add_date(prop_name=":hasBirthdate", value="GREGORIAN:CE:1990-01-01")
resource.add_integer(prop_name=":hasAge", value=33)
resource.add_link(prop_name=":hasPartner", value="resource_2")
```

### Specialized Resources

```python
# Region of Interest
region = RegionResource.create_new(
    res_id="region_1",
    label="ROI 1",
    region_of="image_1",
).add_rectangle(
    (0.5, 0.2),
    (0.1, 0.3),
)

# Video Segment
segment = VideoSegmentResource.create_new(
    res_id="segment_1",
    label="The second minute of the video",
    segment_of="video_1",
    segment_start="60",
    segment_end="120"
)
```

## Value Types and Validation

### Supported Value Types

- **SimpleText**: Plain text values
- **Richtext**: Formatted text with standoff markup
- **Integer**: Numeric integers
- **Decimal**: Floating point numbers
- **Boolean**: True/false values
- **Date**: Calendar dates with era and precision. Always as data range with start and end.
- **Time**: Timestamps
- **Color**: Hex color values
- **URI**: Web addresses and identifiers
- **Geoname**: Geographic location references, as geoname.org identifiers
- **List**: Controlled vocabulary values
- **Link**: References to other resources
- **File**: Multimedia file attachments

### Validation Functions

```python
# Check data types
date_value = reformat_date("1.1.1990", ".", None, DateFormat.DD_MM_YYYY)
assert is_date(date_value)

if is_bool_like("yes"):
    bool_value = convert_to_bool_string("yes")

if is_color("#FF0000"):
    # Valid hex color
    pass
```

## Configuration Options

### Permissions

- `PROJECT_SPECIFIC_PERMISSIONS`: Use project defaults
- `OPEN`: Publicly accessible
- `RESTRICTED`: Only visible for project members
- `RESTRICTED_VIEW`: Only applicable for images: Publicly accessible,
  but users who are not project members see the image in lower resolution or with a watermark

### Date Formatting

- `DateFormat.YYYY_MM_DD`: ISO format (2023-12-31)
- `DateFormat.DD_MM_YYYY`: European format (31.12.2023)
- `DateFormat.MM_DD_YYYY`: US format (12/31/2023)

### Calendar Systems

- `Calendar.GREGORIAN`: Modern standard calendar
- `Calendar.JULIAN`: Julian calender, only used for historical dates
- `Calendar.ISLAMIC`: Islamic calendar

### Text Processing

- `NewlineReplacement.PARAGRAPH`: Convert linebreaks to `<p>` tags
- `NewlineReplacement.LINEBREAK`: Convert linebreaks to `<br>` tags
- `NewlineReplacement.NONE`: Preserve linebreaks as-is

## Rich Text and Standoff Markup

### Creating Links

```python
# Link to another resource
link_text = create_standoff_link_to_resource("target_resource_id", "link text")

# Link to external URI
uri_link = create_standoff_link_to_uri("https://example.com", "external link")

# Add to richtext
resource.add_richtext(prop_name=":hasDescription", value=f"See {link_text} for details")
```

### Footnotes

```python
# Create footnote
footnote = create_footnote_string("This is a footnote")
footnote_element = create_footnote_element("Footnote text")
resource.add_richtext(prop_name=":hasDescription", value=f"Rich text with a footnote: {footnote}")
```

## Error Handling

### Warning System

- **Input Warnings**: Non-fatal data issues with input data
- **Type Mismatches**: Automatic conversion with notification
- **Validation Failures**: Clear error messages with resource context

### Error Types

```python
# Warning for non-fatal issues
emit_xmllib_input_warning("Non-standard boolean value converted")

# Type mismatch warning
if not is_color(val):
    emit_xmllib_input_type_mismatch_warning(expected_type="color", value=val, res_id=resource_id, prop_name=prop_name)

# Input validation errors
raise_input_error(MessageInfo(f"Invalid date format: {date}", resource_id="res_1", prop_name=":hasDate"))
```

## Testing Approach

### Unit Tests (`test/unittests/xmllib`)

- Individual function validation
- Type checking verification
- Data conversion accuracy

### Integration Tests (`test/integration/xmllib`)

- Multi-resource XML generation
- Cross-module compatibility
- File I/O operations

## Common Patterns

### Resource Creation Pipeline

1. **Validate Input**: Use checker functions
2. **Convert Data**: Apply converters if needed
3. **Create Resource**: Instantiate with validated data
4. **Add Values**: Use typed `add_xyz()` methods
5. **Serialize**: Generate XML output

### Batch Processing

```python
# Process multiple resources
for data_row in dataset:
    resource = Resource.create_new(
        res_id=make_xsd_compatible_id(data_row['id']),
        restype=data_row['type'],
        label=clean_whitespaces_from_string(data_row['label'])
    )

    # Add values with validation
    for prop, value in data_row.items():
        if is_nonempty_value(value):
            resource.add_simpletext(prop_name=prop, value=str(value))

    root.add_resource(resource)
```

### List Value Processing

```python
# Work with controlled vocabularies
lookup = ListLookup(project_lists)
string_with_list_labels = "Label 1; Label 2"
nodes = get_list_nodes_from_string_via_list_name(
    string_with_list_labels="Label 1; Label 2",
    label_separator=";",
    list_name="list1",
    list_lookup=list_lookup,
)
assert nodes == ["node1", "node2"]
resource.add_list_multiple(prop_name=":hasColor", list_name="list1", values=list_nodes)
```

## Important Guidelines

### Type Safety

- Always use type hints in new code
- Leverage dataclass models for structured data
- Use validation functions before creating values

### Maintainability

- Follow existing patterns for new value types
- Add comprehensive docstrings for public functions
- Include validation logic with clear error messages

## Dependencies

### External

- `lxml`: XML processing and validation
- `pandas`: Data manipulation (NA handling)
- `regex`: Unicode-aware pattern matching
- `loguru`: Structured logging

### Internal

- `dsp_tools.error`: Warning and error system
- `dsp_tools.utils`: Data format utilities
- Type definitions and constants

## Migration Notes

When updating xmllib:

- Maintain backward compatibility in public API
- Add deprecation warnings before removing features
- Update type hints for new Python versions
- Ensure XML schema compliance is preserved
