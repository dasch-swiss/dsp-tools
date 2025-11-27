# Analysis of Exception Hierarchy and Handling

**Date:** 2025-11-07
**Updated:** 2025-11-27
**Scope:** Analysis of exception handling across DSP-TOOLS codebase with improvement recommendations

## Proposed Steps

1. Nora reviews this document
    - Some recently added error classes are not considered yet in this report,
      but this should not hinder us discussing this report.
2. Based on the feedback, Johannes fine-tunes this document
3. Johannes creates a project and tickets
    - Implementation order:
        - Hierarchy redesign
        - Concrete issues in error handling (easily fixable in 1 PR each)
        - Add Architecture Documentation
        - Error Message Quality - More Involved

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
│   ├── CreateError (moved)
│   |   └── ProjectNotFoundError
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

---

## 3. Concrete issues in error handling (easily fixable in 1 PR each)

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


### 3.9 Issues with `parse_json_file()`

`parse_json_file()` in `src/dsp_tools/utils/json_parsing.py`
doesn't follow the pattern in "How to Handle Exceptions". 
In addition, it doesn't pass on the parsing error to the user, so the user doesn't have a chance to fix his JSON.


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
