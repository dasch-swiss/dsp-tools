from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import UserError


class InvalidMigrationConfigFileError(UserError):
    """This error is to be raised in case the provided config file is invalid."""


class MigrationReferenceInfoIncompleteError(UserError):
    def __init__(self, required_field: str) -> None:
        msg = (
            f"The following field(s) in the migration reference file (composed by dsp-tools) must be filled "
            f"to be able to continue with the process: {required_field}.\n"
            f"You can find the reference file at the same location as the zip download."
        )
        super().__init__(msg)


class MigrationExportFailureError(InternalError):
    def __init__(self) -> None:
        msg = (
            "The migration export failed, it is not possible to continue with the process."
            "Please contact Engineering for help."
        )
        super().__init__(msg)


class MigrationDownloadFailureError(InternalError):
    def __init__(self) -> None:
        msg = (
            "The download of the migration zip failed, it is not possible to continue with the process."
            "Please contact Engineering for help."
        )
        super().__init__(msg)


class MigrationImportFailureError(InternalError):
    def __init__(self) -> None:
        msg = (
            "The import of the migration zip failed, it is not possible to continue with the process."
            "Please contact Engineering for help."
        )
        super().__init__(msg)


class MigrationExportOnServerError(UserError):
    """An export of the project already exists on the server."""

    def __init__(self, server_message: str) -> None:
        super().__init__(f"{server_message} To remove the export, use 'uvx dsp-tools migration clean-up'.")


class MigrationImportOnServerError(UserError):
    """An import of the project already exists on the server."""

    def __init__(self, server_message: str) -> None:
        msg = (
            f"{server_message} To remove the import, use 'uvx dsp-tools migration clean-up'. "
            "If you are on localhost, you can also restart the stack with 'uvx dsp-tools start-stack'."
        )
        super().__init__(msg)
