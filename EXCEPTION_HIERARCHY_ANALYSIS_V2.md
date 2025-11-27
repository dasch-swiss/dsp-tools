# DSP-TOOLS Exception Hierarchy Analysis

**Date:** 2025-11-07
**Scope:** Analysis of exception handling across DSP-TOOLS codebase with improvement recommendations

---

## Executive Summary

The DSP-TOOLS exception system has a clear hierarchy distinguishing user-fixable errors (`InputError`)
from internal errors (`InternalError`). However, implementation inconsistencies, ambiguous exception semantics,
and missing best practices undermine its effectiveness.

**Key Findings:**

- ✅ **Strengths:** Clear conceptual hierarchy, good user message formatting, comprehensive logging
- ⚠️ **Weaknesses:** Inconsistent exception usage, ambiguous naming, inappropriate exception
  chain suppression
- 🔴 **Critical Issues:** Raw `BaseError` raises, catch-all exception handler, missing error
  context

**Overall Assessment:** 6.5/10 - Solid foundation requiring implementation refinement

---

## Command Grouping Context

DSP-TOOLS commands fall into two categories with different error handling needs:

### 1. Server Interaction Commands (fail-fast acceptable)

Commands that interact with DSP servers (`create`, `xmlupload`, `ingest-xmlupload`, `resume-xmlupload`):

- Tested in local/test environments before production
- Can fail fast with context when issues occur
- Users may need developer assistance
- Bugs can escalate to top-level handler in `entry_point.py`

### 2. Local Validation/Transformation Commands (must report all problems)

Commands running locally (`excel2json`, `excel2xml`, `xmllib`, `get`, `validate-data`):

- Must work immediately on user machines
- Should report ALL problems clearly
- Users must be able to fix issues themselves without contacting developers
- Errors should be handled gracefully with user-friendly messages
- Bugs can escalate to top-level handler in `entry_point.py`

---

## Guidelines: When to Catch vs. Let Fail

All exceptions are caught at the top level (`entry_point.py` > `run()`) to prevent Python tracebacks
from reaching users.

### In Implementation Code: Do NOT Catch

Avoid catching errors from your own code logic (your own programming bugs like type errors, logic mistakes).
Let them crash immediately because:

- Standard Python tracebacks pinpoint the failure location and cause
- Try-except blocks may mask root causes and delay discovery
- Test environments exist to surface these issues before production
- Silent failures or generic error messages make debugging harder

### In Implementation Code: DO Catch

Catch exceptions for external operations where failure is expected and recoverable:

- File I/O operations (file not found, permission denied)
- Network requests (connection failures, timeouts)
- User input validation (invalid formats, out-of-range values)
- External API calls
- External library calls that might fail in predictable ways

### Only Catch When You Have a Specific Recovery Strategy

- Adding crucial diagnostic context not in the traceback
- Implementing retry logic for transient failures
- Gracefully degrading functionality (e.g., skipping one item in a batch)

This produces a **leaner codebase** focused on handling genuine external failures while bugs fail loudly
and get fixed quickly.

---

## How to Handle Exceptions

### General Principles

When catching errors, preserve as much context as possible:

- if possible, extract the message from the exception object: `err.msg` / `err.message`
- log the original stack trace with `logger.exception(err.msg)`
    - `logger.error()` doesn't preserve the original stack trace -> avoid it
- if re-raising is wished, do NOT use `from None`
    - `from None` removes the information about the original error from the stack trace -> avoid it
- whenever possible, don't compose long error messages outside of the error class.
  Instead, the message should be composed in the `__str__(self)` method of the error class

```python
try:
    return json.load(filepath)
except json.JSONDecodeError as err:
    logger.exception(err.msg)  # extract err.msg and preserve the original stack trace
    raise JSONFileParsingError(filepath, err.msg)

@dataclass
class JSONFileParsingError:
    filepath: Path
    orig_err_msg: str

    def __str__(self) -> str:
        return f"The input file '{self.filepath}' cannot be parsed due to the following problem: {self.orig_err_msg}"
```

---

## 1. Proposed Exception Hierarchy Redesign

