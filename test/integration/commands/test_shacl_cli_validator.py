from pathlib import Path

from dsp_tools.commands.validate_data.models.validation import ValidationFilePaths
from dsp_tools.commands.validate_data.shacl_cli_validator import ShaclCliValidator


def test_run_validate_cli():
    file_dir = Path("testdata/e2e/shacl_cli")
    report_file = "report.ttl"
    files = ValidationFilePaths(
        directory=file_dir, data_file="data.ttl", shacl_file="shacl.ttl", report_file=report_file
    )
    validator = ShaclCliValidator()
    validator._run_validate_cli(files)
    assert (file_dir / report_file).is_file()
