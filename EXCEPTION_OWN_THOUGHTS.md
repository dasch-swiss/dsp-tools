## Prompt

When reading your report @EXCEPTION_HIERARCHY_CRITICAL_ANALYSIS.md,
I digged through the codebase and found some further issues.
I noted them in this document. (I hope I didn't duplicate one of your findings, by mistake).

Please create a new version of your report, and save it as a new file.
Please think about my thoughts carefully, ask me if necessary, and then include my input in the new version.

In your original report, I added some feedback, but it's clearly marked as such.
Your new version should reflect my feedback.
Again: If you disagree with my thoughts, ask back, so that we can discuss the issue.
I have also deleted some paragraphs from your original report, because they were irrelevant.
So you have to update the numbering system.

The new version of the report should be a bit less verbose, and more concise,
i.e. it should contain the same amount of information, but with less words.

If necessary, you can also use the intermediary steps from our previous conversation,
i.e. the files that you have stored under ./EXCEPTION_*.(md|txt)

Please be aware that in the meantime there were some commits to the codebase, so it has slightly changed.


## Grouping of our commands

The DSP-TOOLS functionalities (commands) can be grouped in 2 groups:

1. Server interaction commands: Can fail fast when things go wrong, but should still provide context.
  If new customer data is tested with these commands, it is always first tested in a test environment before going to prod.
  If they fail in the test environment, the data is fixed (or the DSP-TOOLS code is fixed/enhanced) until it works.
  It is okay if users cannot fix the problem themselves. They can contact the DSP-TOOLS developers.
  In the rare case of bugs in our codebase, it's okay to let it escalate until `entry_point.py` > `run()`, where it is catched anyway.
    - create
    - xmlupload
    - ingest-xmlupload
    - resume-xmlupload
2. Locally running data validation/transformation commands: Should report ALL problems clearly and allow users to fix them.
  These commands are run on the machines of the user, and it should immediately work.
  If there's a problem, it should be handled gracefully, and communicated in a user-friendly way,
  so that the users can fix the problem themselves, without contacting the developers.
  In the rare case of bugs in our codebase, it's okay to let it escalate until `entry_point.py` > `run()`, where it is catched anyway.
    - excel2json
    - excel2xml
    - xmllib
    - get
    - validate-data


## Guidelines When to Catch vs. Let Fail

We catch all exceptions at the top level (`entry_point.py` > `run()`)
to prevent Python tracebacks from reaching users.

In the implementation code, we shouldn't catch errors from your own code logic (bugs like type errors, logic mistakes).
These should crash immediately because:

- The standard Python traceback pinpoints exactly where and why the failure occurred
- Wrapping them in try-except blocks may mask the root cause (if done poorly) and delays discovery
- The test environments exists precisely to surface these issues before production
- Silent failures or generic error messages make debugging significantly harder

In the implementation code, do catch exceptions for external operations where failure is expected and recoverable:

- File I/O operations (file not found, permission denied)
- Network requests (connection failures, timeouts)
- User input validation (invalid formats, out-of-range values)
- External API calls
- external library calls that might fail in predictable ways

Only catch exceptions when you have a **specific recovery strategy**:

- Adding crucial diagnostic context not in the traceback
- Implementing retry logic for transient failures
- Gracefully degrading functionality (e.g., skipping one item in a batch)

The result is a **leaner codebase** focused on handling genuine external failures,
while bugs in your logic fail loudly and get fixed quickly.


## How to handle exceptions

Generally: When handling an internal error, where the cause of the mistake is not 100% clear, 
as much context as possible should be logged, either with `logger.exception()` or by re-raising a new exception *without* `from None`

Guideline how to re-raise exceptions:

- Use explicit chaining (`from e`) when the original exception provides valuable debugging context and directly caused your new exception.
- Use `from None` when the original exception would confuse callers or expose internal implementation details that shouldn't be visible.

Question to Claude Code: What is better, `logger.exception()` or raising without `from None`? Or both?


## Envisioned error class hierarchy

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
- What is your opinion on the CreateError? It's a functionality-specific error class for the "create" command in src/dsp_tools/commands/create
- All UserErrors that belong to xmlupload could be grouped under a class XmluploadUserError, which is a subclass of UserError


## Miscellaneous

Issues with ShaclCliValidator.validate():

- The error message says that Docker is not running, but this is already checked in `src/dsp_tools/cli/utils.py` > `check_docker_health()`
- it uses `logger.error()` instead of `logger.exception()`
- it uses `logger.error()` twice
- it raises ShaclValidationCliError from None, so the original error is lost. 
