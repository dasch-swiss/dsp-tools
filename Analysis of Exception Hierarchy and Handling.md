# Analysis of Exception Hierarchy and Handling

**Date:** 2025-11-07
**Updated:** 2026-01-29
**Scope:** Analysis of exception handling across DSP-TOOLS codebase with improvement recommendations

## Proposed Steps

1. ✅ Nora reviews this document
    - Some recently added error classes are not considered yet in this report,
      but this should not hinder us discussing this report.
2. ✅ Based on the feedback, Johannes fine-tunes this document
3. ✅ Johannes creates a project and tickets
    - Implementation order:
        - ✅ Hierarchy redesign (InputError→UserError, exception separation)
        - Concrete issues in error handling (easily fixable in 1 PR each)
        - Add Architecture Documentation
        - Error Message Quality - More Involved

---

## Implementation Status

### Major Refactorings Completed (January 2026)

The following major changes from Section 2 have been **successfully implemented**:

1. **✅ InputError renamed to UserError** (commit ce758a4a, Jan 2026)
   - All occurrences of `InputError` class removed
   - All references updated to `UserError` throughout the codebase
   - Reflects broader scope beyond just input validation issues

2. **✅ Exception separation to command-specific files** (commit 9f216006, Jan 2026)
   - Affected 99 files across the codebase
   - Each command module now has its own `exceptions.py` file:
     - `src/dsp_tools/cli/exceptions.py`
     - `src/dsp_tools/clients/exceptions.py`
     - `src/dsp_tools/utils/exceptions.py`
     - `src/dsp_tools/commands/create/exceptions.py`
     - `src/dsp_tools/commands/excel2json/exceptions.py`
     - `src/dsp_tools/commands/get/exceptions.py`
     - `src/dsp_tools/commands/ingest_xmlupload/exceptions.py`
     - `src/dsp_tools/commands/start_stack/exceptions.py`
     - `src/dsp_tools/commands/update_legal/exceptions.py`
     - `src/dsp_tools/commands/validate_data/exceptions.py`
     - `src/dsp_tools/commands/xmlupload/exceptions.py`
     - `src/dsp_tools/xmllib/internal/exceptions.py`
   - Central [src/dsp_tools/error/exceptions.py](src/dsp_tools/error/exceptions.py) now contains only base classes
   - Achieved better modularity and separation of concerns

3. **✅ Base hierarchy structure established**
   - `BaseError` as root exception (dataclass with message attribute)
   - `UserError(BaseError)` for user-fixable errors
   - `InternalError(BaseError)` for errors requiring developer assistance
   - Additional base exceptions: `UnreachableCodeError`, `UserFilepathNotFoundError`, `UserDirectoryNotFoundError`, etc.

### Remaining Work

All items in **Section 3 (Concrete Issues)** and **Section 4 (Error Message Quality)** remain to be implemented:

- Section 3.1: ShaclCliValidator logging and error handling issues
- Section 3.2: _check_api_health() logging and control flow issues
- Section 3.3: UnknownDOAPException misuse of exceptions for control flow
- Section 3.4: Inconsistent message formatting ("ERROR:" prefixes)
- Section 3.5: Meta-tests for exception hierarchy
- Section 3.6: Bare BaseError raises (21 files)
- Section 3.7: Entry point exception handling improvements
- Section 3.8: Exception chain suppression (`from None` usage - 44 occurrences)
- Section 3.9: Duplicate error logging
- Section 3.10: PermanentTimeOutError cleanup
- Section 4: Error message quality improvements

---

## 1. Missing Architecture Documentation

**Current state:** No centralized documentation explaining:

- When to use exceptions vs Problem protocol
- How to choose between exception types
- Exception conversion patterns
- The two command groups and their error handling needs

**Recommendation:** Create guideline with:

1. Command grouping and error handling requirements
2. Decision tree for choosing exception types
3. When to catch vs. let fail
4. Standard patterns for exception conversion and logging
5. Guidelines for user-friendly error messages
6. Examples of good and bad error handling

--> **See the separate file `Draft for Error Handling Guideline.md`**

