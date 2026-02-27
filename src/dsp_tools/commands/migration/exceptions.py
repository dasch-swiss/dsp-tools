from dsp_tools.error.exceptions import UserError


class InvalidMigrationConfigFile(UserError):
    """This error is to be raised in case the provided config file is invalid."""


class MigrationReferenceInfoIncomplete(UserError):
    def __init__(self, required_field: str) -> None:
        msg = (
            f"The following field(s) in the reference file must be filled "
            f"to be able to continue with the process: {required_field}"
        )
        super().__init__(msg)
