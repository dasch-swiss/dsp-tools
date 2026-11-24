import json
import re
import warnings
from pathlib import Path
from typing import Any

import pytest
from rdflib import XSD
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.ingest_xmlupload.bulk_import import write_payload as write_payload_module
from dsp_tools.commands.ingest_xmlupload.bulk_import.mint_iris import mint_resource_iris
from dsp_tools.commands.ingest_xmlupload.bulk_import.write_payload import write_payload_file
from dsp_tools.commands.ingest_xmlupload.exceptions import ResourceIriMissingError
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.formatted_text_value import FormattedTextValue
from dsp_tools.commands.xmlupload.models.lookup_models import IRILookups
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileBitstream
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileMetadata
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValue
from dsp_tools.commands.xmlupload.models.processed.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedList
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedRichtext
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedSimpleText
from dsp_tools.utils.rdf_constants import KNORA_API
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraFileValueType

ONTO = "http://0.0.0.0:3333/ontology/0001/onto/v2#"
SHORTCODE = "0001"
LIST_NODE_IRI = "http://rdfh.ch/0001/lists/node"
UUID_RE = "[A-Za-z0-9_-]{22}"
NUM_NODES_RES_WITH_ONE_VALUE = 2
FAILING_CALL = 2
META = ProcessedFileMetadata(license_iri="http://rdfh.ch/licenses/cc-by-4.0", copyright_holder="h", authorships=["a"])


def _resource(res_id: str, values: list[Any] | None = None, **kwargs: Any) -> ProcessedResource:
    return ProcessedResource(
        res_id=res_id,
        type_iri=f"{ONTO}Class",
        label=res_id,
        permissions=None,
        values=values or [],
        **kwargs,
    )


def _link(target_id: str, order: int = 0) -> ProcessedLink:
    return ProcessedLink(target_id, f"{ONTO}hasLinkTo", None, None, order, "uuid")


def _write(resources: list[ProcessedResource], tmp_path: Path) -> tuple[Path, dict[str, str]]:
    resolver = mint_resource_iris(resources, SHORTCODE)
    lookups = IRILookups(project_iri=URIRef("http://rdfh.ch/projects/proj"), id_to_iri=resolver)
    target = tmp_path / "payload.jsonld"
    write_payload_file(resources, lookups, target)
    return target, dict(resolver.lookup)


def _parse(target: Path) -> Graph:
    # rdflib's JSON-LD parser emits a DeprecationWarning of its own.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return Graph().parse(data=target.read_text(encoding="utf-8"), format="json-ld")


def test_file_is_one_list_without_blank_nodes(tmp_path):
    target, _ = _write([_resource("a", [_link("b")]), _resource("b")], tmp_path)
    assert isinstance(json.loads(target.read_text(encoding="utf-8")), list)
    graph = _parse(target)
    assert len(graph) > 0
    assert not [n for t in graph for n in t if isinstance(n, BNode)]
    assert not list(tmp_path.glob("*.part"))


def test_zero_resources(tmp_path):
    target, _ = _write([], tmp_path)
    assert json.loads(target.read_text(encoding="utf-8")) == []


def test_iri_shapes(tmp_path):
    target, iris = _write([_resource("a", [ProcessedSimpleText("x", f"{ONTO}hasText", None, None, 0)])], tmp_path)
    nodes = json.loads(target.read_text(encoding="utf-8"))
    ids = [n["@id"] for n in nodes]
    res_ids = [i for i in ids if re.fullmatch(rf"http://rdfh\.ch/{SHORTCODE}/{UUID_RE}", i)]
    val_ids = [i for i in ids if re.fullmatch(rf"{re.escape(iris['a'])}/values/{UUID_RE}", i)]
    assert res_ids == [iris["a"]]
    assert len(val_ids) == 1
    assert len(ids) == NUM_NODES_RES_WITH_ONE_VALUE


def test_link_cycle(tmp_path):
    target, iris = _write([_resource("a", [_link("b")]), _resource("b", [_link("a")])], tmp_path)
    graph = _parse(target)
    link_prop = URIRef(f"{ONTO}hasLinkToValue")
    targets = {
        str(s): {str(o) for _, _, o in graph.triples((v, KNORA_API.linkValueHasTargetIri, None))}
        for s, _, v in graph.triples((None, link_prop, None))
    }
    assert targets == {iris["a"]: {iris["b"]}, iris["b"]: {iris["a"]}}


def test_richtext_standoff_reference(tmp_path):
    richtext = ProcessedRichtext(
        value=FormattedTextValue('<a class="salsah-link" href="IRI:b:IRI">b</a>'),
        prop_iri=f"{ONTO}hasRichtext",
        resource_references={"b"},
        value_uuid="uuid",
        comment=None,
        permissions=None,
        value_order=0,
    )
    target, iris = _write([_resource("a", [richtext]), _resource("b")], tmp_path)
    text = target.read_text(encoding="utf-8")
    assert iris["b"] in text
    assert "IRI:b:IRI" not in text
    assert "hasStandoffLinkTo" not in text


def test_preset_migration_iri_is_kept(tmp_path):
    preset = f"http://rdfh.ch/{SHORTCODE}/{'A' * 22}"
    target, iris = _write([_resource("a", migration_metadata=MigrationMetadata(preset, None))], tmp_path)
    assert iris["a"] == preset
    assert preset in {n["@id"] for n in json.loads(target.read_text(encoding="utf-8"))}


def test_list_value(tmp_path):
    target, _ = _write([_resource("a", [ProcessedList(LIST_NODE_IRI, f"{ONTO}hasList", None, None, 0)])], tmp_path)
    assert URIRef(LIST_NODE_IRI) in set(_parse(target).objects())


def test_bitstream_filename(tmp_path):
    file_value = ProcessedFileValue(
        value=ProcessedFileBitstream(value="internal.jp2", res_id="a"),
        value_type=KnoraFileValueType.STILL_IMAGE_FILE,
        metadata=ProcessedFileMetadata(
            license_iri="http://rdfh.ch/licenses/cc-by-4.0", copyright_holder="h", authorships=["a"]
        ),
    )
    target, _ = _write([_resource("a", file_value=file_value)], tmp_path)
    graph = _parse(target)
    filenames = set(graph.objects(None, KNORA_API.fileValueHasFilename))
    assert {str(f) for f in filenames} == {"internal.jp2"}
    file_node = next(graph.subjects(KNORA_API.fileValueHasFilename, None))
    assert graph.value(file_node, KNORA_API.valueHasOrder) == Literal(0, datatype=XSD.integer)


def test_missing_iri_raises(tmp_path):
    lookups = IRILookups(project_iri=URIRef("http://rdfh.ch/projects/proj"), id_to_iri=IriResolver({}))
    target = tmp_path / "payload.jsonld"
    with pytest.raises(ResourceIriMissingError):
        write_payload_file([_resource("a")], lookups, target)
    assert not target.exists()
    assert not list(tmp_path.glob("*.part"))


def test_failure_leaves_no_file(tmp_path, monkeypatch):
    calls = []

    def _raise_on_second(graph: Graph) -> list[dict[str, Any]]:
        calls.append(graph)
        if len(calls) == FAILING_CALL:
            raise KeyboardInterrupt
        return []

    monkeypatch.setattr(write_payload_module, "serialise_json", _raise_on_second)
    with pytest.raises(KeyboardInterrupt):
        _write([_resource("a"), _resource("b")], tmp_path)
    assert list(tmp_path.iterdir()) == []
