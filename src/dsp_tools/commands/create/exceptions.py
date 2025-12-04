from dsp_tools.error.exceptions import InputError


class ProjectJsonSchemaValidationError(InputError):
    def __init__(self, file_input: str | None, details_msg: str) -> None:
        msg = (
            f"The JSON file '{file_input}' did not pass the schema validation. "
            f"We found the following error:\n{details_msg}"
        )
        super().__init__(msg)