### Current Issues

- `InputError` should be renamed to `UserError` (broader scope: not just input problems)
- No clear distinction between user-fixable and internal errors at the hierarchy level
- Several errors are misclassified

### Proposed Structure

```text
BaseError
├── UserError (renamed from InputError)
│   ├── UserFilepathNotFoundError
│   ├── UserDirectoryNotFoundError
│   ├── JSONFileParsingError
│   ├── DuplicateIdsInXmlAndId2IriMapping
│   ├── DockerNotReachableError (moved)
│   ├── DspApiNotReachableError (moved)
│   ├── InvalidGuiAttributeError (moved)
│   ├── BadCredentialsError (moved)
    ├── CreateError (moved)
    |   └── ProjectNotFoundError
│   └── XmlUploadUserError (new grouping for xmlupload user errors)
│       ├── Id2IriReplacementError
│       ├── XmlUploadPermissionsNotFoundError (XmlUploadError should be merged with this class)
│       ├── XmlUploadAuthorshipsNotFoundError
│       └── XmlUploadListNodeNotFoundError
└── InternalError
    ├── UnexpectedApiResponseError (moved)
    ├── PermanentConnectionError (moved)
    │   └── PermanentTimeOutError (moved under PermanentConnectionError)
    ├── ShaclValidationError (renamed from ShaclValidationCliError and moved)
    ├── XmlInputConversionError (moved)
    ├── XmlUploadInterruptedError

    ├── InvalidIngestFileNameError
    └── InvalidInputError (should be a subclass of InternalError, and marked as deprecated,
                           because it's only used by the deprecated `Connection` class and the old `create` code)
```

### Key Changes

1. **Rename `InputError` to `UserError`**: Reflects broader scope (not just input issues)
2. **Create two main branches**: `UserError` (user can fix) and `InternalError` (requires developer intervention)
3. **Move `PermanentTimeOutError` under `PermanentConnectionError`**: Timeouts are a type of connection failure
4. **Move infrastructure errors to `UserError`**:
   - `DockerNotReachableError` (user needs to start Docker)
   - `DspApiNotReachableError` (user needs to start API)
