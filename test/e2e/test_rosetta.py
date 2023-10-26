# pylint: disable=protected-access,missing-function-docstring,redefined-outer-name

import tempfile
from pathlib import Path
from typing import Iterator

import pytest

from dsp_tools.utils import rosetta


@pytest.fixture(scope="module", autouse=True)
def temporary_dir() -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def rosetta_folder(temporary_dir: Path) -> Path:
    return temporary_dir / "082E-rosetta-scripts"


def test_repo_does_not_exist(rosetta_folder: Path) -> None:
    is_rosetta_up_to_date = rosetta._update_possibly_existing_repo(rosetta_folder=rosetta_folder)
    assert not is_rosetta_up_to_date


def test_update_repo(rosetta_folder: Path) -> None:
    rosetta._clone_repo(rosetta_folder=rosetta_folder, enclosing_folder=rosetta_folder.parent)
    is_rosetta_up_to_date = rosetta._update_possibly_existing_repo(rosetta_folder=rosetta_folder)
    assert is_rosetta_up_to_date


def test_create_data_model(rosetta_folder: Path) -> None:
    success1 = rosetta._create_json(rosetta_folder=rosetta_folder)
    assert success1


def test_upload_data(rosetta_folder: Path) -> None:
    success2 = rosetta._upload_xml(rosetta_folder=rosetta_folder)
    assert success2


if __name__ == "__main__":
    pytest.main([__file__])
