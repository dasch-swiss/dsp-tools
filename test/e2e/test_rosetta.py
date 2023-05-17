# pylint: disable=protected-access,missing-class-docstring,missing-function-docstring

import shutil
import unittest
from pathlib import Path

import pytest

from dsp_tools.utils import rosetta


class TestRosetta(unittest.TestCase):

    def test_rosetta(self) -> None:
        enclosing_folder = Path("tmp/.dsp-tools/rosetta")
        enclosing_folder.mkdir(parents=True, exist_ok=True)
        rosetta_folder = enclosing_folder / "082E-rosetta-scripts"

        is_rosetta_up_to_date = rosetta._update_possibly_existing_repo(rosetta_folder=rosetta_folder)
        self.assertFalse(is_rosetta_up_to_date)

        rosetta._clone_repo(rosetta_folder=rosetta_folder, enclosing_folder=enclosing_folder)
        is_rosetta_up_to_date = rosetta._update_possibly_existing_repo(rosetta_folder=rosetta_folder)
        self.assertTrue(is_rosetta_up_to_date)

        success1 = rosetta._create_json(rosetta_folder=rosetta_folder)
        self.assertTrue(success1)
        success2 = rosetta._upload_xml(rosetta_folder=rosetta_folder)
        self.assertTrue(success2)

        shutil.rmtree("tmp", ignore_errors=True)

if __name__ == "__main__":
    pytest.main([__file__])
