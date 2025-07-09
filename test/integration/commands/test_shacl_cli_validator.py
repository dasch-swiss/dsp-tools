# mypy: disable-error-code="no-untyped-def"

from pathlib import Path
from uuid import uuid4

from dsp_tools.commands.validate_data.models.validation import ValidationFilePaths
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator

FILE_DIR = Path("testdata/validate-data/shacl_cli")
DATA_TTL = "data.ttl"
SHACL_TTL = "shacl.ttl"


def test_run_validate_cli():
    report_ttl = f"{uuid4()!s}.ttl"
    files = ValidationFilePaths(
        directory=FILE_DIR,
        data_file="data.ttl",
        shacl_file="shacl.ttl",
        report_file=report_ttl,
    )
    validator = ShaclCliValidator()
    validator._run_validate_cli(files)
    assert (FILE_DIR / report_ttl).is_file()
    (FILE_DIR / report_ttl).unlink()


def test_validate_conforms():
    report_ttl = f"{uuid4()!s}.ttl"
    files = ValidationFilePaths(
        directory=FILE_DIR,
        data_file="data.ttl",
        shacl_file="shacl.ttl",
        report_file=report_ttl,
    )
    validator = ShaclCliValidator()
    result = validator.validate(files)
    assert result.conforms
    (FILE_DIR / report_ttl).unlink()
