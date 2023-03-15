from pathlib import Path
import shutil
import subprocess

from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.project_create import create_project
from dsp_tools.utils.xml_upload import xml_upload

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
    
    if rosetta_folder.is_dir():
        cloning_necessary = False
        print(f"Make 'git pull' in {rosetta_folder}...")
        completed_process = subprocess.run("git pull", shell=True, cwd=rosetta_folder)
        if not completed_process or completed_process.returncode != 0:
            print(f"'git pull' failed. Remove '{rosetta_folder}'...")
            shutil.rmtree(rosetta_folder, ignore_errors=True)
            cloning_necessary = True
    else:
        cloning_necessary = True
    
    if cloning_necessary:
        print(f"Clone into {rosetta_folder}...")
        completed_process = subprocess.run("git clone https://github.com/dasch-swiss/082E-rosetta-scripts.git", shell=True, cwd=enclosing_folder)
        if not completed_process or completed_process.returncode != 0:
            raise UserError("There was a problem while cloning the rosetta test project")
    
    print("Execute 'dsp-tools create rosetta.json'...")
    success1 = create_project(
        project_file_as_path_or_parsed=rosetta_folder/"rosetta.json",
        server="http://0.0.0.0:3333",
        user_mail="root@example.com",
        password="test",
        verbose=False,
        dump=False
    )

    print("Execute 'dsp-tools xmlupload rosetta.xml'...")
    success2 = xml_upload(
        input_file=rosetta_folder/"rosetta.xml",
        server="http://0.0.0.0:3333",
        user="root@example.com",
        password="test",
        imgdir=".",
        sipi="http://0.0.0.0:1024",
        verbose=False,
        incremental=False,
        save_metrics=False
    )
    
    return success1 and success2
