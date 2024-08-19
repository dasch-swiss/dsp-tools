from pathlib import Path

from dsp_tools.cli.args import ServerCredentials
from dsp_tools.commands.xml_validate.prepare_input import parse_file, deserialise_xml_project


def xml_validate(xml_file: Path, creds: ServerCredentials, imgdir: Path) -> None:
    xml_project = parse_file(xml_file)
    project_deserialised = deserialise_xml_project(xml_project)
