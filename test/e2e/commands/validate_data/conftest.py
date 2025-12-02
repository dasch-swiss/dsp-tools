from pathlib import Path

import pytest

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.project.create.project_create_all import create
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator


@pytest.fixture(scope="module")
def shacl_validator() -> ShaclCliValidator:
    return ShaclCliValidator()


@pytest.fixture(scope="module")
def create_generic_project(creds: ServerCredentials) -> None:
    assert create(Path("testdata/validate-data/core_validation/core-validation-project-9999.json"), creds)
