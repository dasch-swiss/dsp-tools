import pytest

from dsp_tools.commands.get.legacy_models.context import create_context
from dsp_tools.error.exceptions import BaseError


class TestContextReduceIri:
    """Tests for Context.reduce_iri IRI manipulation."""

    def test_knora_api_prefix_returns_name_only(self) -> None:
        # System ontology prefixes return just the name
        ctx = create_context()
        result = ctx.reduce_iri("knora-api:hasValue", "myonto")
        assert result == "hasValue"

    def test_salsah_gui_prefix_returns_name_only(self) -> None:
        ctx = create_context()
        result = ctx.reduce_iri("salsah-gui:SimpleText", "myonto")
        assert result == "SimpleText"

    def test_same_ontology_returns_colon_name(self) -> None:
        # Same ontology → ":name" form
        ctx = create_context({"myonto": "http://0.0.0.0:3333/ontology/0001/myonto/v2#"})
        result = ctx.reduce_iri("myonto:MyResource", "myonto")
        assert result == ":MyResource"

    def test_different_ontology_returns_prefixed(self) -> None:
        # Different ontology keeps full prefix
        ctx = create_context(
            {
                "myonto": "http://0.0.0.0:3333/ontology/0001/myonto/v2#",
                "otheronto": "http://0.0.0.0:3333/ontology/0001/otheronto/v2#",
            }
        )
        result = ctx.reduce_iri("otheronto:OtherResource", "myonto")
        assert result == "otheronto:OtherResource"


class TestContextPrefixFromIri:
    """Tests for Context.prefix_from_iri with lazy caching."""

    def test_known_prefix_from_context(self) -> None:
        ctx = create_context({"myonto": "http://0.0.0.0:3333/ontology/0001/myonto/v2#"})
        result = ctx.prefix_from_iri("http://0.0.0.0:3333/ontology/0001/myonto/v2")
        assert result == "myonto"

    def test_lazy_cache_from_common_ontologies(self) -> None:
        # First lookup adds to context (lazy caching)
        # Note: foaf uses slash separator, but is_iri doesn't match trailing slash
        ctx = create_context()
        assert "skos" not in ctx.context
        # Use skos which has hashtag=True and doesn't end in /
        result = ctx.prefix_from_iri("http://www.w3.org/2004/02/skos/core")
        assert result == "skos"
        assert "skos" in ctx.context

    def test_invalid_iri_raises(self) -> None:
        ctx = create_context()
        with pytest.raises(BaseError, match="does not conform to IRI"):
            ctx.prefix_from_iri("not-an-iri")

    def test_unknown_iri_raises(self) -> None:
        ctx = create_context()
        # Use an IRI that doesn't end in / (which the regex doesn't match)
        with pytest.raises(BaseError, match="cannot be resolved"):
            ctx.prefix_from_iri("http://example.org/unknown/ontology")


class TestContextGetPrefixedIri:
    """Tests for Context.get_prefixed_iri."""

    def test_already_prefixed_returned_unchanged(self) -> None:
        ctx = create_context()
        result = ctx.get_prefixed_iri("myonto:MyClass")
        assert result == "myonto:MyClass"

    def test_full_iri_with_hash_separator(self) -> None:
        ctx = create_context({"myonto": "http://0.0.0.0:3333/ontology/0001/myonto/v2#"})
        result = ctx.get_prefixed_iri("http://0.0.0.0:3333/ontology/0001/myonto/v2#MyClass")
        assert result == "myonto:MyClass"

    def test_unknown_iri_returns_none(self) -> None:
        ctx = create_context()
        result = ctx.get_prefixed_iri("http://unknown.org/ontology#Something")
        assert result is None

    def test_none_input_returns_none(self) -> None:
        ctx = create_context()
        result = ctx.get_prefixed_iri(None)
        assert result is None


class TestContextGetExternalsUsed:
    """Tests for Context.get_externals_used."""

    def test_filters_knora_ontologies(self) -> None:
        # Standard ontologies are excluded
        ctx = create_context({"myonto": "http://0.0.0.0:3333/ontology/0001/myonto/v2#"})
        externals = ctx.get_externals_used()
        assert "knora-api" not in externals
        assert "salsah-gui" not in externals
        assert "rdf" not in externals
        assert "rdfs" not in externals
        assert "owl" not in externals
        assert "xsd" not in externals

    def test_includes_custom_ontologies(self) -> None:
        ctx = create_context({"myonto": "http://0.0.0.0:3333/ontology/0001/myonto/v2#"})
        externals = ctx.get_externals_used()
        assert "myonto" in externals


class TestCreateContext:
    """Tests for the create_context factory function."""

    def test_empty_input_has_standard_ontologies(self) -> None:
        ctx = create_context()
        # Should have standard ontologies
        assert "rdf" in ctx.context
        assert "rdfs" in ctx.context
        assert "owl" in ctx.context
        assert "xsd" in ctx.context
        assert "knora-api" in ctx.context
        assert "salsah-gui" in ctx.context

    def test_custom_prefix_added(self) -> None:
        ctx = create_context({"myonto": "http://example.org/ontology#"})
        assert "myonto" in ctx.context
        # Reverse context should also be set up
        assert "http://example.org/ontology" in ctx.rcontext
