import shutil
import subprocess
from pathlib import Path

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create import create_project
from dsp_tools.commands.xmlupload.xmlupload import xmlupload
from dsp_tools.models.exceptions import UserError


def _update_possibly_existing_repo(rosetta_folder: Path) -> bool:
    """
    Makes an attempt to pull the latest version of rosetta from GitHub.

    Args:
        rosetta_folder: path to the (possibly existing) clone of the repo

    Returns:
        True if the repo exists and could be updated, False if the repo doesn't exist or couldn't be updated
    """
    is_rosetta_up_to_date = True
    if rosetta_folder.is_dir():
        print(f"Execute 'git pull' in {rosetta_folder}...")
        completed_process = subprocess.run("git pull".split(), cwd=rosetta_folder, check=False)
        if not completed_process or completed_process.returncode != 0:
            print(f"'git pull' failed. Remove '{rosetta_folder}'...")
            shutil.rmtree(rosetta_folder, ignore_errors=True)
            is_rosetta_up_to_date = False
    else:
        is_rosetta_up_to_date = False

    return is_rosetta_up_to_date


def _clone_repo(
    rosetta_folder: Path,
    enclosing_folder: Path,
) -> None:
    """
    Clones the rosetta repo into the enclosing folder.

    Args:
        rosetta_folder: path to the (not yet existing) clone
        enclosing_folder: path to the (existing) destination where rosetta should be cloned into

    Raises:
        UserError: If rosetta cannot be cloned
    """
    print(f"Clone into {rosetta_folder}...")
    cmd = "git clone https://github.com/dasch-swiss/082E-rosetta-scripts.git".split()
    completed_process = subprocess.run(cmd, cwd=enclosing_folder, check=False)
    if not completed_process or completed_process.returncode != 0:
        raise UserError("There was a problem while cloning the rosetta test project")


def _create_json(rosetta_folder: Path) -> bool:
    """
    Creates the rosetta project on the locally running DSP stack.

    Args:
        rosetta_folder: path to the clone

    Returns:
        True if the project could be created without problems, False if something went wrong during the creation process
    """
    print("Execute 'dsp-tools create rosetta.json'...")
    creds = ServerCredentials(server="http://0.0.0.0:3333", user="root@example.com", password="test")
    return create_project(
        project_file_as_path_or_parsed=rosetta_folder / "rosetta.json",
        creds=creds,
        verbose=False,
    )


def _upload_xml(rosetta_folder: Path) -> bool:
    """
    Uplaod the rosetta data on the locally running DSP stack.

    Args:
        rosetta_folder: path to the clone

    Returns:
        True if all data could be uploaded without problems, False if something went wrong during the upload process
    """
    print("Execute 'dsp-tools xmlupload rosetta.xml'...")
    creds = ServerCredentials(
        user="root@example.com",
        password="test",
        server="http://0.0.0.0:3333",
        dsp_ingest_url="http://0.0.0.0:3340",
    )
    return xmlupload(
        input_file=rosetta_folder / "rosetta.xml",
        creds=creds,
        imgdir=str(rosetta_folder),
    )


def upload_rosetta() -> bool:
    """
    This method clones https://github.com/dasch-swiss/082E-rosetta-scripts
    into ~/.dsp-tools/rosetta.
    If the repository is already there, it pulls instead of cloning.
    Then, rosetta.json is created and rosetta.xml uploaded.

    Raises:
        UserError: If the repo cannot be cloned nor pulled

    Returns:
        True if everything went well
    """

    enclosing_folder = Path.home() / Path(".dsp-tools/rosetta")
    enclosing_folder.mkdir(parents=True, exist_ok=True)
    rosetta_folder = enclosing_folder / "082E-rosetta-scripts"

    is_rosetta_up_to_date = _update_possibly_existing_repo(rosetta_folder=rosetta_folder)
    if not is_rosetta_up_to_date:
        _clone_repo(rosetta_folder=rosetta_folder, enclosing_folder=enclosing_folder)

    success1 = _create_json(rosetta_folder=rosetta_folder)
    success2 = _upload_xml(rosetta_folder=rosetta_folder)

    return success1 and success2
