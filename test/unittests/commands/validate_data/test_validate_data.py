import pytest
from rdflib import Graph

from test.unittests.commands.validate_data.constants import PREFIXES


@pytest.fixture
def onto() -> Graph:
    ttl = f"""{PREFIXES}
    onto:One a owl:Class ;
            knora-api:isResourceClass true .
    
    knora-api:TextValue a owl:Class ;
            knora-api:isValueClass true .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    return g


@pytest.fixture
def data_ok() -> Graph:
    ttl = f"""{PREFIXES}
    <http://data/identical_text_different_prop> a onto:One ;
            onto:testSimpleText <http://data/textValue> .
    
    <http://data/textValue> a knora-api:TextValue ;
            knora-api:valueAsString "Text"^^xsd:string .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    return g


@pytest.fixture
def data_wrong() -> Graph:
    ttl = f"""{PREFIXES}
    <http://data/identical_text_different_prop> a onto:NonExistent ;
            onto:testSimpleText <http://data/textValue> .

    <http://data/textValue> a knora-api:TextValue ;
            knora-api:valueAsString "Text"^^xsd:string .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    return g


@pytest.fixture
def prefix_non_existent() -> Graph:
    ttl = f"""{PREFIXES}
    @prefix  non-existing-onto: <http://0.0.0.0:3333/ontology/9999/non-existent/v2#> .
    
    <http://data/identical_text_different_prop> a non-existing-onto:One ;
            onto:testSimpleText <http://data/textValue> .
    
    <http://data/textValue> a knora-api:TextValue ;
            knora-api:valueAsString "Text"^^xsd:string .
    """
    g = Graph()
    g.parse(data=ttl, format="turtle")
    return g


if __name__ == "__main__":
    pytest.main([__file__])
