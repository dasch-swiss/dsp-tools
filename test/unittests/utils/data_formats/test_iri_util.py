import pytest

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


if __name__ == "__main__":
    pytest.main([__file__])
