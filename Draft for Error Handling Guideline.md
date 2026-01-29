# Draft for Error Handling Guideline

**Status:** This is a draft guideline. The exception hierarchy described here (BaseError, UserError, InternalError)
has been implemented (January 2026), but these guidelines are not yet systematically enforced in the codebase.

--> **Please consider only the content of this draft, and ignore its form.**


## 1 Whenever An Exception Is Raised, Either Of 2 Situations Applies

Actions taken by DSP-TOOLS fall into two categories with different error handling needs.
Whenever an exception is raised, the developer must decide which situation applies.

### 1. Developer assistance necessary: Fail-fast acceptable

- For commands that are tested in local/test environments before production
- For situations when it's acceptable that users need developer assistance to resolve the issue
- The exception might escalate ugly.
- Bugs can escalate to top-level handler in `entry_point.py`

### 2. Situations that must be fixable by the user 

- Local validation/transformation commands must work immediately on user machines.
- Users must be able to fix issues themselves without contacting developers
- They must report all problems aggregated in a user-friendly way.
- Errors should be handled gracefully with user-friendly messages
- Bugs can escalate to top-level handler in `entry_point.py`



## 2 Guidelines: When to Catch vs. Let Fail

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



## 3 How to Handle Exceptions

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
class JSONFileParsingError(UserError):
    filepath: Path
    orig_err_msg: str

    def __str__(self) -> str:
        return f"The input file '{self.filepath}' cannot be parsed due to the following problem: {self.orig_err_msg}"
```
