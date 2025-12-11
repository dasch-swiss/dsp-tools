from dsp_tools.commands.xmlupload.models.input_problems import MultimediaFileNotFoundProblem
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
