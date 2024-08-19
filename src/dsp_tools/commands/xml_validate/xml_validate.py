from pathlib import Path

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.xml_validate.deserialise_xml import deserialise_xml_project
from dsp_tools.commands.xml_validate.utils import parse_file


def xml_validate(xml_file: Path, creds: ServerCredentials, imgdir: Path) -> None:
    xml_project = parse_file(xml_file)
    project_deserialised = deserialise_xml_project(xml_project)
