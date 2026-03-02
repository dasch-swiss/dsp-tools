from dsp_tools.error.exceptions import UserError


class InvalidMigrationConfigFile(UserError):
    """This error is to be raised in case the provided config file is invalid."""


class MigrationReferenceInfoIncomplete(UserError):
    def __init__(self, required_field: str) -> None:
        msg = (
            f"The following field(s) in the migration reference file (composed by dsp-tools) must be filled "
            f"to be able to continue with the process: {required_field}.\n"
            f"You can find the reference file at the same location as the zip download."
        )
        super().__init__(msg)
