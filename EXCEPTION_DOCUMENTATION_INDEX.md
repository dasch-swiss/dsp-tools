# DSP-TOOLS Exception System Documentation Index

This directory contains comprehensive documentation of the DSP-TOOLS exception system, mapping out all custom exceptions, their usage patterns, and error handling flows.

## Documents Created

### 1. EXCEPTION_SYSTEM_SUMMARY.txt (Quick Reference - 156 lines)

**Purpose:** Quick lookup guide for the exception system

**Contents:**
- Exception locations and counts
- Exception hierarchy overview
- Key design principles
- How errors flow to users
- Exception catching patterns
- Problem collection pattern
- Common usage examples
- Inconsistencies noted
- Testing recommendations
- Patterns to follow

**Best for:** Getting up to speed quickly, finding patterns to follow

---

### 2. EXCEPTION_SYSTEM_MAP.md (Detailed Reference - 561 lines)

**Purpose:** Comprehensive map of the entire exception system

**Contents:**
- Complete exception class hierarchy with tree diagram
- Detailed definition of all 28 exception classes
- 5 custom warning classes
- Problem reporting models (4 main files)
- Exception raising locations (69 files across codebase)
- Exception catching patterns (30 files across codebase)
- Error message propagation to users
- Problem collection patterns
- Key design patterns explained
- Inconsistencies and improvement areas
- Testing considerations
- Summary statistics
- All referenced files

**Best for:** Understanding the full system, finding specific exceptions, seeing where they're used

---

### 3. EXCEPTION_FLOW_DIAGRAMS.md (Visual Guide - 477 lines)

**Purpose:** Visual flowcharts showing how exceptions work

**Contents:**
- Exception propagation and handling flow diagram
- Exception type selection by scenario
- Input validation exception flow
- Network request error handling
- Problem collection vs exception pattern
- Exception creation and consumption pipeline
- Exception type decision tree
- Exception message flow for user
- Exception conversion pattern example
- Complete exception inheritance diagram

**Best for:** Understanding control flow, seeing how exceptions are handled visually

---

## Statistics

| Metric | Value |
|--------|-------|
| Total documentation lines | 1,194 |
| Exception classes documented | 28 |
| Warning classes documented | 5 |
| Problem model files | 4 |
| Files raising exceptions | 69 |
| Files catching exceptions | 30 |
| Exception definition files | 3 |
| Visual diagrams | 10 |

---

## Exception System Overview

### Core Structure

All exceptions in DSP-TOOLS inherit from a single base exception `BaseError`, which itself inherits from Python's built-in `Exception` class. This creates a clean hierarchy that allows catching all DSP-TOOLS exceptions with `except BaseError:`.

### Main Exception Categories

