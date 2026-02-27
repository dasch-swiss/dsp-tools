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


class ExportZipExistsError(UserError):
    """This error is to be raised in case the export zip file already exists at the provided path."""


class ExportZipNotFoundError(UserError):
    """This error is to be raised in case the export zip file does not exist at the provided path."""
