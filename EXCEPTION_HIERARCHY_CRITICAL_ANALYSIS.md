# Critical Analysis of DSP-TOOLS Exception Hierarchy and Error Handling System

**Date:** 2025-10-29
**Scope:** Complete analysis of exception handling across the DSP-TOOLS codebase
**Focus:** Weak points, inconsistencies, and areas for improvement

---

## Executive Summary

The DSP-TOOLS exception system is **fundamentally well-designed**
with a clear hierarchy that distinguishes between user-fixable errors (`InputError`) and internal errors (`InternalError`).
However, the implementation suffers from **significant inconsistencies** in usage patterns,
**architectural ambiguities**, and **missing best practices** that undermine the system's clarity and maintainability.

**Key Findings:**
- ✅ **Strengths:** Clear hierarchy, good user message formatting, comprehensive logging
- ⚠️ **Weaknesses:** Inconsistent exception construction, ambiguous exception semantics, catch-all patterns
- 🔴 **Critical Issues:** Exception/Problem duality creates confusion, positional arguments break dataclass contracts

**Overall Assessment:** 6.5/10 - Good foundation with significant implementation issues

---

**OVERALL RESPONSE FROM DEVELOPER**: When reading your report, I digged through the codebase and found some further issues.
I noted them in this paragraph. (I hope I didn't duplicate one of your findings, by mistake).
Please think about them carefully, and if you agree, include them in your report.

- InputError should be renamed to UserError, to reflect the broader scope: not only the input might be wrong, but also other circumstances within the power of the user
- There should be 2 subclasses of BaseError: 
  - UserError where the user is the culprit and can do something to remedy the issue,
  - InternalError for issues with server infrastructure, unexpected API responses, unexpected behaviour of our own python code, ... where the user can do nothing to remedy the issue.
  - All other classes should be a subclass of either of the aforementioned.
- In the try-except block in entry_point.py > run(), first the UserErrors should be handled (instead of BaseError as it is now), then the `Exception` (which include `InternalError`) should be transformed into `InternalError`
- DockerNotReachableError and DspApiNotReachableError should be subclasses of UserError
- UnexpectedApiResponseError should be a subclass of InternalError
- InvalidGuiAttributeError should be a subclass of UserError
- PermanentConnectionError should be a subclass of InternalError
- ShaclValidationCliError should be replaced by ShaclValidationError. ShaclValidationError should be a subclass of InternalError
- PermanentTimeOutError should be a subclass of InternalError
- XmlUploadError should be renamed to XmlPermissionError and be a subclass of UserError. The messages should be improved, in order to be helpful for the user
- XmlInputConversionError should be a subclass of InternalError
- Id2IriReplacementError should be a subclass of UserError
- XmlUploadInterruptedError should be a subclass of InternalError
- XmlUploadPermissionsNotFoundError should be a subclass of UserError. Its message should be improved, in order to be helpful for the user
- XmlUploadAuthorshipsNotFoundError should be a subclass of UserError. Its message should be improved, in order to be helpful for the user
- XmlUploadListNodeNotFoundError should be a subclass of UserError. Its message should be improved, in order to be helpful for the user
- UnknownDOAPException should either be a subclass of InternalError, or be removed entirely. Instead of raising an UnknownDOAPException, the functions should just return None. What do you think?


- All UserErrors that belong to xmlupload could be grouped under a class XmluploadUserError, which is a subclass of UserError


- Generally: When handling an internal error, where the cause of the mistake is not 100% clear, 
  as much context as possible should be logged, either with `logger.exception()` or by re-raising a new exception *without* `from None`
- Issues with ShaclCliValidator.validate():
  - The error message says that Docker is not running, but this is already checked in `src/dsp_tools/cli/utils.py` > `check_docker_health()`
  - it uses `logger.error()` instead of `logger.exception()`
  - it uses `logger.error()` twice
  - it raises ShaclValidationCliError from None, so the original error is lost. 
  - Question to Claude Code: What is better, `logger.exception()` or removing `from None`? Or should both be used?



---

## 1. Exception Hierarchy Architecture

### 1.1 Strengths

**Clear Separation of Concerns**
The system distinguishes between:
- **User-fixable errors** (`InputError` subclasses) - invalid input that users can correct
- **Connection/network errors** (`PermanentConnectionError`, `PermanentTimeOutError`)
- **Internal errors** (`InternalError`) - bugs requiring dev team intervention
- **Domain-specific errors** (`XmlUploadError`, `ShaclValidationError`)

This separation is conceptually sound and helps direct error messages to appropriate audiences.

**Dataclass-Based Design**
Using `@dataclass` for `BaseError` with a `message` field and custom `__str__` is clean:

```python
@dataclass
class BaseError(Exception):
    message: str = ""

    def __str__(self) -> str:
        return self.message
```

This ensures consistent string representation across all exceptions.

### 1.2 Critical Weaknesses

#### **Issue 1.1: Semantic Ambiguity in Exception Names**

Several exceptions have unclear or overlapping purposes:

**Problem A: `InvalidInputError` vs `InputError`**
```python
class InputError(BaseError):
    """User input is invalid. Message should be user-friendly."""

class InvalidInputError(BaseError):
    """API responds with permanent error due to invalid input data"""
```

**Critique:** These names are confusingly similar but serve different purposes.
`InvalidInputError` is raised when the **API** rejects input (suggesting a programming error),
while `InputError` is for direct user input errors.
This distinction is not obvious from the names.

**Recommendation:** Rename to clarify intent: `InvalidInputError` → `ApiRejectedInputError` or `InvalidApiInputError`
**RESPONSE FROM DEVELOPER**: Please go for `ApiRejectedInputError`

**Problem B: `XmlInputConversionError` vs `InputError`**
```python
class XmlInputConversionError(BaseError):
    """Error during XML input conversion."""
```

**Critique:** Why isn't this a subclass of `InputError`? XML conversion errors are fundamentally user input issues.
The current hierarchy suggests it's neither user-fixable nor internal, creating ambiguity.

**Recommendation:** Make it a subclass of `InputError` or clarify why it's fundamentally different.

**RESPONSE FROM DEVELOPER**: You're right, it should be a subclass of `InputError`. 

**Problem C: Generic `BaseError` Raises**

Found multiple locations raising raw `BaseError`:
- [src/dsp_tools/utils/data_formats/date_util.py:46](src/dsp_tools/utils/data_formats/date_util.py#L46): `raise BaseError(f"Invalid calendar type: {s}")`
- [src/dsp_tools/utils/json_parsing.py:33](src/dsp_tools/utils/json_parsing.py#L33): `raise BaseError("Invalid input: ...")`
- [src/dsp_tools/commands/xmlupload/make_rdf_graph/make_values.py:191](src/dsp_tools/commands/xmlupload/make_rdf_graph/make_values.py#L191)

**Critique:** Raising raw `BaseError` defeats the purpose of having a hierarchy. These should use more specific exception types:
- Date parsing errors → `InputError` (user provided bad date)
- JSON validation → `JSONFileParsingError` (already exists!)
- Unknown value types → `InternalError` (programming error)

**Impact:** This makes it impossible to catch specific exception types, forcing developers to catch all `BaseError` instances.

#### **Issue 1.2: Confusing Exception Chain Suppression**

Found extensive use of `from None` pattern:

```python
except PermanentConnectionError as e:
    raise InputError(e.message) from None  # Suppresses traceback chain
```

**Locations:**
- [src/dsp_tools/clients/authentication_client_live.py:43](src/dsp_tools/clients/authentication_client_live.py#L43)
- [src/dsp_tools/clients/authentication_client_live.py:45](src/dsp_tools/clients/authentication_client_live.py#L45)
- [src/dsp_tools/utils/xml_parsing/parse_clean_validate_xml.py:46](src/dsp_tools/utils/xml_parsing/parse_clean_validate_xml.py#L46)
- 17 additional locations

**Critique:** Using `from None` suppresses the exception chain, losing valuable debugging information.
This makes it harder to diagnose the root cause of errors.

**When it's appropriate:**
- Converting low-level exceptions to user-friendly messages where the technical details aren't relevant

**When it's problematic:**
- Converting between DSP-TOOLS exceptions (e.g., `PermanentConnectionError` → `InputError`)
- In development/debugging scenarios

**Recommendation:**
- Use `from e` (or no `from` clause) for DSP-TOOLS-to-DSP-TOOLS conversions
- Reserve `from None` for converting third-party exceptions to user messages

#### **Issue 1.3: Inconsistent Exception Constructor Patterns**

Found three different patterns for exception construction:

**Pattern A: Custom `__init__` with specific parameters** ✅ Good
```python
class UserFilepathNotFoundError(InputError):
    def __init__(self, filepath: str | Path) -> None:
        msg = f"The provided filepath does not exist: {filepath}"
        super().__init__(msg)
```

**Pattern B: Dataclass field with positional argument** ⚠️ Fragile
```python
raise InputError("Some error message")  # Relies on positional arg
```

**Pattern C: Complex custom logic** 🤔 Complex but justified
```python
class InternalError(BaseError):
    def __init__(self, custom_msg: str | None = None, keep_default_msg: bool = True) -> None:
        # Complex message construction logic
```

**Critique:**

Pattern B (positional arguments) is **dangerous** because:
1. It relies on dataclass field ordering (fragile)
2. Doesn't communicate intent (what does `InputError("foo")` mean?)
3. Breaks if dataclass fields are added/reordered

**Evidence of the problem:**
```python
# Current usage across codebase:
raise InputError("Invalid DSP server URL")  # positional
raise BaseError(f"Could not parse date: {s}")  # positional
raise InputError(msg)  # positional - what does 'msg' represent?
```

**Recommendation:**
- **Enforce keyword arguments:** `raise InputError(message="Invalid DSP server URL")`
- Or create factory methods: `InputError.from_message("...")`
- Add type hints to make field names explicit

---

## 2. Exception vs. Problem Duality

### 2.1 The Two Systems

DSP-TOOLS has **two parallel systems** for reporting errors:

**System 1: Exceptions** (raises and catches)
```python
raise InputError("Bad input")
```

**System 2: Problem Protocol** (collects and reports)
```python
class Problem(Protocol):
    def execute_error_protocol(self) -> str: ...
```

### 2.2 Critical Issues

#### **Issue 2.1: Inconsistent Usage Across Modules**

**Problem collection used in:**
- ✅ `excel2json` module - extensively uses `Problem` protocol
- ✅ `validate_data` module - uses `InputProblem` dataclasses
- ✅ `create` module - uses problem models

**Exception raising used in:**
- All other modules
- Even within modules that use `Problem`, exceptions are still raised

**Critique:** There's no clear guidance on when to use which system. This leads to:
- **Inconsistent error reporting UX** - some commands show all errors together, others fail on first error
- **Harder testing** - need to test two different error patterns
- **Cognitive overhead** - developers must decide which system to use

#### **Issue 2.2: Missing Conversion Between Systems**

When both systems exist in the same module, there's no standard pattern for:
- Converting a `Problem` to an `Exception` when it should be fatal
- Collecting multiple exceptions as `Problem` instances

**Example from excel2json:**
```python
# Sometimes raises immediately:
raise InputError(msg)  # Line 65 in resources.py

# Sometimes collects problems:
compliance_problem = check_compliance(...)
if compliance_problem:
    raise InputError(compliance_problem.execute_error_protocol())  # Line 58 in json_header.py
```

**Critique:** Mixing patterns within the same module is confusing. The excel2json module sometimes validates everything and reports all problems, other times fails fast on first error.

**RESPONSE FROM DEVELOPER**: The idea is that first, all problems are collected, then they are transformed into a string with the `execute_error_protocol()` method, and finally, an InputError is raised with the string as message.
The example you cite as "Sometimes raises immediately" perfectly follows this pattern.

#### **Issue 2.3: Problem Protocol Lacks Severity Levels**

The `Problem` protocol is minimal:
```python
class Problem(Protocol):
    def execute_error_protocol(self) -> str: ...
```

But `InputProblem` (in validate_data) has severity:
```python
class Severity(Enum):
    VIOLATION = auto()
    WARNING = auto()
    INFO = auto()
```

**Critique:** The base `Problem` protocol doesn't support severity levels, but implementations need them. This creates inconsistency:
- `excel2json` problems are all-or-nothing (no warnings)
- `validate_data` problems have three severity levels
- No standard way to aggregate and present problems across modules

**Recommendation:** Enhance the `Problem` protocol:
```python
class Problem(Protocol):
    def execute_error_protocol(self) -> str: ...
    def get_severity(self) -> Severity: ...
    def is_fatal(self) -> bool: ...
```

---

## 3. Exception Catching and Propagation

### 3.1 Top-Level Exception Handler

Located in [src/dsp_tools/cli/entry_point.py:66-80](src/dsp_tools/cli/entry_point.py#L66-L80):

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

#### **Issue 3.1: Catch-All Exception Handler Catches Too Much**

**Problem:** `except Exception` catches **everything**, including:
- `KeyboardInterrupt` (in Python < 3.0, or if someone incorrectly raises it as Exception)
- `SystemExit` (though typically bypasses except)
- All third-party library exceptions

**Critique:** This can prevent graceful shutdown:
- User presses Ctrl+C → caught as `Exception` → shown as "InternalError"
- Third-party library raises unexpected exception → logged but loses context

**Recommendation:**
```python
except BaseError as err:
    # Handle DSP-TOOLS exceptions
    ...
except KeyboardInterrupt:
    logger.info("User interrupted execution")
    sys.exit(130)  # Standard exit code for SIGINT
except Exception as err:
    # Only truly unexpected exceptions
    logger.exception("Unexpected error", exc_info=err)
    print(InternalError())
    success = False
```

#### **Issue 3.2: Inconsistent Re-raising Patterns**

Found multiple patterns for exception conversion:

**Pattern A: Catch and convert** (used 15+ times)
```python
except PermanentConnectionError as e:
    raise InputError(e.message) from None
```

**Pattern B: Catch and re-raise** (used 5+ times)
```python
except BaseError:
    logger.error("...")
    raise  # Let it propagate unchanged
```

**Pattern C: Catch, log, and continue** (used 10+ times)
```python
except BaseError:
    logger.exception("Failed to create list")
    # Don't re-raise, continue execution
```

**Pattern D: Catch multiple, handle differently** (used 3+ times)
```python
except (PermanentConnectionError, InvalidInputError) as e:
    # Special handling
except BaseError as e:
    # Generic handling
```

**Critique:** No clear guidelines on when to use each pattern. This leads to:
- **Inconsistent error recovery** - some commands continue after errors, others abort
- **Lost context** - some conversions lose important details
- **Redundant catches** - multiple layers catching the same exception types

**Locations exhibiting inconsistency:**
- [src/dsp_tools/commands/project/create/project_create_all.py](src/dsp_tools/commands/project/create/project_create_all.py) - 6 different catch blocks with different patterns
- [src/dsp_tools/commands/project/create/project_create_ontologies.py](src/dsp_tools/commands/project/create/project_create_ontologies.py) - 4 different catch blocks

**Recommendation:** Document standard patterns:
```python
# Pattern 1: Full conversion (external → internal exceptions)
try:
    response = requests.get(url)
except requests.RequestException as e:
    raise PermanentConnectionError(f"Network error: {e}") from e

# Pattern 2: Enrichment (add context to existing exception)
try:
    create_resource(data)
except BaseError as e:
    logger.error(f"Failed to create {resource_id}")
    raise  # Re-raise with logged context

# Pattern 3: Recovery (non-fatal errors)
try:
    optional_operation()
except BaseError as e:
    logger.warning(f"Optional operation failed: {e}")
    # Continue without re-raising
```

### 3.2 Authentication Client Exception Handling

The [authentication_client_live.py](src/dsp_tools/clients/authentication_client_live.py#L38-L51) has a **logical impossibility**:

```python
try:
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    logger.debug(f"RESPONSE: Requesting token responded with status {response.status_code}")
    res_json: dict[str, Any] = response.json()
except BadCredentialsError:  # ← This can NEVER be raised by requests.post()!
    raise InputError(f"Username and/or password are not valid on server '{self.server}'") from None
except PermanentConnectionError as e:
    raise InputError(e.message) from None
```

**Critique:** `BadCredentialsError` is a DSP-TOOLS exception, but it's being caught around a `requests.post()` call that can **never raise it**. This catch block is **dead code**.

**Root cause:** The exception handling was probably refactored at some point, leaving obsolete catch blocks.

**Recommendation:** Remove the impossible catch block or investigate if different code should be inside the try block.

---

## 4. Error Message Quality and User Experience

### 4.1 Strengths

**Good message formatting:**
- Red color for errors
- Yellow for warnings
- Clear separation between user message (stdout) and technical details (log file)

**InternalError provides excellent guidance:**
```python
"\n\nAn internal error occurred.\n"
"Please contact the dsp-tools development team with the following information:\n"
"    - Which command was used.\n"
"    - If applicable, any files that were used in conjunction with the command.\n"
"    - A text file with the terminal output copied into.\n"
"    - The log file at {LOGGER_SAVEPATH}.\n"
```

### 4.2 Weaknesses

#### **Issue 4.1: Inconsistent Message Formatting**

**Problem:** Exception messages use different formats:

```python
# Format 1: Prefixed with "ERROR:"
raise InputError(f"ERROR: Invalid DSP server URL '{server}'")  # entry_point.py:246

# Format 2: No prefix
raise InputError(f"Invalid DSP server URL '{server}'")

# Format 3: Sentence case
raise InputError("Username and/or password are not valid")

# Format 4: Lowercase continuation
raise InputError(f"max_file_size must be between 1 and {MAX_FILE_SIZE}")
```

**Critique:** The "ERROR:" prefix is redundant since the CLI already prints "The process was terminated because of an Error:" before the message. This creates double-prefixing:

```
The process was terminated because of an Error: ERROR: Invalid DSP server URL 'foo'
                                              ^^^^^^ redundant
```

**Recommendation:**
- Remove all "ERROR:" prefixes from exception messages
- Standardize on sentence case with punctuation
- Create message format guidelines

#### **Issue 4.2: Technical Jargon in User-Facing Errors**

Some `InputError` messages contain technical details:

```python
raise InputError(f"A project with shortcode {shortcode} could not be found on the DSP server")
```

**Critique:** Users may not know what a "shortcode" is. Better message:
```python
raise InputError(
    f"The project with ID '{shortcode}' could not be found on the DSP server. "
    f"Please verify the project ID is correct."
)
```

**Other examples:**
- "OntologyConstraintException" mentioned in error (too technical)
- "Resource ID exists in both mapping and new data" (unclear what to do)
- "INGEST rejected file due to its name" (what's INGEST? What's wrong with the name?)

#### **Issue 4.3: Missing Actionable Guidance**

Many errors tell users **what** went wrong but not **how** to fix it:

```python
raise InputError(f"{data_model_files} is not a directory.")
# Better: "Expected {data_model_files} to be a directory, but found a file.
#          Please provide a directory path containing Excel files."

raise InvalidGuiAttributeError("Invalid gui attribute")
# Better: "Invalid gui-attribute '{attr}'. Valid attributes for {gui_element} are: {valid_attrs}"
```

**Recommendation:** For all `InputError` subclasses, ensure messages:
1. State what was expected
2. State what was found
3. Suggest how to fix it

---

## 5. Xmllib Exception Isolation

The xmllib has its own exception hierarchy:
- `XmllibInputError`
- `XmllibFileNotFoundError`
- `XmllibInternalError`

### 5.1 Analysis

**Good:**
- Clear isolation of library-specific errors
- Follows same pattern as main exceptions (Input/Internal distinction)

**Problems:**

#### **Issue 5.1: Redundant with Main Exceptions**

```python
class XmllibFileNotFoundError(BaseError):
    """User provided filepath that does not exist."""

class UserFilepathNotFoundError(InputError):
    """Filepath from user does not exist."""
```

**Critique:** These are functionally identical. Why does xmllib need its own file-not-found exception?

**Recommendation:** Either:
- **Option A:** Use `UserFilepathNotFoundError` everywhere (remove xmllib version)
- **Option B:** If xmllib needs isolation, document **why** and ensure the exceptions provide xmllib-specific context

#### **Issue 5.2: Xmllib Warnings are More Sophisticated**

The xmllib warning system has:
```python
class XmllibUserInfoBase(Warning, ABC):
    @classmethod
    @abstractmethod
    def showwarning(cls, message: str) -> None: ...

class XmllibInputInfo(XmllibUserInfoBase):
    # Printed in YELLOW

class XmllibInputWarning(XmllibUserInfoBase):
    # Printed in BOLD_RED
```

But main warnings are simpler:
```python
class DspToolsUserWarning(DspToolsWarning):
    # Just warnings, no "info" level
```

**Critique:** Why does xmllib have `Info` and `Warning` levels, but the main system doesn't? This suggests:
- The main warning system is under-designed
- Or xmllib has special needs that weren't generalized

**Recommendation:** Either adopt xmllib's Info/Warning split project-wide, or justify why xmllib needs special handling.

---

## 6. Connection and Network Error Handling

### 6.1 Connection Error Hierarchy

```
BaseError
├── PermanentConnectionError
│   └── BadCredentialsError
├── PermanentTimeOutError
└── InvalidInputError
```

#### **Issue 6.1: Timeout Errors Aren't Connection Errors**

**Problem:** `PermanentTimeOutError` is a sibling of `PermanentConnectionError`, but semantically, a timeout **is** a connection failure.

**Current code:**
```python
# In xmlupload.py, must catch both separately:
except (PermanentConnectionError, PermanentTimeOutError, XmlUploadInterruptedError):
    # Handle network issues
```

**Critique:** Having to catch both separately is a code smell. Timeouts are a **type** of connection problem.

**Recommendation:**
```python
class PermanentConnectionError(BaseError):
    """All reconnection attempts to DSP have failed."""

class PermanentTimeOutError(PermanentConnectionError):
    """Python timeout due to no response from DSP-API."""
```

This allows catching all network issues with just `except PermanentConnectionError`.

#### **Issue 6.2: Retry Logic Hidden in Connection Class**

The [ConnectionLive._try_network_action](src/dsp_tools/clients/connection_live.py#L148-L190) has:
- Hardcoded 24 retries
- Exponential backoff in `log_request_failure_and_sleep`
- Timeout durations: 30 min for PUT/POST, 20 sec for GET

**Critique:** This retry logic is:
- Not configurable without changing code
- Not testable with different retry counts
- Hidden implementation detail

**Recommendation:**
- Make retry parameters configurable via constructor or config file
- Extract retry logic to separate utility for testability
- Document the retry strategy in exception docstrings

---

## 7. Validation Error Handling

### 7.1 SHACL Validation Exceptions

```python
class ShaclValidationCliError(BaseError):
    """Docker command has problems"""

class ShaclValidationError(BaseError):
    """Unexpected error during validation"""
```

#### **Issue 7.1: Unclear Error Boundaries**

**Question:** When should each be raised?
- Is `ShaclValidationCliError` for Docker issues specifically?
- Is `ShaclValidationError` for SHACL validation failures or unexpected errors?

**From usage:**
```python
# In shacl_cli_validator.py
raise ShaclValidationCliError(...)  # Docker problems

# In get_validation_report.py
raise ShaclValidationError(msg) from None  # Parsing errors
```

**Critique:** These names don't communicate the distinction. Better names:
- `ShaclValidationCliError` → `ShaclDockerCommandError`
- `ShaclValidationError` → `ShaclResultParsingError`

#### **Issue 7.2: Validation Problems vs Exceptions**

Validation uses the `Problem` protocol extensively with `InputProblem` dataclasses:

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

This is **excellent** - allows collecting all validation errors and showing them together.

**But:** When does validation raise an exception vs return problems?

**Answer from code:** Validation returns `ValidateDataResult` with problems, then the CLI command decides whether to exit:

```python
if not result.no_problems:
    # Print problems
    sys.exit(1)
```

**Critique:** This is actually **good design** - validation is pure (no side effects), CLI handles exceptions. However, this pattern isn't used consistently in other commands.

**Recommendation:** Adopt this pattern project-wide:
1. Commands return result objects (success + problems)
2. CLI layer handles exceptions and exit codes
3. Document this pattern as standard

---

## 8. Upload Error Handling

### 8.1 XML Upload Exceptions

```python
class XmlUploadError(BaseError):
    """Generic XML upload error"""

class XmlUploadInterruptedError(XmlUploadError):
    """Upload was interrupted"""

class XmlUploadPermissionsNotFoundError(BaseError):
    """Permission does not exist"""

class XmlUploadAuthorshipsNotFoundError(BaseError):
    """Authorship ID does not exist"""

class XmlUploadListNodeNotFoundError(BaseError):
    """List node does not exist"""
```

#### **Issue 8.1: Inconsistent Hierarchy**

**Problem:** The "NotFoundError" exceptions are siblings of `XmlUploadError`, but semantically they're upload-related errors.

**Recommendation:**
```python
class XmlUploadError(BaseError):
    """Generic XML upload error"""

class XmlUploadInterruptedError(XmlUploadError):
    """Upload was interrupted"""

class XmlUploadResourceNotFoundError(XmlUploadError):
    """Referenced resource not found"""

class XmlUploadPermissionsNotFoundError(XmlUploadResourceNotFoundError):
    """Permission does not exist"""

class XmlUploadAuthorshipsNotFoundError(XmlUploadResourceNotFoundError):
    """Authorship ID does not exist"""

class XmlUploadListNodeNotFoundError(XmlUploadResourceNotFoundError):
    """List node does not exist"""
```

This creates logical groupings and allows catching all upload errors with one catch.

#### **Issue 8.2: XmlUploadInterruptedError Raised in Multiple Places**

Found in [xmlupload.py:405, 411, 427, 435](src/dsp_tools/commands/xmlupload/xmlupload.py):

```python
raise XmlUploadInterruptedError(msg) from None
```

**Critique:** The same exception is raised in 4 different places with different messages. This suggests:
- Either the messages should be standardized
- Or different exception types should be used (e.g., `XmlUploadUserInterrupted`, `XmlUploadConnectionInterrupted`)

---

## 9. Testing Considerations

### 9.1 Current State

**Observed:** Many unit tests verify exception types and messages:
```python
with pytest.raises(InputError, match="expected message"):
    function_that_should_raise()
```

**Good practices found:**
- Tests verify specific exception types (not just `Exception`)
- Tests check error message content
- Some tests verify exception chains with `__cause__`

### 9.2 Missing Test Coverage

#### **Issue 9.1: No Tests for Exception Hierarchy**

**Missing:**
- Tests verifying inheritance relationships (e.g., `isinstance(InputError(), BaseError)`)
- Tests ensuring all custom exceptions have proper `__str__` behavior
- Tests for exception message formatting (no double "ERROR:" prefix)

**Recommendation:** Add meta-tests:
```python
def test_all_exceptions_inherit_from_base_error():
    """Ensure all custom exceptions inherit from BaseError."""
    for exc_class in get_all_exception_classes():
        assert issubclass(exc_class, BaseError)

def test_exception_messages_dont_have_error_prefix():
    """Ensure exception messages don't redundantly include 'ERROR:'."""
    for exc_class in get_all_exception_classes():
        instance = exc_class("Test message")
        assert not str(instance).startswith("ERROR:")
```

#### **Issue 9.2: No Tests for Exception Conversion Patterns**

**Missing:** Tests verifying that exceptions are correctly converted between layers:
```python
def test_permanent_connection_error_converts_to_input_error_in_auth():
    """Verify authentication converts connection errors to input errors."""
    # Mock connection to raise PermanentConnectionError
    # Verify AuthenticationClient raises InputError instead
```

---

## 10. Documentation Issues

### 10.1 Docstring Quality

**Good examples:**
```python
class PermanentConnectionError(BaseError):
    """This error is raised when all attempts to reconnect to DSP have failed."""
```

**Poor examples:**
```python
class InvalidGuiAttributeError(BaseError):
    """This error is raised when a invalid gui-attribute is used."""
    # Typo: "a invalid" → "an invalid"
    # Vague: What is a gui-attribute? What makes it invalid?
```

#### **Issue 10.1: Missing Exception Documentation in Functions**

**Problem:** Many functions don't document which exceptions they raise:

```python
def create_project(...) -> bool:
    """
    Create a project on the DSP server.

    Returns:
        True if successful

    # Missing: Raises section!
    """
    raise InputError(...)
    raise PermanentConnectionError(...)
```

**Recommendation:** Add comprehensive "Raises" sections:
```python
def create_project(...) -> bool:
    """
    Create a project on the DSP server.

    Returns:
        True if successful

    Raises:
        InputError: If the project definition is invalid
        PermanentConnectionError: If the server is unreachable after retries
        BadCredentialsError: If authentication fails
    """
```

### 10.2 Missing Architecture Documentation

**Current state:** No centralized documentation explaining:
- When to use exceptions vs Problem protocol
- How to choose between exception types
- Exception conversion patterns
- Retry and recovery strategies

**Recommendation:** Create `docs/error-handling.md` with:
1. Decision tree for choosing exception types
2. Standard patterns for exception conversion
3. Guidelines for error messages
4. Examples of good and bad error handling

---

## 11. Specific Code Locations Requiring Attention

### Critical Issues (Fix First)

| Location | Issue | Severity | Recommendation |
|----------|-------|----------|----------------|
| [authentication_client_live.py:42](src/dsp_tools/clients/authentication_client_live.py#L42) | Catching exception that can't be raised | 🔴 High | Remove dead catch block |
| [entry_point.py:77](src/dsp_tools/cli/entry_point.py#L77) | Catch-all catches KeyboardInterrupt | 🔴 High | Add KeyboardInterrupt handler |
| [Multiple files](src/dsp_tools/utils/data_formats/date_util.py) | Raising raw BaseError | 🟡 Medium | Use specific exception types |
| [Multiple files](src/dsp_tools/commands/excel2json/) | Inconsistent Exception/Problem usage | 🟡 Medium | Standardize on one pattern per module |

### Refactoring Opportunities

| Location | Opportunity | Benefit |
|----------|-------------|---------|
| `exceptions.py` | Add `from __future__ import annotations` | Enable forward references |
| All exception raises | Use keyword arguments | Type safety and clarity |
| `connection_live.py` | Extract retry logic | Testability |
| `xmllib_errors.py` | Merge with main exceptions | Reduce duplication |
| All files | Remove "ERROR:" prefix | Cleaner messages |

---

## 12. Recommendations Summary

### Immediate Actions (High Priority)

1. **Fix dead code in authentication_client_live.py**
   - Remove impossible catch block
   - Add unit test to catch similar issues

2. **Add KeyboardInterrupt handling**
   - Prevent treating Ctrl+C as InternalError

3. **Standardize exception messages**
   - Remove "ERROR:" prefixes
   - Add actionable guidance
   - Fix grammar/typos

4. **Document exception hierarchy**
   - Create architecture doc
   - Add decision tree for developers

5. **Enforce keyword arguments for exceptions**
   - Prevents fragile positional argument bugs

### Medium-Term Improvements

6. **Rationalize exception hierarchy**
   - Make `PermanentTimeOutError` subclass of `PermanentConnectionError`
   - Group upload errors under common parent
   - Remove redundant xmllib exceptions

7. **Standardize Problem vs Exception usage**
   - Document when to use each
   - Consider adopting validation's return-result pattern project-wide

8. **Enhance Problem protocol**
   - Add severity levels
   - Add is_fatal() method

9. **Add meta-tests**
   - Test exception hierarchy
   - Test message formatting
   - Test conversion patterns

### Long-Term Enhancements

10. **Make retry logic configurable**
    - Extract to utility class
    - Allow configuration per-command

11. **Add development mode**
    - Preserve exception chains (ignore `from None`)
    - Show full tracebacks to stdout

12. **Create exception catalog**
    - Document all exceptions
    - Show example usage
    - Link to handling code

---

## 13. Conclusion

The DSP-TOOLS exception system has a **solid foundation** with clear user/internal error separation and good message formatting. However, it suffers from **inconsistent implementation** that undermines its effectiveness.

### Key Takeaways

**What's Working:**
- Clear exception hierarchy concept
- Excellent InternalError user guidance
- Good logging and color-coded output
- Problem protocol for validation

**What Needs Work:**
- Inconsistent exception construction (positional args)
- Ambiguous exception names and relationships
- Mixed Exception/Problem usage patterns
- Dead code and impossible catch blocks
- Missing documentation of exception semantics

### Bottom Line

This is **not a bad system**, but it shows signs of **organic growth without periodic refactoring**. With focused effort on standardization and documentation, it could become exemplary.

**Estimated effort to address critical issues:** 2-3 weeks
**Estimated effort for complete refactoring:** 6-8 weeks

---

**Report compiled by:** Claude (Sonnet 4.5)
**Analysis depth:** Complete codebase scan with focused examination of exception patterns
**Total exceptions analyzed:** 28 exception classes, 69 raise sites, 30 catch sites
