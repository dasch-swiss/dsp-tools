import shutil
from pathlib import Path

import pytest

from dsp_tools.commands.template import generate_template_repo
from dsp_tools.error.exceptions import InputError


def test_generate_template_repo() -> None:
    """Test that the command succeeds the first time, fails the second time, and that the JSON + XML file exist."""
    success = generate_template_repo()
    assert success

    with pytest.raises(InputError, match="already exists in your current working directory"):
        generate_template_repo()

    assert Path("0100-template-repo/template.json").exists()
    assert Path("0100-template-repo/template.xml").exists()

    shutil.rmtree("0100-template-repo")


if __name__ == "__main__":
    pytest.main([__file__])
