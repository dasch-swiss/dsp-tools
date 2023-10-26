# pylint: disable=protected-access,missing-function-docstring,redefined-outer-name

import shutil
from pathlib import Path

import pytest

from dsp_tools.utils import rosetta

# @pytest.fixture
# def setup_teardown():
#     print("setup")
#     yield
#     print("teardown")

# @pytest.fixture
# def temporary_dir() -> Path:
#     with tempfile.TemporaryDirectory() as tmpdirname:
#         yield Path(tmpdirname)


@pytest.fixture
def enclosing_folder() -> Path:
    return Path("tmp/.dsp-tools/rosetta")


@pytest.fixture
def rosetta_folder(enclosing_folder: Path) -> Path:
    return enclosing_folder / "082E-rosetta-scripts"


def test_repo_does_not_exist(enclosing_folder: Path, rosetta_folder: Path) -> None:
    enclosing_folder.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(rosetta_folder, ignore_errors=True)
    is_rosetta_up_to_date = rosetta._update_possibly_existing_repo(rosetta_folder=rosetta_folder)
    assert not is_rosetta_up_to_date


def test_update_repo(enclosing_folder: Path, rosetta_folder: Path) -> None:
    rosetta._clone_repo(rosetta_folder=rosetta_folder, enclosing_folder=enclosing_folder)
    is_rosetta_up_to_date = rosetta._update_possibly_existing_repo(rosetta_folder=rosetta_folder)
    assert is_rosetta_up_to_date


def test_create_data_model(rosetta_folder: Path) -> None:
    success1 = rosetta._create_json(rosetta_folder=rosetta_folder)
    assert success1


def test_upload_data(rosetta_folder: Path) -> None:
    success2 = rosetta._upload_xml(rosetta_folder=rosetta_folder)
    assert success2
    shutil.rmtree("tmp", ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__])
