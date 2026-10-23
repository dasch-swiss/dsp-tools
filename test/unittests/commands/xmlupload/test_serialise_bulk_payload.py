import dataclasses
import json
import re
from pathlib import Path

from rdflib import RDF
from rdflib import BNode
from rdflib import Graph
from rdflib import Literal
from rdflib import URIRef

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.lookup_models import XmlReferenceLookups
from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileBitstream
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileIIIFUri
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileMetadata
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFilePlaceholder
from dsp_tools.commands.xmlupload.models.processed.file_values import ProcessedFileValue
from dsp_tools.commands.xmlupload.models.processed.res import MigrationMetadata
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedGeolocation
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedGeometry
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedLink
from dsp_tools.commands.xmlupload.models.processed.values import ProcessedSimpleText
from dsp_tools.commands.xmlupload.serialise_bulk_payload import LenientIriResolver
from dsp_tools.commands.xmlupload.serialise_bulk_payload import make_lookups_lenient
from dsp_tools.commands.xmlupload.serialise_bulk_payload import mint_resource_iris
from dsp_tools.commands.xmlupload.serialise_bulk_payload import process_resources_lenient
from dsp_tools.commands.xmlupload.serialise_bulk_payload import replace_blank_nodes
from dsp_tools.commands.xmlupload.serialise_bulk_payload import serialise_resources
from dsp_tools.commands.xmlupload.serialise_bulk_payload import write_json_array
from dsp_tools.utils.rdf_constants import KNORA_API
from dsp_tools.utils.rdf_constants import URN_DASCH_PLACEHOLDER
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraFileValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import KnoraValueType
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileBitstream
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValue
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedFileValueMetadata
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedGeolocation
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedResource
from dsp_tools.utils.xml_parsing.models.parsed_resource import ParsedValue

SHORTCODE = "9999"
PROJECT_IRI = URIRef("http://rdfh.ch/projects/yTerZGyxjZVqFMNNKXCDPF")
ONTO = "http://0.0.0.0:3333/ontology/9999/onto/v2#"
MINTED_RESOURCE_IRI = re.compile(r"^http://rdfh\.ch/9999/[A-Za-z0-9_-]{22}$")


def _resource(res_id: str, values: list | None = None, iri: str | None = None) -> ProcessedResource:  # type: ignore[type-arg]
    migration = MigrationMetadata(iri, None) if iri else None
    return ProcessedResource(
        res_id=res_id,
        type_iri=f"{ONTO}Thing",
        label=res_id,
        permissions=None,
        values=values or [],
        migration_metadata=migration,
    )


def _link(target: str) -> ProcessedLink:
    return ProcessedLink(
        value=target, prop_iri=f"{ONTO}hasLink", comment=None, permissions=None, value_order=0, value_uuid="u"
    )


def _text() -> ProcessedSimpleText:
    return ProcessedSimpleText(value="text", prop_iri=f"{ONTO}hasText", comment=None, permissions=None, value_order=0)


class TestMintResourceIris:
    def test_mints_iri(self) -> None:
        resources, resolver = mint_resource_iris([_resource("a")], SHORTCODE)
        minted = resources[0].migration_metadata
        assert minted is not None
        assert minted.iri_str is not None
        assert MINTED_RESOURCE_IRI.match(minted.iri_str)
        assert resolver.get("a") == minted.iri_str

    def test_keeps_preset_iri(self) -> None:
        resources, resolver = mint_resource_iris([_resource("a", iri="http://rdfh.ch/9999/preset")], SHORTCODE)
        assert resources[0].migration_metadata == MigrationMetadata("http://rdfh.ch/9999/preset", None)
        assert resolver.get("a") == "http://rdfh.ch/9999/preset"

    def test_iris_are_unique(self) -> None:
        _, resolver = mint_resource_iris([_resource("a"), _resource("b")], SHORTCODE)
        assert resolver.get("a") != resolver.get("b")


