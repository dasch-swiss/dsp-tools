from dsp_tools.utils.json_ld_util import get_default_json_ld_context, get_json_ld_context_for_project

# ruff: noqa: D103 (undocumented-public-function)


def test_get_default_context() -> None:
    context = get_default_json_ld_context()
    expected = {
        "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
        "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
    }
    assert context == expected


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
