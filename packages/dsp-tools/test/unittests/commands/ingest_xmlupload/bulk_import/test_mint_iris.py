import pytest
import regex

from dsp_tools.commands.ingest_xmlupload.bulk_import.mint_iris import make_resource_iri
from dsp_tools.commands.ingest_xmlupload.bulk_import.mint_iris import make_value_iri
from dsp_tools.commands.ingest_xmlupload.bulk_import.mint_iris import mint_resource_iris
from dsp_tools.commands.ingest_xmlupload.exceptions import ForeignShortcodeIriError
from dsp_tools.commands.xmlupload.models.processed.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.prepare_xml_input.ark2iri import convert_ark_v0_to_resource_iri


def _resource(res_id: str, iri: str | None = None) -> ProcessedResource:
    metadata = MigrationMetadata(iri, None) if iri else None
    return ProcessedResource(
        res_id=res_id,
        type_iri="http://0.0.0.0:3333/ontology/1234/onto/v2#Class",
        label="label",
        permissions=None,
        values=[],
        migration_metadata=metadata,
    )


def test_make_resource_iri() -> None:
    assert regex.fullmatch(r"http://rdfh\.ch/1234/[A-Za-z0-9_-]{22}", make_resource_iri("1234"))


def test_make_resource_iri_upper_cases_shortcode() -> None:
    assert make_resource_iri("080c").startswith("http://rdfh.ch/080C/")


def test_make_resource_iri_is_unique() -> None:
    assert make_resource_iri("1234") != make_resource_iri("1234")


def test_make_value_iri() -> None:
    res_iri = make_resource_iri("1234")
    assert regex.fullmatch(regex.escape(res_iri) + r"/values/[A-Za-z0-9_-]{22}", make_value_iri(res_iri))


def test_make_value_iri_is_unique() -> None:
    res_iri = make_resource_iri("1234")
    assert make_value_iri(res_iri) != make_value_iri(res_iri)


def test_mint_resource_without_metadata() -> None:
    resolver = mint_resource_iris([_resource("a")], "1234")
    assert regex.fullmatch(r"http://rdfh\.ch/1234/[A-Za-z0-9_-]{22}", resolver.get("a") or "")


def test_mint_resource_keeps_preset_iri() -> None:
    preset = "http://rdfh.ch/1234/custom-iri"
    resolver = mint_resource_iris([_resource("a", preset)], "1234")
    assert resolver.get("a") == preset


def test_mint_resource_keeps_ark_derived_iri() -> None:
    ark_iri = convert_ark_v0_to_resource_iri("ark:/72163/080c-779b9990a0c3f-6e")
    resolver = mint_resource_iris([_resource("a", ark_iri)], "080C")
    assert resolver.get("a") == ark_iri


def test_mint_resource_accepts_preset_iri_with_other_case() -> None:
    preset = "http://rdfh.ch/080c/custom-iri"
    resolver = mint_resource_iris([_resource("a", preset)], "080C")
    assert resolver.get("a") == preset


def test_mint_resource_rejects_iri_outside_rdfh() -> None:
    with pytest.raises(ForeignShortcodeIriError):
        mint_resource_iris([_resource("a", "http://example.org/1234/x")], "1234")


def test_mint_resource_foreign_shortcode_lists_all() -> None:
    resources = [
        _resource("ok", "http://rdfh.ch/1234/x"),
        _resource("bad1", "http://rdfh.ch/9999/x"),
        _resource("bad2", "http://rdfh.ch/8888/y"),
    ]
    with pytest.raises(ForeignShortcodeIriError) as exc_info:
        mint_resource_iris(resources, "1234")
    message = str(exc_info.value)
    assert "bad1" in message
    assert "http://rdfh.ch/9999/x" in message
    assert "bad2" in message
    assert "'ok'" not in message
