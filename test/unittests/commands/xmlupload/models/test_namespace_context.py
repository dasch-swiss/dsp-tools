import pytest

from dsp_tools.commands.xmlupload.models.namespace_context import _get_default_json_ld_context
from dsp_tools.commands.xmlupload.models.namespace_context import get_json_ld_context_for_project


def test_get_default_context() -> None:
    context = _get_default_json_ld_context()
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
    assert context.serialise() == {"@context": expected}


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
    assert context.serialise() == {"@context": expected}


if __name__ == "__main__":
    pytest.main([__file__])
