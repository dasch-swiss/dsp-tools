# Analysis of Exception Hierarchy and Handling

**Date:** 2025-11-07
**Updated:** 2026-03-24
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
        - ✅ Add Architecture Documentation
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

### Further Changes (March 2026)

4. **✅ Error Handling Guideline published** (PR #2225, March 2026)
   - Published at [docs/developers/architecture/error-handling.md](docs/developers/architecture/error-handling.md)
   - Referenced in CLAUDE.md

5. **✅ Section 3.11: BaseError hierarchy violations resolved** (PR #2224, March 2026)
   - `UnreachableCodeError` → reclassified as `UnreachableCodeError(InternalError)`
   - `PermanentConnectionError` → reclassified as `PermanentConnectionError(InternalError)`
   - `PermanentTimeOutError` → reclassified as `PermanentTimeOutError(InternalError)`
   - `FatalNonOkApiResponseCode` → reclassified as `FatalNonOkApiResponseCode(InternalError)` in `clients/`
   - `DspToolsRequestException` → reclassified as `DspToolsRequestException(InternalError)` in `utils/`
   - `UnableToRetrieveProjectInfoError`, `XmlUploadError` → reclassified as `InternalError` in `xmlupload/`
   - `MigrationExportFailureError`, `MigrationDownloadFailureError`, `MigrationImportFailureError`
     → reclassified as `InternalError` in `commands/migration/`

6. **✅ Section 3.6 (partial): Bare `InternalError`/`UserError` raises removed from active code** (PR #2226, March 2026)
   - `create.py`: `raise InternalError(...)` → `raise UnreachableCodeError(...)`
   - `server_project_info.py`: three bare `raise InternalError(...)` → `raise UnableToCreateProjectError(...)`
   - `shacl_cli_validator.py`: three bare `raise InternalError(...)` → `raise ShaclValidationError(...)`

### Remaining Work

The following items in **Section 3 (Concrete Issues)** and **Section 4 (Error Message Quality)** remain to be implemented:

- ✅ Section 3.1: ShaclCliValidator logging and error handling issues (**COMPLETED** - January 2026)
- ✅ Section 3.2: _check_api_health() logging and control flow issues (**COMPLETED** - January 2026)
- Section 3.3: UnknownDOAPException misuse of exceptions for control flow
- Section 3.4: Inconsistent message formatting ("ERROR:" prefixes)
- Section 3.5: Meta-tests for exception hierarchy
- Section 3.6: Bare `BaseError` raises in non-legacy, actively maintained code (remaining after PR #2226):
    - `ark2iri.py` (3 occurrences)
    - `make_values.py:191`
    - `get.py:96`
    - `reformat_validation_results.py:62`
    - `excel2json/project.py:252`
- Section 3.7: Entry point exception handling improvements (missing KeyboardInterrupt handler)
- Section 3.8: Exception chain — converting vs. propagating (`from None` usage - ~30 occurrences across ~17 files)
- Section 3.9: Duplicate error logging
- Section 3.10: PermanentTimeOutError cleanup
- ✅ Section 3.11: Hierarchy violations (**COMPLETED** - PR #2224, March 2026)
- ✅ Section 2 hierarchy update: BaseError violations resolved (PR #2224);
  `XmllibInternalError(UserError)` naming bug in `xmllib/internal/exceptions.py` still remains
- Section 4: Error message quality improvements

---

## 1. Architecture Documentation

**✅ COMPLETED (March 2026)** — The guideline has been published at
[docs/developers/architecture/error-handling.md](docs/developers/architecture/error-handling.md).

It covers:

1. Command grouping and error handling requirements
2. Decision tree for choosing exception types
3. When to catch vs. let fail
4. Standard patterns for exception conversion and logging
5. Guidelines for user-friendly error messages
6. Anti-patterns table with fixes

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
│   ├── UserFilepathNotFoundError       # Generic file not found
│   ├── UserFilepathMustNotExistError   # Filepath already exists (but shouldn't)
│   ├── UserDirectoryNotFoundError      # Generic directory not found
│   └── BadCredentialsError            # Authentication failure
└── InternalError                       # Developer necessary to fix it
    ├── UnreachableCodeError            # For code paths that should never execute
    ├── PermanentConnectionError        # All reconnection attempts failed
    └── PermanentTimeOutError           # Timeout from DSP-API
```

**Utils exceptions** ([src/dsp_tools/utils/exceptions.py](src/dsp_tools/utils/exceptions.py)):

```text
JSONFileParsingError(UserError)                 # Cannot parse JSON file
XsdValidationError(UserError)                   # XML validation failure
DuplicateIdsInXmlAndId2IriMapping(UserError)    # ID collision in mapping
MalformedPrefixedIriError(UserError)            # Invalid IRI format
DspToolsRequestException(InternalError)         # Request exception wrapper
```

**Note:** `UserFilepathNotFoundError` and `BadCredentialsError` are in the base exceptions file, not utils.

**CLI exceptions** ([src/dsp_tools/cli/exceptions.py](src/dsp_tools/cli/exceptions.py)):

```text
CliUserError(UserError)                             # Invalid CLI input
├── CliCommandNotInvokableError(CliUserError)       # Command not usable with this configuration
DockerNotReachableError(UserError)                  # Docker not running
DspApiNotReachableError(UserError)                  # API unreachable on localhost
```

**Note:** `UserDirectoryNotFoundError` is in the base exceptions file, not CLI.

**Clients exceptions** ([src/dsp_tools/clients/exceptions.py](src/dsp_tools/clients/exceptions.py)):

```text
FatalNonOkApiResponseCode(InternalError)            # Unexpected API response
InvalidInputError(UserError)                        # API rejected input data
ProjectOntologyNotFound(UserError)                  # No ontologies in project
ProjectNotFoundError(UserError)                     # Project doesn't exist
MigrationExportExistsError(UserError)               # Export for project already exists
MigrationImportExistsError(UserError)               # Import for project already exists
MigrationExportImportInProgressError(UserError)     # Export or import is in progress
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
UnableToRetrieveProjectInfoError(InternalError)     # Cannot get project info
MultimediaFileNotFound(UserError)                   # Referenced files don't exist
InvalidIngestFileNameError(InvalidInputError)       # INGEST rejected filename
XmlUploadError(InternalError)                       # General xmlupload error
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

**Migration command** ([src/dsp_tools/commands/migration/exceptions.py](src/dsp_tools/commands/migration/exceptions.py)):

```text
InvalidMigrationConfigFile(UserError)               # Provided config file is invalid
MigrationReferenceInfoIncomplete(UserError)         # Required field in migration reference file is missing
MigrationExportFailureError(InternalError)          # Migration export failed
MigrationDownloadFailureError(InternalError)        # Download of migration zip failed
MigrationImportFailureError(InternalError)          # Import of migration zip failed
```

### ✅ Hierarchy Drift: Resolved (PR #2224, March 2026)

All direct `BaseError` subclasses that violated the guideline have been reclassified
(see Implementation Status item 5). The hierarchy in `src/dsp_tools/error/exceptions.py`
now matches the guideline exactly.

**Remaining naming bug (open):**

- `XmllibInternalError(UserError)` in `xmllib/internal/exceptions.py`:
  the name implies `InternalError` classification but the type inherits `UserError`.
  Either rename it to match the `UserError` semantics, or reclassify it as `InternalError`.
  Tracked as part of Section 3.11 in the Remaining Work list above.

---

## 2b. Command Groups

The guideline classifies all commands into two groups with different error handling requirements.

### Group A — Fail-fast acceptable

Commands: `create`, `get`, `xmlupload`, `upload-files`, `ingest-files`, `ingest-xmlupload`, `resume-xmlupload`

These commands run in controlled environments. Developer assistance is acceptable when something goes wrong.
Errors may escalate with a full traceback.

### Group B — Must be fixable by the user

Commands: `excel2json`, `excel2lists`, `excel2resources`, `excel2properties`, `old-excel2json`,
`old-excel2lists`, `id2iri`, `update-legal`, `validate-data`, `start-stack`, `stop-stack`

`xmllib` is also Group B, but as a **library**, not a CLI command. Its aggregated reporting requirement
applies to validation helpers, which collect all problems before raising a single `UserError`.

`start-stack` / `stop-stack` can fail for reasons outside the user's control (Docker not running,
port conflicts). Those failures present as `InternalError`-grade messages instructing the user to
contact the development team.

All problems must be reported in an aggregated, user-friendly way.
Users must be able to resolve everything without contacting developers.

**Aggregated error reporting (Group B):**

Group B commands must not raise on the first problem — they must collect all problems and report them together.

Pattern:

1. Represent each problem as a `@dataclass(frozen=True)` with an `execute_error_protocol() -> str` method
   that returns a formatted, human-readable description.
2. Collect all problem instances into a list during processing (do not raise immediately).
3. After processing, aggregate the messages into a single `UserError` subclass and raise it once.

**Implications for open issues:**

- Section 3.3 (UnknownDOAPException): `get` is Group A — fail-fast is acceptable.
  But exception-as-control-flow is still wrong when a sensible fallback exists, regardless of group.
- Section 3.7 (entry point): `entry_point.py` `run()` is the top-level handler for both groups.

---

## 3. Concrete issues in error handling (easily fixable in 1 PR each)

**Note:** While major refactoring work (Section 2) has been completed, the specific issues identified below
remain unaddressed and should be fixed as described.

### 3.1 ShaclCliValidator Issues

**✅ COMPLETED (January 2026)** - All issues in this section have been fixed.

**What was implemented:**

- Enhanced `ShaclValidationCliError` to store diagnostic data (returncode, stderr)
- Updated exception handler to use `logger.exception()` instead of `logger.error()` - preserves stack trace
- Removed redundant logging (consolidated to single call)
- Removed `from None` to keep exception chain intact
- Error message now includes exit code and stderr output

**Original issues** (for reference):

Multiple issues in `ShaclCliValidator.validate()`:

1. **Incorrect error message**: Says Docker is not running, but this is already checked in
   `cli/utils.py` > `check_docker_health()`
2. **Uses `logger.error()` instead of `logger.exception()`**: Loses stack trace information
3. **Uses `logger.error()` twice**: Redundant logging
4. **Raises with `from None`**: Original error is lost

**Original recommendation** (for reference):

- Remove Docker check error (already handled upstream)
- Use `logger.exception()` to preserve context
- Consolidate logging to single call
- Replace `ShaclValidationCliError` with `ShaclValidationError` as `InternalError` subclass
- Use `from e` or `logger.exception()` + `from None` pattern

### 3.2 `_check_api_health()` (`src/dsp_tools/cli/utils.py`) issues

**✅ COMPLETED (January 2026)** - All issues in this section have been fixed.

**What was implemented:**

- Moved `if not response.ok` block outside try-except - clearer separation of concerns
- Replaced `logger.error(e)` with `logger.exception()` in except block - preserves full stack trace
- Removed redundant logging (consolidated to single call per error path)
- Removed `from None` to keep exception chain intact for debugging
- Improved message selection logic - localhost vs remote messages defined upfront

**Original issues** (for reference):

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

### 3.6. Do Not Raise Bare BaseError, UserError, or InternalError

The guideline extends the rule beyond `BaseError`: **never raise any of the three base classes directly** —
not `BaseError`, not `UserError`, not `InternalError`.
Callers cannot catch specifically, and the type carries no semantic information about the actual problem.

**✅ Bare `UserError` / `InternalError` raises in active code: resolved** (PR #2226, March 2026) —
no bare `raise UserError(...)` or `raise InternalError(...)` remain outside legacy/deprecated modules.

**Bare `BaseError` raises in non-legacy, actively maintained code (still open):**

- [ark2iri.py](src/dsp_tools/commands/xmlupload/prepare_xml_input/ark2iri.py) — 3 occurrences
- [make_values.py:191](src/dsp_tools/commands/xmlupload/make_rdf_graph/make_values.py#L191)
- [get.py:96](src/dsp_tools/commands/get/get.py#L96)
- [reformat_validation_results.py:62](src/dsp_tools/commands/validate_data/process_validation_report/reformat_validation_results.py#L62)
- [excel2json/project.py:252](src/dsp_tools/commands/excel2json/project.py#L252)

Legacy and deprecated modules (`excel2xml`, `langstring.py`, `datetimestamp.py`, `date_util.py`,
`get/legacy_models/`) are exempt per the guideline.

**Recommendation:** Use specific subclasses; create a new one if no appropriate one exists yet.


### 3.7. Improve Entry Point Exception Handling

**Current state of `entry_point.py`:**

The entry point catches `BaseError` and bare `Exception`. `KeyboardInterrupt` is not handled
explicitly — it falls into `except Exception`, which logs it as an internal error and prints the
`InternalError` contact message. This is incorrect: Ctrl+C is not a bug.

Update `entry_point.py` > `run()`:

```python
try:
    parsed_arguments = _derive_dsp_ingest_url(...)
    success = call_requested_action(parsed_arguments)
except KeyboardInterrupt:
    logger.info("User interrupted execution")
    sys.exit(130)  # Standard POSIX exit code for SIGINT
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


### 3.8. Exception Chain — Converting vs. Propagating

The guideline distinguishes two cases for exception chaining. The current codebase mixes them.

**Converting** — catching a low-level exception, raising a *different* DSP-TOOLS exception:

```python
except SomeLowLevelError as err:
    logger.exception(err)                              # preserve original traceback in logs
    raise DSPErrorSubclass("User message.") from None  # prevent duplicate traceback in entry_point.py
```

- Log first with `logger.exception()` (not `logger.error()` — `error()` drops the stack trace)
- Then use `from None` to prevent a duplicate traceback when `entry_point.py` logs the new exception

**Propagating** — catching a DSP-TOOLS exception and re-raising the *same* exception:

```python
except SomeDSPError:
    raise  # do NOT log here; entry_point.py logs exactly once
```

- Do **not** log before re-raising
- Do **not** use `from None`

**Current violations (31 `from None` usages across 17 files):**

Many usages are in "converting" scenarios but lack the required prior `logger.exception()` call.
The old guidance to "use `from e` for DSP-TOOLS-to-DSP-TOOLS conversions" is superseded by the
propagating rule: just `raise` (no `from e` needed when re-raising the same exception unchanged).

**Specific violation — `src/dsp_tools/utils/request_utils.py` `log_and_raise_timeouts()`:**

- Uses `logger.error(msg)` before `from None` — this loses the stack trace of the original exception
- Must use `logger.exception(error)` to capture the traceback in logs before suppressing the chain



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

**Root cause:** Duplicate logging arises from violating the converting/propagating distinction:

- **Propagating** (re-raising the same exception): never log — `entry_point.py` handles it once.
- **Converting** (raising a different exception): log once with `logger.exception()`, then `from None`.

**Recommendation:**

- **Log at the highest level only:** Let exceptions bubble up to `entry_point.py` where they are logged once.
- **Intermediate handlers must NOT log before re-raising:** If re-raising the same exception, just `raise`.
- **When converting:** Use `logger.exception()` + `raise NewError(...) from None`.

Check all `logger.error()` + re-raise patterns in the codebase against these rules.



### 3.10 Get rid of unnecessary PermanentTimeOutError

In the Connection class, the builtins TimeoutError and ReadTimeout are logged and converted into PermanentTimeOutError.
The xmlupload code adds some text, and then exits Python via a XmlUploadInterruptedError.
For this, we don't need an own class. The xmlupload can also catch and handle the builtins directly.

### 3.11 Exceptions Inheriting Directly from BaseError (Guideline Violation)

**✅ COMPLETED (PR #2224, March 2026)** — All direct `BaseError` subclasses that violated the guideline
have been reclassified. See Implementation Status item 5 for the full list.

**Remaining naming bug (open):**

- `XmllibInternalError(UserError)` in `xmllib/internal/exceptions.py`: name implies `InternalError`
  classification but the type inherits `UserError`. Either rename it to reflect its actual semantics,
  or reclassify it as `InternalError`.

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
