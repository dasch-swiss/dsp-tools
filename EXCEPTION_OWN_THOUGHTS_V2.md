Please search the codebase if there are occurrences where we log the same error multiple times.
I guess we should avoid catching an error, logging it, re-raising it, and then catch and log it in the caller.
If you find such a thing, please add it to the report.

Please add to the report that `parse_json_file()` in `src/dsp_tools/utils/json_parsing.py`
doesn't follow the pattern in "How to Handle Exceptions". 
In addition, it doesn't pass on the parsing error to the user, so the user doesn't have a chance to fix his JSON.

