from dsp_tools.error.exceptions import UserError


class InvalidGuiAttributeError(UserError):
    """This error is raised when a invalid gui-attribute is used."""


class InvalidFileFormatError(UserError):
    """When the user input file does not conform to the expected format."""


class InvalidFolderStructureError(UserError):
    """When the user input file does not conform to the expected format."""


class InvalidFileContentError(UserError):
    """When the user input is not valid."""


class InvalidListSectionError(UserError):
    """When the list section did not pass validation."""
