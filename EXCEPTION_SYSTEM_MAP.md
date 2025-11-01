# DSP-TOOLS Exception System - Comprehensive Map

## Overview

The DSP-TOOLS codebase implements a well-structured exception hierarchy centered around `BaseError` and `InputError` classes. The exception system is designed to distinguish between errors that users can fix (InputError) and errors that are internal/technical (InternalError). Error messages are propagated to users through the CLI entry point with formatted output.

---

## Exception Class Hierarchy

```
Exception (Python built-in)
├── BaseError
│   ├── InternalError
│   ├── DockerNotReachableError
│   ├── DspApiNotReachableError
│   ├── InputError
│   │   ├── UserFilepathNotFoundError
│   │   ├── UserDirectoryNotFoundError
│   │   ├── JSONFileParsingError
│   │   └── DuplicateIdsInXmlAndId2IriMapping
│   ├── InvalidGuiAttributeError
│   ├── UnexpectedApiResponseError
│   ├── PermanentConnectionError
│   │   └── BadCredentialsError
│   ├── InvalidInputError
│   │   └── InvalidIngestFileNameError
│   ├── ShaclValidationCliError
│   ├── ShaclValidationError
│   ├── PermanentTimeOutError
│   ├── XmlUploadError
│   │   └── XmlUploadInterruptedError
│   ├── XmlInputConversionError
│   ├── Id2IriReplacementError
│   ├── XmlUploadPermissionsNotFoundError
│   ├── XmlUploadAuthorshipsNotFoundError
│   ├── XmlUploadListNodeNotFoundError
│   └── UnknownDOAPException
│
├── XmllibInputError (BaseError)
├── XmllibFileNotFoundError (BaseError)
└── XmllibInternalError (BaseError)

Warning (Python built-in)
├── DspToolsWarning (ABC)
│   ├── DspToolsUserWarning
│   └── DspToolsFutureWarning
│
└── XmllibUserInfoBase (Warning, ABC)
    ├── XmllibInputInfo
    └── XmllibInputWarning
```

---

## Exception Definitions

### Location: `/src/dsp_tools/error/exceptions.py`

#### Core Exception Classes

| Exception | Parent | Purpose | When Raised |
|-----------|--------|---------|------------|
| `BaseError` | `Exception` | Base exception for all DSP-TOOLS errors with dataclass fields and custom `__str__` method | Base class for all framework errors |
| `InternalError` | `BaseError` | Errors the user cannot solve; includes dev team contact info in message | Internal logic errors, unexpected states |
| `DockerNotReachableError` | `BaseError` | Docker is not running properly | When Docker health check fails |
| `DspApiNotReachableError` | `BaseError` | DSP-API could not be reached | When API health endpoint fails |
| `InputError` | `BaseError` | User input is invalid; message should be user-friendly | Invalid user-provided data |
| `InvalidGuiAttributeError` | `BaseError` | Invalid gui-attribute used | Invalid GUI attributes in input |
| `UnexpectedApiResponseError` | `BaseError` | API returned unexpected response | Unexpected API response format |

#### User File/Directory Errors (InputError subclass)

| Exception | Purpose | Constructor |
|-----------|---------|------------|
| `UserFilepathNotFoundError` | Filepath from user does not exist | `__init__(filepath: str \| Path)` |
| `UserDirectoryNotFoundError` | Directory from user does not exist | `__init__(directory: str \| Path)` |
| `JSONFileParsingError` | JSON file cannot be parsed | Message passed to parent |

#### Connection & API Errors

| Exception | Parent | Purpose |
|-----------|--------|---------|
| `PermanentConnectionError` | `BaseError` | All reconnection attempts to DSP have failed |
| `BadCredentialsError` | `PermanentConnectionError` | DSP-API doesn't accept provided credentials |
| `PermanentTimeOutError` | `BaseError` | Python timeout due to no response from DSP-API |
| `InvalidInputError` | `BaseError` | API responds with permanent error due to invalid input |

