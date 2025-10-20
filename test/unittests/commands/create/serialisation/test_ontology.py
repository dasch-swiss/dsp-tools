from rdflib import XSD
from rdflib import Literal

from dsp_tools.commands.create.serialisation.ontology import make_ontology_base_graph
from test.unittests.commands.create.serialisation.fixtures import ONTO_IRI

LAST_MODIFICATION_DATE = Literal("2025-10-14T13:00:00.000000Z", XSD.dateTimeStamp)


def test_creates_graph_with_correct_structure() -> None:
    result = make_ontology_base_graph(ONTO_IRI, LAST_MODIFICATION_DATE)
    assert len(result) == 2