5. **Move API/server errors to `InternalError`**:
   - `UnexpectedApiResponseError` (unexpected behavior we can't handle)
   - `PermanentConnectionError` (infrastructure issues after retries)
6. **Rename/improve xmlupload errors**:
   - `XmlUploadError` → should be merged with `XmlUploadPermissionsNotFoundError`
   - Group xmlupload user errors under `XmlUploadUserError` for easier catching
7. **Replace `ShaclValidationCliError` with `ShaclValidationError`**: Make it a subclass of `InternalError`
8. **Move `InvalidGuiAttributeError` to `UserError`**: User provided invalid attribute
9. **Move `Id2IriReplacementError` to `UserError`**: User's ID mapping is incomplete/incorrect
10. **Keep `CreateError` as `InternalError` subclass**: Functionality-specific grouping is useful

### Entry Point Exception Handling

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

---

## 2. Semantic Ambiguity Issues

### Issue 2.1: Confusingly Similar Names

**Problem:** `InvalidInputError` vs `InputError` (soon `UserError`)

```python
class UserError(BaseError):
    """User input is invalid. Message should be user-friendly."""

class InvalidInputError(BaseError):
    """API responds with permanent error due to invalid input data"""
```

These names are too similar but serve different purposes. `InvalidInputError` means the API rejected
our request (likely a programming error), while `UserError` means the user provided bad input.

**Recommendation:** Rename `InvalidInputError` → `ApiRejectedInputError`

### Issue 2.2: Generic BaseError Raises

Multiple locations raise raw `BaseError`:

- [date_util.py:46](src/dsp_tools/utils/data_formats/date_util.py#L46): `raise BaseError(f"Invalid calendar type: {s}")`
- [json_parsing.py:33](src/dsp_tools/utils/json_parsing.py#L33): `raise BaseError("Invalid input: ...")`
- [make_values.py:191](src/dsp_tools/commands/xmlupload/make_rdf_graph/make_values.py#L191)

**Problem:** Raising raw `BaseError` defeats the purpose of having a hierarchy. Cannot catch specific exception types.

**Recommendation:** Use specific exceptions:

- Date parsing errors → `UserError` (user provided bad date)
- JSON validation → `JSONFileParsingError` (already exists!)
- Unknown value types → `InternalError` (programming error)

### Issue 2.3: XmlInputConversionError Misclassification

```python
class XmlInputConversionError(BaseError):
    """Error during XML input conversion."""
```

**Problem:** Why isn't this a subclass of `UserError`? XML conversion errors are fundamentally user input
issues.

**Recommendation:** Make it a subclass of `InternalError` (if conversion fails due to our code) or
`UserError` (if user's XML is malformed). Clarify the use case.

---

## 3. Exception Chain Suppression

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

---

## 4. Top-Level Exception Handler Issues

Located in [entry_point.py:66-80](src/dsp_tools/cli/entry_point.py#L66-L80):

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

### Issue 4.1: Catch-All Catches Too Much

**Problem:** `except Exception` catches everything including:

- `KeyboardInterrupt` (user presses Ctrl+C) → shown as "InternalError"
- All third-party library exceptions → logged but loses context

**Impact:** Prevents graceful shutdown and confuses users when they interrupt execution.

**Recommendation:** Add explicit `KeyboardInterrupt` handler (see Section 1)

### Issue 4.2: No Distinction Between User and Internal Errors

Currently catches all `BaseError` the same way. Should distinguish:

- User errors → friendly message suggesting fixes
- Internal errors → message directing users to contact developers

---

## 5. Error Message Quality

### Strengths

- Red color for errors, yellow for warnings
- Clear separation between user message (stdout) and technical details (logs)
- `InternalError` provides excellent guidance for contacting developers

### Issues

#### Issue 5.1: Inconsistent Message Formatting

**Problem:** Some messages include "ERROR:" prefix, others don't.

**Recommendation:** Remove all "ERROR:" prefixes from exception messages. The red color and context
already indicate it's an error.

Replace: `raise FooError("ERROR: foobar")`
With: `raise FooError("foobar")`

#### Issue 5.2: Technical Jargon in User-Facing Errors

**Examples:**

- "OntologyConstraintException" (too technical)
- "INGEST rejected file due to its name" (what's INGEST? What's wrong with the name?)

**Recommendation:** Use plain language and explain what users need to do.

#### Issue 5.3: Missing Actionable Guidance

Many errors state **what** went wrong but not **how** to fix it:

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

#### Issue 5.4: xmlupload Errors Need Better Messages

Errors like `XmlUploadPermissionsNotFoundError`, `XmlUploadAuthorshipsNotFoundError`, and
`XmlUploadListNodeNotFoundError` need improved messages explaining:

- Which permission/authorship/list node was not found
- Where in the XML file the reference occurs
- How to fix it (add the missing definition, fix the reference, etc.)

---

## 6. Concrete issues in error handling

### 6.1 ShaclCliValidator Issues

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

### 6.2 `_check_api_health()` (`src/dsp_tools/cli/utils.py`) issues

- `if not response.ok`  should be moved out of the try-except block
- except block uses `logger.error()` twice
    - remove `logger.error(e)`
    - `logger.error(msg)` -> `logger.exception(msg)`
- remove `from None`

---

## 7. UnknownDOAPException - Exception Misuse

```python
class UnknownDOAPException(BaseError):
    """Class for errors that are raised if a DOAP cannot be parsed"""
```

### Analysis: This is Not an Exception

**The Situation:**

- Legacy projects have custom DOAP combinations that don't fit the current limited system
- When downloading existing projects, these legacy DOAPs must be handled gracefully
- A sensible fallback exists (write default text to JSON)
- This is **expected behavior**, not an exceptional condition

**The Problem:** This is a textbook case of **exception misuse**.

Exceptions should represent **unexpected errors**, not **expected alternative outcomes**.
Using exceptions for control flow in expected scenarios is an anti-pattern that makes code harder to reason about.

#### Current Code (problematic)

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

#### Recommended Approach - Option 1: Union Types

```python
def parse_doap(...) -> str | None:
    """Parse DOAP configuration.

    Returns:
        DOAP string if recognized, None if legacy/unrecognized
    """
    if not recognized:
        return None
    return doap_string

# Calling code (clean and natural)
doap = parse_doap(...) or DEFAULT_DOAP_TEXT
```

#### Recommended Approach - Option 2: Result Type (more expressive)

```python
@dataclass
class DOAPResult:
    value: str
    is_legacy: bool

def parse_doap(...) -> DOAPResult:
    """Parse DOAP configuration.

    Returns:
        DOAPResult with parsed value and legacy flag
    """
    if not recognized:
        return DOAPResult(value=DEFAULT_DOAP_TEXT, is_legacy=True)
    return DOAPResult(value=doap_string, is_legacy=False)

# Calling code (explicit and type-safe)
result = parse_doap(...)
if result.is_legacy:
    logger.info("Using default DOAP for legacy project")
doap = result.value
```

### Benefits of Union/Result Types

1. **Type system clarity**: The "no match" case is explicit in the function signature
2. **Natural control flow**: No try-except needed for expected cases
3. **Better performance**: No exception overhead
4. **Clearer intent**: Signals this is a normal outcome, not an error

### Recommendation

Remove `UnknownDOAPException` entirely and replace with union return types (`str | None`) or result objects.
This better represents the domain: legacy DOAPs are an expected reality, not an exceptional failure.

---

## 8. CreateError and Functionality-Specific Errors

```python
class CreateError(BaseError):
    """Errors for the create command."""
```

**Analysis:** Functionality-specific error classes like `CreateError` and `XmlUploadUserError` are useful for:

- Grouping related errors
- Catching all errors from a specific command together
- Providing command-specific context

**Recommendation:** Keep `CreateError` as a subclass of `InternalError`. It provides useful grouping
without adding complexity.

---

## 9. Xmllib Exception Isolation

The xmllib has its own hierarchy:

- `XmllibInputError`
- `XmllibFileNotFoundError`
- `XmllibInternalError`

### Good

- Clear isolation of library-specific errors
- Follows same pattern as main exceptions (Input/Internal distinction)

### Problem: Redundancy

```python
class XmllibFileNotFoundError(BaseError):
    """User provided filepath that does not exist."""

class UserFilepathNotFoundError(UserError):
    """Filepath from user does not exist."""
```

**Recommendation:** Consider merging xmllib exceptions with main hierarchy:

- `XmllibInputError` → `UserError`
- `XmllibFileNotFoundError` → `UserFilepathNotFoundError`
- `XmllibInternalError` → `InternalError`

Alternatively, keep them separate if xmllib is intended to be independently distributable.

---

## 10. Validation: Problem Protocol vs Exceptions

The validation system uses a `Problem` protocol with `InputProblem` dataclasses:

```python
@dataclass
class InputProblem:
    problem_type: ProblemType
    severity: Severity
    res_id: str | None
    res_type: str | None
    prop_name: str
    message: str | None
    ...
```

**Analysis:** This is **excellent design**:

- Allows collecting all validation errors at once (don't fail on first error)
- Returns `ValidateDataResult` with problems
- CLI decides whether to exit based on severity

This pattern aligns perfectly with local validation commands that should "report ALL problems clearly."

**Recommendation:** Adopt this pattern more broadly for commands in the "local validation/transformation" group:

1. Commands return result objects (success + list of problems)
2. CLI layer handles exit codes based on problems
3. Document this as standard pattern for batch validation/transformation operations

**When to use:**

- Batch operations that can find multiple problems (validation, transformation)
- Operations where users benefit from seeing all issues at once

**When not to use:**

- Single-resource operations (one API call)
- Operations that must fail fast (authentication, connection)

---

## 11. Testing Considerations

### Current Strengths

- Tests verify specific exception types
- Tests check error message content
- Some tests verify exception chains

### Missing Coverage

#### Issue 11.1: No Meta-Tests for Exception Hierarchy

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

---

## 12. Documentation Gaps

### Issue 12.1: Missing Exception Documentation in Functions

**Current state:** Many functions don't document which exceptions they raise.

**Analysis:** While documenting every possible exception would create maintenance burden and doc-rot,
documenting **DSP-TOOLS custom exceptions** that a function intentionally raises is valuable:

```python
def create_project(...) -> bool:
    """
    Create a project on the DSP server.

    Returns:
        True if successful

    Raises:
        UserError: If the project definition is invalid
        PermanentConnectionError: If the server is unreachable after retries
        BadCredentialsError: If authentication fails
    """
```

**Recommendation:** Document only custom DSP-TOOLS exceptions (not built-ins or third-party). This
provides useful API documentation without excessive maintenance burden.

### Issue 12.2: Missing Architecture Documentation

**Current state:** No centralized documentation explaining:

- When to use exceptions vs Problem protocol
- How to choose between exception types
- Exception conversion patterns
- The two command groups and their error handling needs

**Recommendation:** Create `docs/developers/error-handling-guidelines.md` with:

1. Command grouping and error handling requirements
2. Decision tree for choosing exception types
3. When to catch vs. let fail
4. Standard patterns for exception conversion and logging
5. Guidelines for user-friendly error messages
6. Examples of good and bad error handling

---

## 13. Summary of Recommended Actions

### Critical (Fix First)

| Priority | Action | Impact |
|----------|--------|--------|
| 🔴 High | Add `KeyboardInterrupt` handler in entry_point.py | Proper Ctrl+C handling |
| 🔴 High | Replace raw `BaseError` raises with specific types | Type-safe exception catching |
| 🔴 High | Restructure hierarchy: `UserError` and `InternalError` branches | Clear error responsibility |

### High Priority (Important Improvements)

| Priority | Action | Benefit |
|----------|--------|---------|
| 🟡 Medium | Rename `InvalidInputError` → `ApiRejectedInputError` | Eliminates naming confusion |
| 🟡 Medium | Move `PermanentTimeOutError` under `PermanentConnectionError` | Logical hierarchy |
| 🟡 Medium | Fix `ShaclCliValidator` exception handling | Better error context |
| 🟡 Medium | Improve xmlupload error messages | Better UX for users |
| 🟡 Medium | Remove `UnknownDOAPException` - replace with union types | Fix exception misuse |

### Medium Priority (Code Quality)

| Priority | Action | Benefit |
|----------|--------|---------|
| 🟢 Low | Remove "ERROR:" prefixes from all exceptions | Consistent formatting |
| 🟢 Low | Standardize exception chaining (`from e` vs `from None`) | Better debugging |
| 🟢 Low | Add actionable guidance to user-facing errors | Improved UX |
| 🟢 Low | Document custom exceptions in function docstrings | Better API docs |

### Low Priority (Nice to Have)

| Priority | Action | Benefit |
|----------|--------|---------|
| 🔵 Optional | Create error handling architecture docs | Developer onboarding |
| 🔵 Optional | Add meta-tests for exception hierarchy | Prevent regressions |
| 🔵 Optional | Consider merging xmllib exceptions | Reduce duplication |

---

## Conclusion

The DSP-TOOLS exception system has a solid conceptual foundation but suffers from implementation
inconsistencies. The proposed two-tier hierarchy (`UserError` vs `InternalError`) combined with the
command grouping approach provides clear guidance for:

- **When to catch exceptions** (external failures only, let bugs crash)
- **How to classify exceptions** (can user fix it?)
- **What error messages to provide** (actionable guidance for users, detailed context for developers)

Implementing these recommendations will result in:

1. **Better user experience**: Clear, actionable error messages
2. **Easier debugging**: Preserved exception chains and context
3. **Clearer codebase**: Consistent exception handling patterns
4. **Better maintainability**: Well-defined error handling responsibilities

The key insight from the command grouping is that **local validation/transformation commands** should
adopt the Problem protocol pattern more extensively, while **server interaction commands** can fail fast
with good error context. This distinction drives the appropriate error handling strategy for each
command type.