#### Upload-Related Errors

| Exception | Parent | Purpose |
|-----------|--------|---------|
| `XmlUploadError` | `BaseError` | Generic XML upload error |
| `XmlUploadInterruptedError` | `XmlUploadError` | XML upload was interrupted |
| `XmlInputConversionError` | `BaseError` | Error during XML input conversion |
| `Id2IriReplacementError` | `BaseError` | Internal ID could not be found in Id2Iri mapping |
| `DuplicateIdsInXmlAndId2IriMapping` | `InputError` | Resource ID exists in both mapping and new data |
| `InvalidIngestFileNameError` | `InvalidInputError` | INGEST rejected file due to its name |

#### Resource Lookup Errors

| Exception | Purpose |
|-----------|---------|
| `XmlUploadPermissionsNotFoundError` | Permission does not exist |
| `XmlUploadAuthorshipsNotFoundError` | Authorship ID does not exist |
| `XmlUploadListNodeNotFoundError` | List node does not exist |

#### Validation Errors

| Exception | Purpose |
|-----------|---------|
| `ShaclValidationCliError` | SHACL Docker command has problems |
| `ShaclValidationError` | Unexpected error during validation |

#### Other Errors

| Exception | Purpose |
|-----------|---------|
| `UnknownDOAPException` | DOAP cannot be parsed |

---

### Location: `/src/dsp_tools/error/xmllib_errors.py`

Specialized exceptions for the xmllib library:

| Exception | Purpose |
|-----------|---------|
| `XmllibInputError` | User provided invalid input to xmllib |
| `XmllibFileNotFoundError` | User provided filepath that does not exist |
| `XmllibInternalError` | Internal error in xmllib on which user has no influence |

All inherit from `BaseError`.

---

### Location: `/src/dsp_tools/error/custom_warnings.py`

Custom warning classes implementing `Warning` interface:

| Warning Class | Purpose |
|---------------|---------|
| `DspToolsWarning` | Abstract base with custom `showwarning()` method |
| `DspToolsUserWarning` | General user-facing warnings |
| `DspToolsFutureWarning` | Deprecation warnings |

---

### Location: `/src/dsp_tools/error/xmllib_warnings.py`

Custom warning classes for xmllib:

| Warning Class | Purpose |
|---------------|---------|
| `XmllibUserInfoBase` | Base with custom `showwarning()` method |
| `XmllibInputInfo` | Informational messages (printed in YELLOW) |
| `XmllibInputWarning` | Warning messages (printed in BOLD_RED) |

---

## Problem Reporting Models

Beyond exceptions, DSP-TOOLS uses structured "Problem" dataclasses for non-fatal error reporting:

### Location: `/src/dsp_tools/commands/excel2json/models/input_error.py`

- `PositionInExcel`: Tracks location in Excel (filename, sheet, column, row)
- `ExcelFileProblem`: Problems within a specific Excel file
- `ExcelSheetProblem`: Problems within a specific sheet
- Multiple specialized problem types: `MissingValuesProblem`, `DuplicatesInColumnProblem`, etc.

Implements `Problem` protocol with `execute_error_protocol() -> str` method.

### Location: `/src/dsp_tools/commands/validate_data/models/input_problems.py`

- `InputProblem`: Validation problems with problem type, severity (VIOLATION/WARNING/INFO)
- `SortedProblems`: Categorized validation results (violations, warnings, info)
- `UnknownClassesInData`: Tracks unknown resource classes
- `OntologyValidationProblem`: Ontology validation issues

---

## Exception Raising Locations

### Authentication & Connection (Clients)

**File: `/src/dsp_tools/clients/authentication_client_live.py`**
- Line ~43: `raise InputError(...)` - Invalid credentials
- Line ~45: `raise InputError(e.message)` - PermanentConnectionError re-raised as InputError
- Line ~51: `raise InputError(...)` - Cannot retrieve token

