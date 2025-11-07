Please search the codebase if there are occurrences where we log the same error multiple times.
I guess we should avoid catching an error, logging it, re-raising it, and then catch and log it in the caller.
If you find such a thing, please add it to the report.

Proposed Exception Hierarchy Redesign: 

- Please update the Proposed Structure to also reflect the proposed renamings
- InvalidInputError should be a subclass of InternalError, and marked as deprecated,
  because it's only used by the deprecated `Connection` class and the old `create` command code.
- InvalidIngestFileNameError should be a direct subclass of InternalError
- BadCredentialsError should be a subclass of UserError, because the user can fix it
- CreateError and ProjectNotFoundError are user-fixable -> subclass of UserError

Please add to the report that `parse_json_file()` in `src/dsp_tools/utils/json_parsing.py`
doesn't follow the pattern in "How to Handle Exceptions". 
In addition, it doesn't pass on the parsing error to the user, so the user doesn't have a chance to fix his JSON.

Your "Proposed Exception Hierarchy Redesign" lists some exceptions 2 times in the hierarchy.
