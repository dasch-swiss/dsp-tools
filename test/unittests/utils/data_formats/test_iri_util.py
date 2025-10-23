import pytest

from dsp_tools.utils.data_formats.iri_util import from_dsp_iri_to_prefixed_iri
from dsp_tools.utils.data_formats.iri_util import is_resource_iri


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


if __name__ == "__main__":
    pytest.main([__file__])