**File: `/src/dsp_tools/clients/connection_live.py`**
- Raises `PermanentConnectionError` - All reconnection attempts failed
- Raises `InvalidInputError` - API returns permanent error from invalid input

**File: `/src/dsp_tools/clients/legal_info_client_live.py`**
- Raises `BadCredentialsError` - Credentials invalid
- Raises `BaseError` - Unexpected response

**File: `/src/dsp_tools/clients/ontology_create_client_live.py`**
- Raises `UnexpectedApiResponseError` - Unexpected API response
- Raises `BadCredentialsError` - Insufficient credentials

**File: `/src/dsp_tools/clients/list_client_live.py`**
- Line: `raise InternalError(...)` - Request failed with status code

### CLI Entry Points

**File: `/src/dsp_tools/cli/entry_point.py`**
- Line 246: `raise InputError(...)` - Invalid DSP server URL

**File: `/src/dsp_tools/cli/utils.py`**
- Line 46: `raise UserFilepathNotFoundError(file_path)` - File doesn't exist
- Line 51: `raise UserDirectoryNotFoundError(dir_path)` - Directory doesn't exist
- Line 62: `raise DockerNotReachableError()` - Docker not running
- Line 80, 87: `raise DspApiNotReachableError(msg)` - API unreachable

**File: `/src/dsp_tools/cli/call_action_with_network.py`**
- Line ~115: `raise InputError(...)` - Invalid validation severity

### XML Upload

**File: `/src/dsp_tools/commands/xmlupload/xmlupload.py`**
- Raises `BaseError` - Permanent network/software failure
- Raises `InputError` - XML file is invalid
- Catches `PermanentConnectionError`, `PermanentTimeOutError`, `XmlUploadInterruptedError`

**File: `/src/dsp_tools/commands/xmlupload/project_client.py`**
- Raises upload-specific errors

### Project Creation

**File: `/src/dsp_tools/commands/project/create/project_create_all.py`**
- Catches `BaseError` at multiple levels for error reporting
- Catches `PermanentConnectionError` and `InvalidInputError`

**File: `/src/dsp_tools/commands/project/create/project_create_ontologies.py`**
- Catches `BaseError` for ontology creation failures

**File: `/src/dsp_tools/commands/project/create/project_create_lists.py`**
- Catches `BaseError` for list creation failures

### Data Validation

**File: `/src/dsp_tools/commands/validate_data/shacl_cli_validator.py`**
- Raises `ShaclValidationCliError` - Docker validation command problems

**File: `/src/dsp_tools/commands/validate_data/validate_data.py`**
- Raises `BaseError` - Unknown validation problem type
- Catches/handles validation results

### XML File Parsing

**File: `/src/dsp_tools/utils/xml_parsing/get_parsed_resources.py`**
- Raises various exceptions for XML parsing issues

**File: `/src/dsp_tools/utils/request_utils.py`**
- Line 186: `raise PermanentTimeOutError(msg)` - Timeout during request

### Excel Processing

**File: `/src/dsp_tools/commands/excel2json/project.py`**
- Raises exceptions for Excel processing errors

**File: `/src/dsp_tools/commands/excel2json/properties.py`**
- Raises exceptions for property parsing

**File: `/src/dsp_tools/commands/excel2json/resources.py`**
- Raises exceptions for resource parsing

---

## Exception Catching Patterns

### Top-Level Catch (CLI Entry Point)

**File: `/src/dsp_tools/cli/entry_point.py` lines 66-80**

```python
try:
    parsed_arguments = _derive_dsp_ingest_url(...)
    success = call_requested_action(parsed_arguments)
except BaseError as err:
    logger.exception(f"The process was terminated because of an Error: {err.message}")
    print(f"\n{BOLD_RED}The process was terminated because of an Error: {err.message}{RESET_TO_DEFAULT}")
    success = False
except Exception as err:  # noqa: BLE001 (blind-except)
    logger.exception(err)
    print(InternalError())
    success = False
```

