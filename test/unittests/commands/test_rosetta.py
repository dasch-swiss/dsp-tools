from pathlib import Path

import pytest

from dsp_tools.commands import rosetta


def test_update_repo_before_cloning(tmp_path: Path) -> None:
    rosetta_folder = tmp_path / "082E-rosetta-scripts"
    is_rosetta_up_to_date = rosetta._update_possibly_existing_repo(rosetta_folder=rosetta_folder)
    assert not is_rosetta_up_to_date


def test_update_repo_after_cloning(tmp_path: Path) -> None:
    rosetta_folder = tmp_path / "082E-rosetta-scripts"
    rosetta._clone_repo(rosetta_folder=rosetta_folder, enclosing_folder=tmp_path)
    is_rosetta_up_to_date = rosetta._update_possibly_existing_repo(rosetta_folder=rosetta_folder)
    assert is_rosetta_up_to_date


if __name__ == "__main__":
    pytest.main([__file__])
