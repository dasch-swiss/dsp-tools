from dsp_tools.clients.exceptions import InvalidInputError
from dsp_tools.commands.xmlupload.models.input_problems import MultimediaFileNotFoundProblem
from dsp_tools.error.exceptions import BaseError
from dsp_tools.error.exceptions import InternalError
from dsp_tools.error.exceptions import UserError

LIST_SEPARATOR = "\n   - "


class MultimediaFileNotFound(UserError):
    def __init__(self, imgdir: str, problems: list[MultimediaFileNotFoundProblem]) -> None:
        image_str = [f"Resource ID: {i.res_id} | Filepath: {i.filepath}" for i in problems]
        msg = (
            f"The following multimedia files do not exist in the provided directory '{imgdir}':"
            f"\n   - {'\n   - '.join(image_str)}"
        )
        super().__init__(msg)


class InvalidIngestFileNameError(InvalidInputError):
    """This error is raised if INGEST rejects a file due to its name."""


class XmlUploadError(BaseError):
    """Represents an error raised in the context of the xmlupload."""


class XmlUploadInterruptedError(XmlUploadError):
    """Represents an error raised when the xmlupload was interrupted."""


class XmlInputConversionError(InternalError):
    """Represents an error raised in the context of the xmlupload."""


class Id2IriReplacementError(UserError):
    """Represents an error raised if an internal ID could not be found in the Id2Iri mapping."""


class XmlUploadPermissionsNotFoundError(UserError):
    """Class for errors that are raised when a permission does not exist."""


class XmlUploadAuthorshipsNotFoundError(UserError):
    """Class for errors that are raised when an authorship id does not exist."""


class XmlUploadListNodeNotFoundError(UserError):
    """Class for errors that are raised when a list node does not exist."""