---

## 2. Exception Hierarchy Redesign

### ✅ IMPLEMENTED - Current Structure (as of January 2026)

The exception hierarchy has been successfully refactored:

- ✅ `InputError` has been renamed to `UserError` (broader scope: not just input problems)
- ✅ Clear distinction between user-fixable (`UserError`) and internal errors (`InternalError`) at the hierarchy level
- ✅ Exceptions have been distributed to command-specific files

The central [src/dsp_tools/error/exceptions.py](src/dsp_tools/error/exceptions.py) now only contains the base classes.
In every command package, there is an `exceptions.py` file with classes that inherit from the base classes.
The grouping by commands is achieved by the location of the file, not by inheritance. 

**Base exceptions** ([src/dsp_tools/error/exceptions.py](src/dsp_tools/error/exceptions.py)):

```text
BaseError                               # Root exception (dataclass with message attribute)
├── UserError                           # User can fix it themselves (renamed from InputError)
├── InternalError                       # Developer necessary to fix it
├── UnreachableCodeError                # For code paths that should never execute
├── UserFilepathNotFoundError(UserError)    # Generic file not found
├── UserDirectoryNotFoundError(UserError)   # Generic directory not found
├── PermanentConnectionError            # All reconnection attempts failed
├── PermanentTimeOutError               # Timeout from DSP-API
└── BadCredentialsError(UserError)      # Authentication failure
```

**Utils exceptions** ([src/dsp_tools/utils/exceptions.py](src/dsp_tools/utils/exceptions.py)):

```text
JSONFileParsingError(UserError)                 # Cannot parse JSON file
XsdValidationError(UserError)                   # XML validation failure
DuplicateIdsInXmlAndId2IriMapping(UserError)    # ID collision in mapping
MalformedPrefixedIriError(UserError)            # Invalid IRI format
DspToolsRequestException(BaseError)             # Request exception wrapper
```

**Note:** `UserFilepathNotFoundError` and `BadCredentialsError` are in the base exceptions file, not utils.

**CLI exceptions** ([src/dsp_tools/cli/exceptions.py](src/dsp_tools/cli/exceptions.py)):

```text
CliUserError(UserError)                 # Invalid CLI input
DockerNotReachableError(UserError)      # Docker not running
DspApiNotReachableError(UserError)      # API unreachable on localhost
```

**Note:** `UserDirectoryNotFoundError` is in the base exceptions file, not CLI.

**Clients exceptions** ([src/dsp_tools/clients/exceptions.py](src/dsp_tools/clients/exceptions.py)):

```text
FatalNonOkApiResponseCode(BaseError)    # Unexpected API response
InvalidInputError(UserError)            # API rejected input data
ProjectOntologyNotFound(UserError)      # No ontologies in project
ProjectNotFoundError(UserError)         # Project doesn't exist
```

**Create command** ([src/dsp_tools/commands/create/exceptions.py](src/dsp_tools/commands/create/exceptions.py)):

```text
ProjectJsonSchemaValidationError(UserError)     # JSON schema validation failed
CircularOntologyDependency(UserError)           # Circular dependencies detected
UnableToCreateProjectError(InternalError)       # Project creation failed
```

**Excel2JSON command** ([src/dsp_tools/commands/excel2json/exceptions.py](src/dsp_tools/commands/excel2json/exceptions.py)):

```text
InvalidFolderStructureError(UserError)      # Bad folder structure
InvalidFileFormatError(UserError)           # File format doesn't match expected
InvalidFileContentError(UserError)          # Invalid content in file
InvalidGuiAttributeError(UserError)         # Invalid GUI attribute
InvalidListSectionError(UserError)          # List section validation failed
```

**Get command** ([src/dsp_tools/commands/get/exceptions.py](src/dsp_tools/commands/get/exceptions.py)):

```text
UnknownDOAPException(InternalError)         # Cannot parse DOAP
```

**Ingest XMLUpload command** ([src/dsp_tools/commands/ingest_xmlupload/exceptions.py](src/dsp_tools/commands/ingest_xmlupload/exceptions.py)):