class TestLenientIriResolver:
    def test_known_id(self) -> None:
        resolver = LenientIriResolver(lookup={"a": "http://rdfh.ch/9999/a"}, shortcode=SHORTCODE)
        assert resolver.get("a") == "http://rdfh.ch/9999/a"

    def test_unknown_id_gets_a_stable_minted_iri(self) -> None:
        resolver = LenientIriResolver(lookup={}, shortcode=SHORTCODE)
        first = resolver.get("missing")
        assert first is not None
        assert MINTED_RESOURCE_IRI.match(first)
        assert resolver.get("missing") == first


class TestMakeLookupsLenient:
    def _lookups(self) -> XmlReferenceLookups:
        return XmlReferenceLookups(
            permissions={"public": Permissions()},
            listnodes={("list", "node"): "http://rdfh.ch/lists/9999/node"},
            authorships={"auth": ["Author"]},
        )

    def _parsed(self) -> ParsedResource:
        values = [
            ParsedValue(f"{ONTO}hasList", ("list", "node"), KnoraValueType.LIST_VALUE, "unknown", None, None, 0),
            ParsedValue(f"{ONTO}hasList", ("list", "missing"), KnoraValueType.LIST_VALUE, "public", None, None, 1),
        ]
        metadata = ParsedFileValueMetadata(None, None, "unknown_auth", "unknown")
        file_value = ParsedFileValue(ParsedFileBitstream("file.jpg"), None, metadata)
        return ParsedResource("a", f"{ONTO}Thing", "a", "unknown", values, file_value, None, "unknown_auth")

    def test_unknown_list_node_gets_placeholder_iri(self) -> None:
        _, lookups = make_lookups_lenient([self._parsed()], self._lookups(), SHORTCODE)
        assert lookups.listnodes[("list", "node")] == "http://rdfh.ch/lists/9999/node"
        assert lookups.listnodes[("list", "missing")] == "http://rdfh.ch/lists/9999/missing-list-missing"

    def test_unknown_permissions_are_removed(self) -> None:
        resources, _ = make_lookups_lenient([self._parsed()], self._lookups(), SHORTCODE)
        res = resources[0]
        assert res.permissions_id is None
        assert [x.permissions_id for x in res.values] == [None, "public"]
        assert res.file_value is not None
        assert res.file_value.metadata.permissions_id is None

    def test_unknown_authorship_gets_placeholder(self) -> None:
        _, lookups = make_lookups_lenient([self._parsed()], self._lookups(), SHORTCODE)
        assert lookups.authorships["unknown_auth"] == ["unknown_auth"]
        assert lookups.authorships["auth"] == ["Author"]


def test_replace_blank_nodes() -> None:
    res = URIRef("http://rdfh.ch/9999/res")
    val = BNode()
    graph = Graph()
    graph.add((res, RDF.type, URIRef(f"{ONTO}Thing")))
    graph.add((res, URIRef(f"{ONTO}hasText"), val))
    graph.add((val, KNORA_API.valueAsString, Literal("x")))
    replaced = replace_blank_nodes(graph, res)
    assert len(replaced) == len(graph)
    assert not [x for x in replaced.all_nodes() if isinstance(x, BNode)]
    value_iri = replaced.value(res, URIRef(f"{ONTO}hasText"))
    assert str(value_iri).startswith("http://rdfh.ch/9999/res/values/")


class TestSerialiseResources:
    def test_link_target_resolves_to_minted_iri(self) -> None:
        resources = [_resource("source", [_link("target")]), _resource("target", [_text()])]
        nodes = list(serialise_resources(resources, PROJECT_IRI, SHORTCODE, lenient=False))
        target_iri = next(x["@id"] for x in nodes if x.get("@type") == [f"{ONTO}Thing"] and _label(x) == "target")
        link_targets = [x[str(KNORA_API.linkValueHasTargetIri)][0]["@id"] for x in nodes if _is_link_value(x)]
        assert link_targets == [target_iri]

    def test_no_blank_nodes(self) -> None:
        resources = [_resource("source", [_link("target")]), _resource("target", [_text()])]
        nodes = list(serialise_resources(resources, PROJECT_IRI, SHORTCODE, lenient=False))
        assert all(not x["@id"].startswith("_:") for x in nodes)

    def test_value_has_order(self) -> None:
        nodes = list(serialise_resources([_resource("a", [_text()])], PROJECT_IRI, SHORTCODE, lenient=False))
        value = next(x for x in nodes if x.get("@type") == [str(KNORA_API.TextValue)])
        assert value[str(KNORA_API.valueHasOrder)] == [
            {"@type": "http://www.w3.org/2001/XMLSchema#integer", "@value": 0}
        ]

    def test_lenient_mints_dangling_link_target(self) -> None:
        nodes = list(serialise_resources([_resource("source", [_link("dangling")])], PROJECT_IRI, SHORTCODE, True))
        link_targets = [x[str(KNORA_API.linkValueHasTargetIri)][0]["@id"] for x in nodes if _is_link_value(x)]
        assert len(link_targets) == 1
        assert MINTED_RESOURCE_IRI.match(link_targets[0])


