from pathlib import Path

from dsp_tools.commands.xml_validate.deserialise_project import create_project_rdf
from dsp_tools.commands.xml_validate.deserialise_project import get_deserialised_lists
from dsp_tools.commands.xml_validate.deserialise_project import get_project_ontology
from dsp_tools.commands.xml_validate.prepare_input import parse_file


def xml_validate() -> bool:
    """Validates an XML file without uploading data."""
    project_deserialised = parse_file(Path("testdata/xml-validate/invalid-data.xml"))
    data_rdf = create_project_rdf(project_deserialised)
    deserialised_lists = get_deserialised_lists()
    onto = get_project_ontology()
    # data_rdf.make_graph().serialize("testdata/xml-validate/invalid-data.ttl")
    return True


xml_validate()