```text
NoIngestFileFound(UserError)                # No files uploaded for ingest
InvalidIngestInputFilesError(UserError)     # Invalid filepaths
IngestIdForFileNotFoundError(UserError)     # File not in ingest mapping
IngestFailure(InternalError)                # Ingest call failed
```

**Start Stack command** ([src/dsp_tools/commands/start_stack/exceptions.py](src/dsp_tools/commands/start_stack/exceptions.py)):

```text
StartStackInputError(InternalError)         # Invalid input to start stack
FusekiStartUpError(InternalError)           # Fuseki startup problem
```

**Update Legal command** ([src/dsp_tools/commands/update_legal/exceptions.py](src/dsp_tools/commands/update_legal/exceptions.py)):

```text
InvalidInputFileFormat(UserError)           # Input file format problem
LegalInfoPropertyError(UserError)           # Property issue
InvalidLicenseError(UserError)              # Cannot parse license string
```

**Validate Data command** ([src/dsp_tools/commands/validate_data/exceptions.py](src/dsp_tools/commands/validate_data/exceptions.py)):

```text
ShaclValidationCliError(InternalError)      # Docker command problems
ShaclValidationError(InternalError)         # Unexpected validation error
```

**XMLUpload command** ([src/dsp_tools/commands/xmlupload/exceptions.py](src/dsp_tools/commands/xmlupload/exceptions.py)):

```text
UnableToRetrieveProjectInfoError(BaseError)         # Cannot get project info
MultimediaFileNotFound(UserError)                   # Referenced files don't exist
InvalidIngestFileNameError(InvalidInputError)       # INGEST rejected filename
XmlUploadError(BaseError)                           # General xmlupload error
XmlUploadInterruptedError(XmlUploadError)           # Upload interrupted
XmlInputConversionError(InternalError)              # XML conversion failed
Id2IriReplacementError(UserError)                   # ID not found in mapping
XmlUploadPermissionsNotFoundError(UserError)        # Permission doesn't exist
XmlUploadAuthorshipsNotFoundError(UserError)        # Authorship doesn't exist
XmlUploadListNodeNotFoundError(UserError)           # List node doesn't exist
```

**xmllib module** ([src/dsp_tools/xmllib/internal/exceptions.py](src/dsp_tools/xmllib/internal/exceptions.py)):

```text
XmllibInputError(UserError)                 # Invalid user input
XmllibFileNotFoundError(UserError)          # File doesn't exist
XmllibInternalError(UserError)              # Internal xmllib error
```



---

## 3. Concrete issues in error handling (easily fixable in 1 PR each)

**Note:** While major refactoring work (Section 2) has been completed, the specific issues identified below
remain unaddressed and should be fixed as described.

### 3.1 ShaclCliValidator Issues

Multiple issues in `ShaclCliValidator.validate()`:

1. **Incorrect error message**: Says Docker is not running, but this is already checked in
   `cli/utils.py` > `check_docker_health()`
2. **Uses `logger.error()` instead of `logger.exception()`**: Loses stack trace information
3. **Uses `logger.error()` twice**: Redundant logging
4. **Raises with `from None`**: Original error is lost

**Recommendation:**

- Remove Docker check error (already handled upstream)
- Use `logger.exception()` to preserve context
- Consolidate logging to single call
- Replace `ShaclValidationCliError` with `ShaclValidationError` as `InternalError` subclass
- Use `from e` or `logger.exception()` + `from None` pattern

### 3.2 `_check_api_health()` (`src/dsp_tools/cli/utils.py`) issues

- `if not response.ok`  should be moved out of the try-except block
- except block uses `logger.error()` twice
    - remove `logger.error(e)`
    - `logger.error(msg)` -> `logger.exception(msg)`
- remove `from None`

### 3.3 UnknownDOAPException - Exception Misuse

- Legacy projects have custom DOAP combinations that don't fit the current limited system
- When downloading existing projects, these legacy DOAPs must be handled gracefully
- A sensible fallback exists (write default text to JSON)
- This is **expected behavior**, not an exceptional condition

