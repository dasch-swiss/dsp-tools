import importlib.resources
import shutil
from pathlib import Path

from dsp_tools.error.exceptions import InputError


def generate_template_repo() -> bool:
    """
    Copies the folder src/dsp_tools/resources/0100-template-repo to the working directory.

    Raises:
        InputError: If a folder with the same name already exists in the working directory

    Returns:
        True if the folder could be copied without problems
    """
    # copy contents of src/dsp_tools/resources/0100-template-repo to cwd/template-repo
    template_path_of_user = Path("0100-template-repo")
    try:
        template_path_of_user.mkdir()
    except OSError:
        raise InputError("A folder '0100-template-repo' already exists in your current working directory.") from None
    template_path_of_distribution = importlib.resources.files("dsp_tools").joinpath("resources/0100-template-repo")
    for file in template_path_of_distribution.iterdir():
        with importlib.resources.as_file(file) as f:
            shutil.copy(f, template_path_of_user / file.name)
        print(f"Created {template_path_of_user / file.name}")

    return True
