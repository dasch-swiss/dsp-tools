import shutil
import unittest
from pathlib import Path

import pytest

from dsp_tools.commands.template import generate_template_repo
from dsp_tools.models.exceptions import UserError


class TestGenerateTemplates(unittest.TestCase):  # pylint: disable=missing-class-docstring
    def test_generate_template_repo(self) -> None:
        """Test the CLI command 'template'"""
        success = generate_template_repo()
        self.assertTrue(success)

        with self.assertRaisesRegex(UserError, "already exists in your current working directory"):
            generate_template_repo()

        self.assertTrue(Path("0100-template-repo/template.json").exists())
        self.assertTrue(Path("0100-template-repo/template.xml").exists())

        shutil.rmtree("0100-template-repo")


if __name__ == "__main__":
    pytest.main([__file__])
