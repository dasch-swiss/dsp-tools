from dsp_tools.commands.create.create_on_server.ontology import make_ontology_base_graph
from test.unittests.commands.create.create_on_server.fixtures import LAST_MODIFICATION_DATE
from test.unittests.commands.create.create_on_server.fixtures import ONTO_IRI


def test_creates_graph_with_correct_structure() -> None:
    result = make_ontology_base_graph(ONTO_IRI, LAST_MODIFICATION_DATE)
    assert len(result) == 2