**The Problem:** This is a textbook case of **exception misuse**.

Exceptions should represent **unexpected errors**, not **expected alternative outcomes**.
Using exceptions for control flow in expected scenarios is an anti-pattern that makes code harder to reason about.

Current Code (problematic):

```python
def parse_doap(...) -> str:
    if not recognized:
        raise UnknownDOAPException("Cannot parse DOAP")
    return doap_string

# Calling code
try:
    doap = parse_doap(...)
except UnknownDOAPException:
    doap = DEFAULT_DOAP_TEXT
```

Recommended Approach - Result Type:

```python
@dataclass
class DOAPResult:
    value: str
    is_legacy: bool

def parse_doap(...) -> DOAPResult:
    if not recognized:
        return DOAPResult(value=DEFAULT_DOAP_TEXT, is_legacy=True)
    return DOAPResult(value=doap_string, is_legacy=False)

# Calling code (explicit and type-safe)
result = parse_doap(...)
if result.is_legacy:
    logger.info("Using default DOAP for legacy project")
doap = result.value
```

### 3.4: Inconsistent Message Formatting

**Problem:** Some messages include "ERROR:" prefix, others don't.

**Recommendation:** Remove all "ERROR:" prefixes from exception messages. The red color and context
already indicate it's an error.

Replace: `raise FooError("ERROR: foobar")`
With: `raise FooError("foobar")`

Optionally, the error class can add the ERROR prefix during serialization.

### 3.5 Add Meta-Tests for Exception Hierarchy

**Recommendation:** Add tests ensuring:

- All custom exceptions inherit from `BaseError`
- All exceptions have proper `__str__` behavior
- Messages don't have redundant "ERROR:" prefixes
- Exception hierarchy matches documentation

```python
def test_all_exceptions_inherit_from_base_error():
    """Ensure all custom exceptions inherit from BaseError."""
    for exc_class in get_all_exception_classes():
        assert issubclass(exc_class, BaseError)

def test_exception_messages_dont_have_error_prefix():
    """Ensure exception messages don't include 'ERROR:' prefix."""
    for exc_class in get_all_exception_classes():
        # Test with sample instances where possible
        pass
```

### 3.6. Do Not Raise Bare BaseError

Multiple locations raise raw `BaseError`:

