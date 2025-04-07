import shutil
import unittest
from pathlib import Path

import pytest

from dsp_tools.commands.template import generate_template_repo
from dsp_tools.error.exceptions import InputError

# ruff: noqa: PT009 (pytest-unittest-assertion) (remove this line when pytest is used instead of unittest)
# ruff: noqa: PT027 (pytest-unittest-raises-assertion) (remove this line when pytest is used instead of unittest)


class TestGenerateTemplates(unittest.TestCase):
    """Test the CLI command 'template'"""

    def test_generate_template_repo(self) -> None:
        """Test that the command succeeds the first time, fails the second time, and that the JSON + XML file exist."""
        success = generate_template_repo()
        self.assertTrue(success)

        with self.assertRaisesRegex(InputError, "already exists in your current working directory"):
            generate_template_repo()

        self.assertTrue(Path("0100-template-repo/template.json").exists())
        self.assertTrue(Path("0100-template-repo/template.xml").exists())

        shutil.rmtree("0100-template-repo")


if __name__ == "__main__":
    pytest.main([__file__])
