import pytest
from rdflib.namespace import Namespace

from dsp_tools.commands.xmlupload.models.namespace_context import NamespaceContext
from dsp_tools.commands.xmlupload.models.namespace_context import get_json_ld_context_for_project


def test_namespace_context_get_json_ld() -> None:
    test_context = NamespaceContext({"testonto": Namespace("http://www.knora.org/ontology/testonto#")})
    res_json = test_context.get_json_ld()
    expected = {
        "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
        "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "testonto": "http://www.knora.org/ontology/testonto#",
    }
    assert res_json == expected


def test_namespace_context_get_json_ld_multiple_ontos() -> None:
    test_context = NamespaceContext(
        {
            "testonto": Namespace("http://www.knora.org/ontology/testonto#"),
            "testonto2": Namespace("http://www.knora.org/ontology/testonto2#"),
        }
    )
    res_json = test_context.get_json_ld()
    expected = {
        "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
        "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "testonto": "http://www.knora.org/ontology/testonto#",
        "testonto2": "http://www.knora.org/ontology/testonto2#",
    }
    assert res_json == expected


def test_get_json_ld_context_for_project() -> None:
    context = get_json_ld_context_for_project({"testonto": "http://www.knora.org/ontology/testonto"})
    expected = {
        "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
        "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "testonto": "http://www.knora.org/ontology/testonto#",
    }
    assert context == expected


def test_get_json_ld_context_for_project_with_multiple_ontologies() -> None:
    context = get_json_ld_context_for_project(
        {
            "testonto": "http://www.knora.org/ontology/testonto",
            "testonto2": "http://www.knora.org/ontology/testonto2",
        }
    )
    expected = {
        "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
        "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "testonto": "http://www.knora.org/ontology/testonto#",
        "testonto2": "http://www.knora.org/ontology/testonto2#",
    }
    assert context == expected


if __name__ == "__main__":
    pytest.main([__file__])
