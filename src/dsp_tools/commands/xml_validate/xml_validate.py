from pathlib import Path

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.xml_validate.utils import parse_file


def xml_validate(xml_file: Path, creds: ServerCredentials, imgdir: Path) -> bool:
    xml_project = parse_file(xml_file)
