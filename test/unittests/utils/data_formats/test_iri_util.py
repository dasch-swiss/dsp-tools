

import pytest

from dsp_tools.utils.data_formats.iri_util import convert_api_url_for_correct_iri_namespace_construction
from dsp_tools.utils.data_formats.iri_util import from_dsp_iri_to_prefixed_iri
from dsp_tools.utils.data_formats.iri_util import is_dsp_project_iri
from dsp_tools.utils.data_formats.iri_util import is_resource_iri
from dsp_tools.utils.data_formats.iri_util import make_dsp_ontology_prefix

HTTPS_API_URL = "https://api.stage.dasch.swiss"
HTTP_API_URL = "http://api.stage.dasch.swiss"
LOCALHOST_URL = "http://0.0.0.0:3333"


def test_is_resource_iri() -> None:
    assert is_resource_iri("https://rdfh.ch/0000/PKzNC8MFQT6NAwR3OaQEKw")
    assert is_resource_iri("http://rdfh.ch/0000/PKzNC8MFQT6NAwR3OaQEKw")
    assert is_resource_iri("https://rdfh.ch/0000/4HATaCuPQeir-L8LyhVj-Q")
    assert is_resource_iri("https://rdfh.ch/0000/31eSNdrwQkae9_0c7-753w")


def test_is_not_resource_iri() -> None:
    assert not is_resource_iri("https://knora.org/0000/PKzNC8MFQT6NAwR3OaQEKw")
    assert not is_resource_iri("https://rdfh.ch/0000/PKzNC8MFQT6NAwR3OaQ")
    assert not is_resource_iri("www.rdfh.ch/0000/PKzNC8MFQT6NAwR3OaQEKw")


@pytest.mark.parametrize(
    "iri",
    [
        "http://0.0.0.0:3333/ontology/482F/e2e-testonto/v2#ImageResource",
        "http://api.dasch.swiss/ontology/4125/e2e-testonto/v2#ImageResource",
        "http://api.dasch.swiss/ontology/000F/e2e-testonto/v2#hasFile",
    ],
)
def test_is_dsp_project_iri_true(iri):
    result = is_dsp_project_iri(iri)
    assert result is True


@pytest.mark.parametrize(
    "iri",
    [
        "http://0.0.0.0:3333/ontology/4125/e2e-testonto/ImageResource",  # no v2
        "http://api.knora.org/ontology/knora-api/v2#Resource",
        "https://schema.org/Person",
        "http://www.cidoc-crm.org/cidoc-crm/E1_CRM_Entity",
    ],
)
def test_is_dsp_project_iri_false(iri):
    result = is_dsp_project_iri(iri)
    assert result is False


@pytest.mark.parametrize(
    ("iri", "expected"),
    [
        ("http://0.0.0.0:3333/ontology/4125/e2e-testonto/v2#ImageResource", "e2e-testonto:ImageResource"),
        ("https://api.dasch.swiss/ontology/4125/e2e-testonto/v2#ImageResource", "e2e-testonto:ImageResource"),
        ("http://0.0.0.0:3333/completely-unexpected", "http://0.0.0.0:3333/completely-unexpected"),
    ],
)
def test_from_dsp_iri_to_prefixed_iri(iri, expected):
    result = from_dsp_iri_to_prefixed_iri(iri)
    assert result == expected


@pytest.mark.parametrize(
    ("input_str", "expected"),
    [
        (HTTPS_API_URL, HTTP_API_URL),
        (LOCALHOST_URL, LOCALHOST_URL),
    ],
)
def test_convert_api_url_for_correct_iri_namespace(input_str, expected):
    assert convert_api_url_for_correct_iri_namespace_construction(input_str) == expected


@pytest.mark.parametrize(
    ("api_url", "fixed_api"),
    [
        (HTTPS_API_URL, HTTP_API_URL),
        (LOCALHOST_URL, LOCALHOST_URL),
    ],
)
def test_make_dsp_ontology_prefix(api_url, fixed_api):
    expected = f"{fixed_api}/ontology/9999/onto/v2#"
    assert make_dsp_ontology_prefix(api_url, "9999", "onto") == expected


if __name__ == "__main__":
    pytest.main([__file__])
