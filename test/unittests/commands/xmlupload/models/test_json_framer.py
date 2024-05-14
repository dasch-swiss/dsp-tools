import pytest
from rdflib import RDF
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace

from dsp_tools.commands.xmlupload.models.serialise.json_framer import frame_value

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")
MY_ONTO = Namespace("http://0.0.0.0:3333/ontology/0009/myonto/v2#")


@pytest.fixture()
def int_value() -> Graph:
    g = Graph()
    res_bn = BNode()
    val_bn = BNode()
    g.add((res_bn, RDF.type, MY_ONTO.Thing))
    g.add((res_bn, MY_ONTO.hasInteger, val_bn))
    g.add((val_bn, RDF.type, KNORA_API.IntValue))
    g.add((val_bn, KNORA_API.intValueAsInt, Literal(4)))
    return g


def test_frame_json_value_only(int_value: Graph) -> None:
    expected = {
        "http://0.0.0.0:3333/ontology/0009/myonto/v2#hasInteger": {
            "@type": "http://api.knora.org/ontology/knora-api/v2#IntValue",
            "http://api.knora.org/ontology/knora-api/v2#intValueAsInt": 4,
        }
    }
    result = frame_value(int_value, MY_ONTO.Thing)
    assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])
