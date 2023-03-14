from pathlib import Path
import subprocess

from dsp_tools.models.exceptions import UserError
from dsp_tools.utils.project_create import create_project
from dsp_tools.utils.xml_upload import xml_upload

def upload_rosetta() -> bool:

    enclosing_folder = Path.home() / Path(".dsp-tools/rosetta")
    enclosing_folder.mkdir(parents=True, exist_ok=True)
    rosetta_folder = enclosing_folder / "082E-rosetta-scripts"
    if rosetta_folder.is_dir():
        print(f"Will execute 'git pull' in {rosetta_folder}...")
        completed_process = subprocess.run("git pull", shell=True, cwd=rosetta_folder)
        if not completed_process or completed_process.returncode != 0:
            raise UserError("There was a problem while pulling the latest version of the rosetta test project")
    else:
        print(f"Will clone into {rosetta_folder}...")
        completed_process = subprocess.run("git clone https://github.com/dasch-swiss/082e-rosetta-scripts.git", shell=True, cwd=enclosing_folder)
        if not completed_process or completed_process.returncode != 0:
            raise UserError("There was a problem while cloning the rosetta test project")
    
    print("Will execute 'dsp-tools create rosetta.json...")
    success1 = create_project(
        project_file_as_path_or_parsed=rosetta_folder/"rosetta.json",
        server="http://0.0.0.0:3333",
        user_mail="root@example.com",
        password="test",
        verbose=False,
        dump=False
    )

    print("Will execute 'dsp-tools xmlupload rosetta.xml...")
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
