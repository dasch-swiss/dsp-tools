from dsp_tools.commands.xmlupload.models.input_problems import ImageNotFoundProblem
from dsp_tools.error.exceptions import UserError

LIST_SEPARATOR = "\n   - "


class ImageNotFoundError(UserError):
    def __init__(self, imgdir: str, problems: list[ImageNotFoundProblem]) -> None:
        image_str = [f"Resource ID: {i.res_id} | Filepath: {i.filepath}" for i in problems]
        msg = (
            f"The following images do not exist in the provided image directory '{imgdir}':"
            f"\n   - {'\n   - '.join(image_str)}"
        )
        super().__init__(msg)
