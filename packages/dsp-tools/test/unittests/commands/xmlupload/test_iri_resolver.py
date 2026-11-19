import pytest

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver


@pytest.fixture
def resolver() -> IriResolver:
    return IriResolver()


def test_empty_resolver(resolver: IriResolver) -> None:
    assert not resolver.non_empty()


def test_non_empty_resolver(resolver: IriResolver) -> None:
    resolver.update("a", "http://example.com/iri#a")
    assert resolver.non_empty()


def test_get_available(resolver: IriResolver) -> None:
    resolver.update("a", "http://example.com/iri#a")
    assert resolver.get("a") == "http://example.com/iri#a"


def test_not_get_unavailable(resolver: IriResolver) -> None:
    resolver.update("a", "http://example.com/iri#a")
    assert resolver.get("b") is None


def test_update_previous_value(resolver: IriResolver) -> None:
    resolver.update("a", "http://example.com/iri#a")
    assert resolver.get("a") == "http://example.com/iri#a"
    resolver.update("a", "http://example.com/iri#aaa")
    assert resolver.get("a") == "http://example.com/iri#aaa"


if __name__ == "__main__":
    pytest.main([__file__])