def _label(node: dict) -> str:  # type: ignore[type-arg]
    label: str = node["http://www.w3.org/2000/01/rdf-schema#label"][0]["@value"]
    return label


def _is_link_value(node: dict) -> bool:  # type: ignore[type-arg]
    return node.get("@type") == [str(KNORA_API.LinkValue)]


def test_write_json_array(tmp_path: Path) -> None:
    out = tmp_path / "out.jsonld"
    write_json_array(iter([{"@id": "a"}, {"@id": "b"}]), out)
    assert json.loads(out.read_text(encoding="utf-8")) == [{"@id": "a"}, {"@id": "b"}]


def test_write_empty_json_array(tmp_path: Path) -> None:
    out = tmp_path / "out.jsonld"
    write_json_array(iter([]), out)
    assert json.loads(out.read_text(encoding="utf-8")) == []


def test_lenient_resolver_is_an_iri_resolver() -> None:
    assert isinstance(LenientIriResolver(lookup={}, shortcode=SHORTCODE), IriResolver)


class TestProcessResourcesLenient:
    def _lookups(self) -> XmlReferenceLookups:
        return XmlReferenceLookups(permissions={}, listnodes={}, authorships={})

    def _resource(self, values: list[ParsedValue]) -> ParsedResource:
        return ParsedResource("a", f"{ONTO}Thing", "a", None, values, None, None)

    def _value(self, value: object, value_type: KnoraValueType, order: int = 0) -> ParsedValue:
        return ParsedValue(f"{ONTO}prop", value, value_type, None, None, None, order)  # type: ignore[arg-type]

    def test_valid_values_are_processed_as_usual(self) -> None:
        res = self._resource([self._value("text", KnoraValueType.SIMPLETEXT_VALUE)])
        processed = process_resources_lenient([res], self._lookups())
        assert processed[0].values == [ProcessedSimpleText("text", f"{ONTO}prop", None, None, 0)]

    def test_geolocation_out_of_range_is_kept_raw(self) -> None:
        geo = ParsedGeolocation("CRS84", {"longitude": "8", "latitude": "91"})
        res = self._resource([self._value(geo, KnoraValueType.GEOLOCATION_VALUE)])
        value = process_resources_lenient([res], self._lookups())[0].values[0]
        assert isinstance(value, ProcessedGeolocation)
        assert value.value == "<http://www.opengis.net/def/crs/OGC/1.3/CRS84> POINT(8 91)"

    def test_geolocation_with_wrong_ordinates_is_kept_raw(self) -> None:
        geo = ParsedGeolocation("LV95", {"longitude": "8", "latitude": "47"})
        res = self._resource([self._value(geo, KnoraValueType.GEOLOCATION_VALUE)])
        value = process_resources_lenient([res], self._lookups())[0].values[0]
        assert isinstance(value, ProcessedGeolocation)
        assert value.value == "LV95 longitude=8 latitude=47"

    def test_invalid_geometry_is_kept_raw(self) -> None:
        res = self._resource([self._value("{ not json }", KnoraValueType.GEOM_VALUE)])
        value = process_resources_lenient([res], self._lookups())[0].values[0]
        assert value == ProcessedGeometry("{ not json }", f"{ONTO}prop", None, None, 0)

    def test_empty_text_becomes_empty_string(self) -> None:
        values = [self._value(None, KnoraValueType.RICHTEXT_VALUE), self._value("", KnoraValueType.SIMPLETEXT_VALUE, 1)]
        processed = process_resources_lenient([self._resource(values)], self._lookups())[0]
        assert processed.values == [
            ProcessedSimpleText("", f"{ONTO}prop", None, None, 0),
            ProcessedSimpleText("", f"{ONTO}prop", None, None, 1),
        ]


