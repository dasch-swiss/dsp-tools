import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

from dsp_tools.commands import rosetta


@pytest.fixture(scope="module", autouse=True)
def rosetta_folder() -> Iterator[Path]:
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname) / "082E-rosetta-scripts"


def test_update_repo_before_cloning(rosetta_folder: Path) -> None:
    is_rosetta_up_to_date = rosetta._update_possibly_existing_repo(rosetta_folder=rosetta_folder)
    assert not is_rosetta_up_to_date


def test_update_repo_after_cloning(rosetta_folder: Path) -> None:
    rosetta._clone_repo(rosetta_folder=rosetta_folder, enclosing_folder=rosetta_folder.parent)
    is_rosetta_up_to_date = rosetta._update_possibly_existing_repo(rosetta_folder=rosetta_folder)
    assert is_rosetta_up_to_date


def test_create_data_model(rosetta_folder: Path) -> None:
    success = rosetta._create_json(rosetta_folder=rosetta_folder)
    assert success


def test_upload_data(rosetta_folder: Path) -> None:
    success = rosetta._upload_xml(rosetta_folder=rosetta_folder)
    assert success


if __name__ == "__main__":
    pytest.main([__file__])
