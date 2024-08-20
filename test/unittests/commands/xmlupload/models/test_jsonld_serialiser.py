import pytest
from rdflib import RDF
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.models.serialise.jsonld_serialiser import _frame_property
from dsp_tools.commands.xmlupload.models.serialise.jsonld_serialiser import serialise_property_graph

KNORA_API = Namespace("http://api.knora.org/ontology/knora-api/v2#")
MY_ONTO = Namespace("http://0.0.0.0:3333/ontology/0009/myonto/v2#")


@pytest.fixture
def int_value() -> Graph:
    g = Graph()
    res_bn = BNode()
    val_bn = BNode()
    g.add((res_bn, MY_ONTO.hasInteger, val_bn))
    g.add((val_bn, RDF.type, KNORA_API.IntValue))
    g.add((val_bn, KNORA_API.intValueAsInt, Literal(1)))
    return g


@pytest.fixture
def int_value_with_comment() -> Graph:
    g = Graph()
    res_bn = BNode()
    val_bn = BNode()
    g.add((res_bn, MY_ONTO.hasInteger, val_bn))
    g.add((val_bn, RDF.type, KNORA_API.IntValue))
    g.add((val_bn, KNORA_API.intValueAsInt, Literal(2)))
    g.add((val_bn, KNORA_API.hasPermissions, Literal("CR knora-admin:Creator")))
    g.add((val_bn, KNORA_API.valueHasComment, Literal("this is the number 2")))
    return g


@pytest.fixture
def two_int_values() -> Graph:
    g = Graph()
    res_bn = BNode()
    val_bn1 = BNode()
    g.add((res_bn, MY_ONTO.hasInteger, val_bn1))
    g.add((val_bn1, RDF.type, KNORA_API.IntValue))
    g.add((val_bn1, KNORA_API.intValueAsInt, Literal(1)))
    val_bn2 = BNode()
    g.add((res_bn, MY_ONTO.hasInteger, val_bn2))
    g.add((val_bn2, RDF.type, KNORA_API.IntValue))
    g.add((val_bn2, KNORA_API.intValueAsInt, Literal(2)))
    return g


class TestSerialiseProperty:
    def test_one_value(self, int_value: Graph) -> None:
        expected = {
            "http://0.0.0.0:3333/ontology/0009/myonto/v2#hasInteger": {
                "@type": "http://api.knora.org/ontology/knora-api/v2#IntValue",
                "http://api.knora.org/ontology/knora-api/v2#intValueAsInt": 1,
            }
        }
        result = serialise_property_graph(int_value, MY_ONTO.hasInteger)
        assert result == expected

    def test_value_with_comments(self, int_value_with_comment: Graph) -> None:
        expected = {
            "http://0.0.0.0:3333/ontology/0009/myonto/v2#hasInteger": {
                "@type": "http://api.knora.org/ontology/knora-api/v2#IntValue",
                "http://api.knora.org/ontology/knora-api/v2#hasPermissions": "CR knora-admin:Creator",
                "http://api.knora.org/ontology/knora-api/v2#valueHasComment": "this is the number 2",
                "http://api.knora.org/ontology/knora-api/v2#intValueAsInt": 2,
            }
        }
        result = serialise_property_graph(int_value_with_comment, MY_ONTO.hasInteger)
        assert result == expected

    def test_several_values(self, two_int_values: Graph) -> None:
        expected = {
            "http://0.0.0.0:3333/ontology/0009/myonto/v2#hasInteger": [
                {
                    "@type": "http://api.knora.org/ontology/knora-api/v2#IntValue",
                    "http://api.knora.org/ontology/knora-api/v2#intValueAsInt": 1,
                },
                {
                    "@type": "http://api.knora.org/ontology/knora-api/v2#IntValue",
                    "http://api.knora.org/ontology/knora-api/v2#intValueAsInt": 2,
                },
            ],
        }

        result = serialise_property_graph(two_int_values, MY_ONTO.hasInteger)
        assert result == expected


def test_frame_property() -> None:
    json_graph = [
        {
            "@id": "_:res_id",
            "http://0.0.0.0:3333/ontology/0009/myonto2/v2#hasInteger": [{"@id": "_:1"}],
            "http://0.0.0.0:3333/ontology/0009/myonto/v2#hasGeoname": [{"@id": "_:2"}, {"@id": "_:3"}],
        },
        {
            "@id": "_:1",
            "@type": ["http://api.knora.org/ontology/knora-api/v2#IntValue"],
            "http://api.knora.org/ontology/knora-api/v2#intValueAsInt": [{"@value": 1}],
        },
        {
            "@id": "_:2",
            "@type": ["http://api.knora.org/ontology/knora-api/v2#GeonameValue"],
            "http://api.knora.org/ontology/knora-api/v2#geonameValueAsGeonameCode": [{"@value": "geo2"}],
        },
        {
            "@id": "_:3",
            "@type": ["http://api.knora.org/ontology/knora-api/v2#GeonameValue"],
            "http://api.knora.org/ontology/knora-api/v2#geonameValueAsGeonameCode": [{"@value": "geo3"}],
        },
    ]
    expected = {
        "http://0.0.0.0:3333/ontology/0009/myonto2/v2#hasInteger": {
            "@type": "http://api.knora.org/ontology/knora-api/v2#IntValue",
            "http://api.knora.org/ontology/knora-api/v2#intValueAsInt": 1,
        },
        "http://0.0.0.0:3333/ontology/0009/myonto/v2#hasGeoname": [
            {
                "@type": "http://api.knora.org/ontology/knora-api/v2#GeonameValue",
                "http://api.knora.org/ontology/knora-api/v2#geonameValueAsGeonameCode": "geo2",
            },
            {
                "@type": "http://api.knora.org/ontology/knora-api/v2#GeonameValue",
                "http://api.knora.org/ontology/knora-api/v2#geonameValueAsGeonameCode": "geo3",
            },
        ],
    }
    res = _frame_property(json_graph, URIRef("http://0.0.0.0:3333/ontology/0009/myonto2/v2#hasInteger"))
    assert res == expected


if __name__ == "__main__":
    pytest.main([__file__])