- [date_util.py:46](src/dsp_tools/utils/data_formats/date_util.py#L46): `raise BaseError(f"Invalid calendar type: {s}")`
- [json_parsing.py:33](src/dsp_tools/utils/json_parsing.py#L33): `raise BaseError("Invalid input: ...")`
- [make_values.py:191](src/dsp_tools/commands/xmlupload/make_rdf_graph/make_values.py#L191)

**Problem:** Raising raw `BaseError` defeats the purpose of having a hierarchy. Cannot catch specific exception types.

**Recommendation:** Use specific exceptions


### 3.7. Improve Entry Point Exception Handling

Update `entry_point.py` > `run()`:

```python
try:
    parsed_arguments = _derive_dsp_ingest_url(...)
    success = call_requested_action(parsed_arguments)
except KeyboardInterrupt:
    logger.info("User interrupted execution")
    sys.exit(130)  # Standard exit code for SIGINT
except UserError as err:
    logger.exception(f"User error: {err.message}")
    print(f"\n{BOLD_RED}Error: {err.message}{RESET_TO_DEFAULT}")
    success = False
except Exception as err:  # Catches InternalError and all unexpected exceptions
    logger.exception("Internal error occurred")
    print(InternalError(custom_msg=str(err) if not isinstance(err, InternalError) else None))
    success = False
```

Key improvements:

1. **Add `KeyboardInterrupt` handler**: Prevent treating Ctrl+C as an internal error
2. **Catch `UserError` first**: Handle user-fixable errors with appropriate messaging
3. **Catch broad `Exception`**: Converts all unexpected exceptions to `InternalError`


### 3.8. Do Not Suppress Exception Chain

Found extensive use of `from None`:

```python
except PermanentConnectionError as e:
    raise UserError(e.message) from None  # Suppresses traceback chain
```

**Locations:** 20+ across the codebase

**Problem:** Using `from None` suppresses exception chains, losing valuable debugging information.

**When appropriate:**

- Converting low-level exceptions to user-friendly messages where technical details aren't relevant
- After using `logger.exception()` to preserve context in logs

**When problematic:**

- Converting between DSP-TOOLS exceptions
- In development/debugging scenarios

**Recommendation:**

- Use `from e` for DSP-TOOLS-to-DSP-TOOLS conversions
- Use `logger.exception()` + `from None` when presenting clean user errors but preserving log context
- Reserve `from None` alone for converting third-party exceptions to user messages



### 3.9 Duplicate Error Logging

**Problem:** The codebase has several locations where the same error is logged multiple times:
once when the exception is caught and logged, and again when the exception is re-raised and caught by a caller.
This creates duplicate log entries that clutter logs and make debugging harder.

**Examples:**

1. **`cli/utils.py` → `entry_point.py` chain:**
   - In [cli/utils.py:79-87](_check_api_health() function):
     - Catches exception, logs with `logger.error(e)` and `logger.error(msg)`
     - Raises `DspApiNotReachableError(msg)`
   - In [entry_point.py:73-74](run() function):
     - Catches all `BaseError` exceptions (which includes `DspApiNotReachableError`)
     - Logs again with `logger.exception(f"The process was terminated because of an Error: {err.message}")`
   - **Result:** Same error logged 2-3 times

2. **`shacl_cli_validator.py`:**
   - In [shacl_cli_validator.py:22-29](ShaclCliValidator.validate()):
     - Logs with `logger.error(e)` at line 22
     - Logs again with `logger.error(msg)` at line 28
     - Raises `ShaclValidationCliError`
   - In [entry_point.py:73-74](run() function):
     - Catches and logs the `ShaclValidationCliError` again
   - **Result:** Same error logged 3 times

3. **`json_parsing.py`:**
   - In [json_parsing.py:44-46](parse_json_file()):
     - Logs with `logger.error(e)` at line 44
     - Raises `JSONFileParsingError(msg)` at line 46
   - Likely caught and logged again by caller through `entry_point.py`
   - **Result:** Same error logged twice

4. **`xmlupload/stash/` modules:**
   - In [upload_stashed_xml_texts.py:47-51](upload_xml_texts()):
     - Catches `BaseError`, calls helper function that logs
     - Returns failure status that may trigger additional logging
   - Similar pattern in [upload_stashed_xml_texts.py:120-124](_upload_stash_item())

**Recommendation:**

Follow a consistent pattern:

- **Log at the highest level only:** Let exceptions bubble up to `entry_point.py` where they are logged once
- **Intermediate handlers should NOT log:** If catching and re-raising, don't log—just transform the exception if needed
- **Use `from e` for chaining:** Preserve the exception chain instead of using `from None`

**Exception:** Only log at intermediate levels when:

- Converting to user-friendly error and using `logger.exception()` + `from None` pattern
- The intermediate handler truly has additional context worth logging



### 3.10 Get rid of unnecessary PermanentTimeOutError

In the Connection class, the builtins TimeoutError and ReadTimeout are logged and converted into PermanentTimeOutError.
The xmlupload code adds some text, and then exits Python via a XmlUploadInterruptedError.
For this, we don't need an own class. The xmlupload can also catch and handle the builtins directly.

---

## 4. Error Message Quality - More Involved

Technical Jargon in User-Facing Errors, e.g.:

- "OntologyConstraintException" (too technical)
- "INGEST rejected file due to its name" (what's INGEST? What's wrong with the name?)

**Recommendation:** Use plain language and explain what users need to do.

Missing Actionable Guidance: Many errors state **what** went wrong but not **how** to fix it:

```python
# Current
raise UserError(f"{data_model_files} is not a directory.")

# Better
raise UserError(
    f"Expected '{data_model_files}' to be a directory, but found a file. "
    f"Please provide a directory path containing Excel files."
)
```

**Recommendation:** All user-facing errors should:

1. State what was expected
2. State what was found
3. Suggest how to fix it