**Pattern:**
- All DSP-TOOLS errors caught as `BaseError` → user-friendly message printed + logged
- Unexpected Python exceptions caught as `Exception` → `InternalError` message printed with dev contact info

### Command-Level Catches

**Pattern: Catch at command implementation level**

Commands typically:
1. Catch `BaseError` to log and handle gracefully
2. Allow specific exceptions to propagate for different handling
3. Example from `project_create_all.py`:
   ```python
   try:
       # operation
   except BaseError:
       # handle or re-raise
   except (PermanentConnectionError, InvalidInputError):
       # special handling
   ```

### Request Utility Catches

**File: `/src/dsp_tools/utils/request_utils.py`**
- Catches `ReadTimeout` and `TimeoutError` → raises `PermanentTimeOutError`

**File: `/src/dsp_tools/clients/connection_live.py`**
- Catches `RequestException` → raises `PermanentConnectionError` or `InvalidInputError` based on status code

---

## Error Message Propagation to Users

### Flow Diagram

```
raise SpecificError("message")
            ↓
        (propagate up)
            ↓
catch BaseError as err
            ↓
logger.exception(f"...{err.message}")  ← logged to file
            ↓
print(BOLD_RED + f"...{err.message}" + RESET_TO_DEFAULT)  ← printed to stdout
            ↓
sys.exit(1)  ← exit with error code
```

### Message Formatting

- **User-facing errors:** Formatted with ANSI colors
  - `BOLD_RED` for errors
  - `YELLOW` for warnings
  - RESET_TO_DEFAULT for normal text
  
- **Logged errors:** Full traceback in log file at path stored in `LOGGER_SAVEPATH`

- **InternalError special handling:**
  ```
  An internal error occurred.
  Please contact the dsp-tools development team with the following information:
    - Which command was used.
    - If applicable, any files that were used in conjunction with the command.
    - A text file with the terminal output copied into.
    - The log file at {LOGGER_SAVEPATH}.
  ```

### Error Message Characteristics

- **InputError messages:** Describe what user should fix
  - Examples: "The provided filepath does not exist: {filepath}"
  - Examples: "Invalid DSP server URL '{server}'"
  
- **BaseError messages:** Technical context plus suggestion
  - Examples: "API responded with status 500..."
  
- **InternalError messages:** Instructions to contact dev team

---

## Problem Collection Pattern

In addition to exceptions, DSP-TOOLS uses non-blocking problem collection for validation:

### Problem Protocol

```python
class Problem(Protocol):
    def execute_error_protocol(self) -> str:
        """Initiate all steps for problem communication with user"""
```

### Usage Pattern