1. **InputError** - User-provided data is invalid (fixable by user)
2. **InternalError** - System/software errors (not user's fault)
3. **PermanentConnectionError** - Cannot connect to DSP server
4. **XmlUploadError** - Issues during XML upload process
5. **ShaclValidationError** - Data validation problems
6. **Domain-specific** - Docker, API, file handling, etc.

### Error Flow to User

```
Code raises exception
    ↓
Propagates up call stack
    ↓
Caught in CLI entry_point.py
    ↓
Logged to file with full traceback
    ↓
User-friendly message printed in BOLD_RED
    ↓
Process exits with code 1
```

### Problem vs Exception Pattern

- **Exceptions:** Used for fatal conditions that stop processing immediately
- **Problems:** Used for non-fatal validation issues that are collected and reported together

---

## File Locations

### Exception Definitions
- `/src/dsp_tools/error/exceptions.py` - Main 25 exceptions
- `/src/dsp_tools/error/xmllib_errors.py` - xmllib-specific exceptions
- `/src/dsp_tools/error/custom_warnings.py` - General warning classes
- `/src/dsp_tools/error/xmllib_warnings.py` - xmllib warning classes

### Most Important Exception Usage Files
1. `/src/dsp_tools/cli/entry_point.py` - Top-level exception handler
2. `/src/dsp_tools/cli/utils.py` - Input validation exceptions
3. `/src/dsp_tools/clients/connection_live.py` - Network error handling
4. `/src/dsp_tools/clients/authentication_client_live.py` - Auth errors
5. `/src/dsp_tools/utils/request_utils.py` - Request timeout handling

### Problem Handling Files
- `/src/dsp_tools/commands/excel2json/models/input_error.py` - Excel problems
- `/src/dsp_tools/commands/validate_data/models/input_problems.py` - Validation problems
- `/src/dsp_tools/commands/create/models/input_problems.py` - Create command problems
- `/src/dsp_tools/commands/ingest_xmlupload/upload_files/input_error.py` - Upload file problems

---

## How to Use These Documents

### For Quick Reference
Start with **EXCEPTION_SYSTEM_SUMMARY.txt**
- Lists all exception locations
- Shows common usage patterns
- Provides quick lookup

### For Implementation
Read **EXCEPTION_SYSTEM_MAP.md**
- See where to raise specific exceptions
- Understand exception hierarchy
- Find relevant problem types
- See catching patterns

### For Understanding Flow
Study **EXCEPTION_FLOW_DIAGRAMS.md**
- Trace how exceptions propagate
- See type conversion patterns
- Understand decision points
- View complete inheritance tree

---

## Key Design Patterns

### Pattern 1: Layered Hierarchy
Different exception types communicate different meanings:
- User can fix: `InputError`
- System issue: `InternalError` or `PermanentConnectionError`
- Domain-specific: `XmlUploadError`, `ShaclValidationError`

### Pattern 2: Exception Conversion
Convert low-level exceptions to high-level user-friendly ones:
```python
except requests.RequestException:
    raise PermanentConnectionError(msg) from None
except PermanentConnectionError as e:
    raise InputError(e.message) from None
```

### Pattern 3: Problem Collection
Collect validation problems instead of raising immediately:
```python
problems = []
for item in items:
    if not validate(item):
        problems.append(Problem(...))
if problems:
    print_all_problems(problems)
    return False
```

### Pattern 4: Color-Coded Output
- Errors: BOLD_RED
- Warnings: YELLOW
- Default: RESET_TO_DEFAULT

### Pattern 5: Comprehensive Logging
All exceptions logged with:
1. Full traceback to log file
2. User message to stdout
3. Process exit code 1

---

## Common Tasks

### I want to add a new exception type
1. Define it in `/src/dsp_tools/error/exceptions.py`
2. Make it inherit from appropriate base (usually `BaseError` or specific category)
3. Update the hierarchy diagram in `EXCEPTION_SYSTEM_MAP.md`
4. Document where it's used

### I want to understand how errors reach users
Read "Error Message Propagation to Users" section in `EXCEPTION_SYSTEM_MAP.md`

### I want to add error handling to my function
See "Exception Catching Patterns" in `EXCEPTION_SYSTEM_MAP.md` for examples

### I want to know what exception to raise
Use the decision tree in `EXCEPTION_FLOW_DIAGRAMS.md` (Diagram 7)

### I want to understand a specific exception
Look it up in the table in `EXCEPTION_SYSTEM_MAP.md` - all 28 exceptions are listed with purpose and usage

---

## Inconsistencies Found

1. **Construction inconsistency** - Should use keyword args consistently
2. **Problem protocol** - Used heavily in excel2json, inconsistently elsewhere
3. **Catch-all exceptions** - May catch KeyboardInterrupt unintentionally
4. **Documentation gaps** - Some commands don't list all exception types in docstrings
5. **Re-raising patterns** - Vary between exception conversion and passthrough

---

## Testing Recommendations

- Test each exception type is raised in correct conditions
- Test exception messages are user-friendly
- Test exception propagation through call stack
- Test error recovery and state after exception
- Test Problem collection and aggregation
- Test color formatting of output

---

## Quick Statistics

| Type | Count |
|------|-------|
| Exception classes | 28 |
| Warning classes | 5 |
| Exception files | 3 |
| Problem model files | 4 |
| Raising locations | 69 files |
| Catching locations | 30 files |
| Main patterns | 5 |
| Design principles | 5 |

---

## Related Documentation

See the following for additional context:
- `/CLAUDE.md` - Project-specific guidelines
- `/src/dsp_tools/error/` - Source code for exceptions
- `/src/dsp_tools/cli/entry_point.py` - Where user sees errors
- Test files for exception handling examples

---

## Document Maintenance

Last updated: 2024-10-29

These documents should be updated when:
- New exception types are added
- Exception hierarchy changes
- Error handling patterns change
- Problems with error messages are discovered
- New inconsistencies are found

---

## How to Read the Documents

### EXCEPTION_SYSTEM_SUMMARY.txt
Plain text, easy to grep and search. Best for quick lookups. Contains minimal formatting.

### EXCEPTION_SYSTEM_MAP.md  
Markdown format with tables and code blocks. Contains detailed information. Use GitHub preview for best formatting.

### EXCEPTION_FLOW_DIAGRAMS.md
Markdown format with ASCII diagrams. Shows processes and flows. Best viewed in terminal or GitHub to see ASCII art properly.

---

## Contact & Questions

If you have questions about the exception system:
1. Check the relevant document for your question
2. Search in `EXCEPTION_SYSTEM_MAP.md` for specific exception
3. Review `EXCEPTION_FLOW_DIAGRAMS.md` for flow questions
4. Look at actual code in `/src/dsp_tools/error/` for implementation details

---

