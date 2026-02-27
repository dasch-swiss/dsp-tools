from dsp_tools.error.exceptions import UserError


class InvalidMigrationConfigFile(UserError):
    """This error is to be raised in case the provided config file is invalid."""


class ExportZipExistsError(UserError):
    """This error is to be raised in case the export zip file already exists at the provided path."""