1. **Collect problems** during validation/parsing (don't raise immediately)
2. **Aggregate problems** by type/severity
3. **Format problems** using `execute_error_protocol()`
4. **Display all problems** together to user
5. **Raise error** if critical problems exist

### Example: Validation Problems

- `InputProblem`: Individual validation violation
- `SortedProblems`: Categorized by severity (violations, warnings, info)
- `UnknownClassesInData`: Special handling for unknown classes

---

## Key Design Patterns

### Pattern 1: Layered Exception Hierarchy

**Purpose:** Different exception types communicate to different audiences

- **User-fixable:** `InputError` and subclasses
- **System issues:** `PermanentConnectionError`, `DockerNotReachableError`
- **Internal bugs:** `InternalError`
- **Domain-specific:** `XmlUploadError`, `ShaclValidationError`

### Pattern 2: Exception Conversion

**Pattern:** Catch lower-level exception → raise higher-level exception

Example from `authentication_client_live.py`:
```python
except PermanentConnectionError as e:
    raise InputError(e.message) from None  # Convert to user-facing error
```

### Pattern 3: Problem vs. Exception

**Exception:** Used for fatal conditions that stop processing

**Problem:** Used for non-fatal validation issues that are collected and reported together

### Pattern 4: Custom `__str__` Implementation

All DSP-TOOLS exceptions use dataclass with `message` field:
```python
@dataclass
class BaseError(Exception):
    message: str = ""
    
    def __str__(self) -> str:
        return self.message
```

This ensures `str(err)` returns the message, not the repr.

### Pattern 5: Logging and User Output

All exceptions logged at point of catch with:
1. `logger.exception()` - Full traceback to log file
2. `print()` - User-friendly message to stdout
3. Color coding for visual distinction

---

## Inconsistencies & Areas for Improvement

### 1. Exception Raising Without Context

**Issue:** Some exceptions raised without checking context
```python
raise InputError(msg)  # vs. should be InputError(message=msg) for dataclass
```
**Current:** Works because dataclass fields are positional, but inconsistent

### 2. Problem vs. Exception Usage

**Issue:** Excel processing uses Problem protocol, but other modules use exceptions
**Pattern:** Not consistently applied across all modules

### 3. Re-raising Pattern Inconsistency

**Observation:** Some code catches and re-raises with conversion:
```python
except PermanentConnectionError as e:
    raise InputError(e.message) from None
```

**Alternative pattern** sometimes used:
```python
except SomeError:
    raise  # let it propagate
```

### 4. Catch-All Pattern

**Current pattern in `entry_point.py`:**
```python
except Exception as err:  # BLE001 ignored (blind-except)
    print(InternalError())
```

**Issue:** Catches ALL exceptions including KeyboardInterrupt

### 5. Missing Exception Documentation

**Issue:** Some commands don't document all possible exceptions in docstrings
```python
def create_project(...) -> bool:
    """
    ...
    Raises:
        InputError: if the project cannot be created
        BaseError: if the input is invalid
    ...
    """
```

**Not exhaustive:** Doesn't list all specific BaseError subclasses

---

## Testing Considerations

### Exception Testing Patterns Used

1. **Test exception type:** `assert isinstance(exception, ExpectedError)`
2. **Test message content:** Check that error message contains expected text
3. **Test exception propagation:** Verify exception bubbles up from function calls
4. **Test error recovery:** Verify state after exception handling

### Recommended Test Coverage

- Each exception should have test that raises it
- Each catch block should test with specific exception types
- Error messages should be tested for user-friendliness
- Recovery mechanisms should be tested

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Custom exception classes | 28 |
| Exception definitions files | 3 |
| Files raising exceptions | 69 |
| Files catching exceptions | 30 |
| Problem model files | 4 |
| Warning classes | 5 |

---

## Files Referenced

### Exception Definitions
- `/src/dsp_tools/error/exceptions.py` - Main exception definitions
- `/src/dsp_tools/error/xmllib_errors.py` - xmllib-specific exceptions
- `/src/dsp_tools/error/custom_warnings.py` - General warning classes
- `/src/dsp_tools/error/xmllib_warnings.py` - xmllib warning classes
- `/src/dsp_tools/error/problems.py` - Problem protocol definition

### Exception Usage
- `/src/dsp_tools/cli/entry_point.py` - Top-level catch point
- `/src/dsp_tools/cli/utils.py` - Input validation and error checking
- `/src/dsp_tools/clients/` - Connection and authentication errors
- `/src/dsp_tools/commands/` - Domain-specific exception raising
- `/src/dsp_tools/utils/request_utils.py` - Request and timeout handling

### Problem Handling
- `/src/dsp_tools/commands/excel2json/models/input_error.py` - Excel problems
- `/src/dsp_tools/commands/validate_data/models/input_problems.py` - Validation problems
- `/src/dsp_tools/commands/create/models/input_problems.py` - Create command problems
- `/src/dsp_tools/commands/ingest_xmlupload/upload_files/input_error.py` - Upload file problems