def test_lenient_file_value_of_unknown_type() -> None:
    metadata = ProcessedFileMetadata("http://rdfh.ch/licenses/cc-by-4.0", "Holder", ["Author"])
    file_value = ProcessedFileValue(ProcessedFileBitstream("file.unknown", "a"), None, metadata)  # type: ignore[arg-type]
    res = dataclasses.replace(_resource("a"), file_value=file_value)
    nodes = list(serialise_resources([res], PROJECT_IRI, SHORTCODE, lenient=True))
    file_node = next(x for x in nodes if x.get("@type") == [str(KNORA_API.FileValue)])
    assert file_node[str(KNORA_API.fileValueHasFilename)][0]["@value"] == "file.unknown"
    res_node = next(x for x in nodes if x.get("@type") == [f"{ONTO}Thing"])
    assert res_node[str(KNORA_API.hasFileValue)] == [{"@id": file_node["@id"]}]


class TestSkipIngestedFiles:
    def _with_file(self, value: object, value_type: KnoraFileValueType | None) -> ProcessedResource:
        metadata = ProcessedFileMetadata("http://rdfh.ch/licenses/cc-by-4.0", "Holder", ["Author"])
        file_value = ProcessedFileValue(value, value_type, metadata)  # type: ignore[arg-type]
        return dataclasses.replace(_resource("a"), file_value=file_value)

    def _file_nodes(self, res: ProcessedResource) -> list[dict]:  # type: ignore[type-arg]
        nodes = serialise_resources([res], PROJECT_IRI, SHORTCODE, lenient=True, skip_ingested_files=True)
        return [x for x in nodes if "/values/" in x["@id"]]

    def test_bitstream_is_dropped(self) -> None:
        res = self._with_file(ProcessedFileBitstream("file.jpg", "a"), KnoraFileValueType.STILL_IMAGE_FILE)
        assert self._file_nodes(res) == []

    def test_unknown_file_type_is_dropped(self) -> None:
        assert self._file_nodes(self._with_file(ProcessedFileBitstream("file.unknown", "a"), None)) == []

    def test_placeholder_is_dropped(self) -> None:
        res = self._with_file(ProcessedFilePlaceholder(), KnoraFileValueType.STILL_IMAGE_FILE)
        assert self._file_nodes(res) == []

    def test_iiif_uri_is_kept(self) -> None:
        uri = "https://iiif.example.org/a.jp2/full/max/0/default.jpg"
        res = self._with_file(ProcessedFileIIIFUri(uri), KnoraFileValueType.STILL_IMAGE_IIIF)
        assert len(self._file_nodes(res)) == 1


def test_lenient_omits_placeholder_legal_info() -> None:
    metadata = ProcessedFileMetadata(URN_DASCH_PLACEHOLDER, URN_DASCH_PLACEHOLDER, [URN_DASCH_PLACEHOLDER])
    uri = ProcessedFileIIIFUri("https://iiif.example.org/a.jp2/full/max/0/default.jpg")
    file_value = ProcessedFileValue(uri, KnoraFileValueType.STILL_IMAGE_IIIF, metadata)
    res = dataclasses.replace(_resource("a"), file_value=file_value)
    nodes = list(serialise_resources([res], PROJECT_IRI, SHORTCODE, lenient=True))
    assert URN_DASCH_PLACEHOLDER not in json.dumps(nodes)


def test_skip_resource_ids() -> None:
    resources = [_resource("keep"), _resource("skip")]
    nodes = list(serialise_resources(resources, PROJECT_IRI, SHORTCODE, False, skip_resource_ids={"skip"}))
    assert [_label(x) for x in nodes] == ["keep"]
