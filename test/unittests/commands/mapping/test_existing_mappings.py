import pytest

from dsp_tools.commands.mapping.existing_mappings import get_existing_mappings
from dsp_tools.commands.mapping.existing_mappings import is_deletable_mapping_iri
from dsp_tools.commands.mapping.existing_mappings import select_mappings_to_delete
from dsp_tools.commands.mapping.models import ExistingMappings
from dsp_tools.commands.mapping.models import MappingDeletion
from dsp_tools.commands.mapping.models import MappingDeletions
from dsp_tools.commands.mapping.models import ResolvedClassMapping
from dsp_tools.commands.mapping.models import ResolvedMappings
from dsp_tools.commands.mapping.models import ResolvedPropertyMapping

DSP_SERVER = "http://0.0.0.0:3333"
DSP_SERVER_HOST = "0.0.0.0"  # noqa: S104 (this is the host a local DSP stack is served on, not a bind address)
ONTO_NAMESPACE = "http://0.0.0.0:3333/ontology/0001/testonto/v2#"

CIDOC_E22 = "http://www.cidoc-crm.org/cidoc-crm/E22_Human-Made_Object"
BIBO_BOOK = "http://purl.org/ontology/bibo/Book"
DCTERMS_TITLE = "https://www.dublincore.org/specifications/dublin-core/dcmi-terms/title"

ONTOLOGY_TTL = f"""
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix knora-api: <http://api.knora.org/ontology/knora-api/v2#> .
@prefix onto: <{ONTO_NAMESPACE}> .
@prefix foreign: <http://0.0.0.0:3333/ontology/0001/otheronto/v2#> .

onto:MappedResource a owl:Class ;
    rdfs:subClassOf knora-api:Resource ,
        <{CIDOC_E22}> ,
        <{BIBO_BOOK}> ,
        [ a owl:Restriction ;
            owl:maxCardinality 1 ;
            owl:onProperty onto:hasText ] .

onto:BareResource a owl:Class ;
    rdfs:subClassOf knora-api:Resource .

onto:hasText a owl:ObjectProperty ;
    rdfs:subPropertyOf knora-api:hasValue ,
        <{DCTERMS_TITLE}> .

foreign:ForeignResource a owl:Class ;
    rdfs:subClassOf knora-api:Resource ,
        <http://www.cidoc-crm.org/cidoc-crm/E21_Person> .
"""


class TestIsDeletableMappingIri:
    @pytest.mark.parametrize(
        "iri",
        [
            CIDOC_E22,
            "https://www.w3.org/TR/rdf-schema/Book",
            BIBO_BOOK,
            "http://www.w3.org/ns/prov#Entity",
        ],
    )
    def test_external_iris_are_deletable(self, iri: str):
        assert is_deletable_mapping_iri(iri, DSP_SERVER_HOST)

    @pytest.mark.parametrize(
        "iri",
        [
            "http://api.knora.org/ontology/knora-api/v2#Resource",
            "http://www.knora.org/ontology/knora-base#Resource",
            "http://api.knora.org/ontology/shared/example-box/v2#Box",
            "http://api.dasch.swiss/ontology/0801/biz/v2#Person",
        ],
    )
    def test_dsp_iris_are_not_deletable(self, iri: str):
        assert not is_deletable_mapping_iri(iri, DSP_SERVER_HOST)

    @pytest.mark.parametrize(
        "iri",
        [
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
            "http://www.w3.org/2000/01/rdf-schema#Class",
            "http://www.w3.org/2002/07/owl#Thing",
            "http://www.w3.org/2001/XMLSchema#string",
            "https://www.w3.org/ns/shacl#NodeShape",
            "http://datashapes.org/dash#SingleLineConstraintComponent",
        ],
    )
    def test_technical_rdf_namespaces_are_not_deletable(self, iri: str):
        assert not is_deletable_mapping_iri(iri, DSP_SERVER_HOST)

    @pytest.mark.parametrize(
        "iri",
        [
            "http://0.0.0.0:3333/ontology/0001/testonto/v2#OtherClass",
            "http://0.0.0.0:41235/ontology/0001/testonto/v2#OtherClass",
        ],
    )
    def test_own_server_is_not_deletable_regardless_of_port(self, iri: str):
        assert not is_deletable_mapping_iri(iri, DSP_SERVER_HOST)

    @pytest.mark.parametrize("iri", ["urn:foo:bar", "", "not-an-iri"])
    def test_iris_without_host_are_not_deletable(self, iri: str):
        assert not is_deletable_mapping_iri(iri, DSP_SERVER_HOST)


class TestGetExistingMappings:
    def test_whole_structure(self):
        result = get_existing_mappings(ONTOLOGY_TTL, ONTO_NAMESPACE, DSP_SERVER)
        expected = ExistingMappings(
            classes={f"{ONTO_NAMESPACE}MappedResource": [BIBO_BOOK, CIDOC_E22]},
            properties={f"{ONTO_NAMESPACE}hasText": [DCTERMS_TITLE]},
        )
        assert result == expected


class TestSelectMappingsToDelete:
    def test_stale_mappings_are_selected(self):
        existing = ExistingMappings(classes={f"{ONTO_NAMESPACE}Book": [CIDOC_E22, BIBO_BOOK]}, properties={})
        resolved = ResolvedMappings(
            classes=[ResolvedClassMapping(iri=f"{ONTO_NAMESPACE}Book", mapping_iris=[BIBO_BOOK, DCTERMS_TITLE])],
            properties=[],
        )
        result = select_mappings_to_delete(existing, resolved)
        expected = MappingDeletions(
            classes=[MappingDeletion(entity_iri=f"{ONTO_NAMESPACE}Book", mapping_iri=CIDOC_E22)],
            properties=[],
        )
        assert result == expected

    def test_unchanged_excel_deletes_nothing(self):
        existing = ExistingMappings(classes={f"{ONTO_NAMESPACE}Book": [CIDOC_E22, BIBO_BOOK]}, properties={})
        resolved = ResolvedMappings(
            classes=[ResolvedClassMapping(iri=f"{ONTO_NAMESPACE}Book", mapping_iris=[CIDOC_E22, BIBO_BOOK])],
            properties=[],
        )
        result = select_mappings_to_delete(existing, resolved)
        assert result == MappingDeletions(classes=[], properties=[])

    def test_entity_absent_from_excel_is_wiped(self):
        existing = ExistingMappings(classes={f"{ONTO_NAMESPACE}Unlisted": [CIDOC_E22]}, properties={})
        resolved = ResolvedMappings(classes=[], properties=[])
        result = select_mappings_to_delete(existing, resolved)
        expected = MappingDeletions(
            classes=[MappingDeletion(entity_iri=f"{ONTO_NAMESPACE}Unlisted", mapping_iri=CIDOC_E22)],
            properties=[],
        )
        assert result == expected

    def test_duplicate_excel_rows_are_unioned(self):
        existing = ExistingMappings(classes={f"{ONTO_NAMESPACE}Book": [CIDOC_E22, BIBO_BOOK]}, properties={})
        resolved = ResolvedMappings(
            classes=[
                ResolvedClassMapping(iri=f"{ONTO_NAMESPACE}Book", mapping_iris=[CIDOC_E22]),
                ResolvedClassMapping(iri=f"{ONTO_NAMESPACE}Book", mapping_iris=[BIBO_BOOK]),
            ],
            properties=[],
        )
        result = select_mappings_to_delete(existing, resolved)
        assert result == MappingDeletions(classes=[], properties=[])

    def test_classes_and_properties_are_independent(self):
        existing = ExistingMappings(
            classes={f"{ONTO_NAMESPACE}Book": [CIDOC_E22]},
            properties={f"{ONTO_NAMESPACE}hasText": [DCTERMS_TITLE]},
        )
        resolved = ResolvedMappings(
            classes=[ResolvedClassMapping(iri=f"{ONTO_NAMESPACE}Book", mapping_iris=[CIDOC_E22])],
            properties=[ResolvedPropertyMapping(iri=f"{ONTO_NAMESPACE}hasText", mapping_iris=[BIBO_BOOK])],
        )
        result = select_mappings_to_delete(existing, resolved)
        expected = MappingDeletions(
            classes=[],
            properties=[MappingDeletion(entity_iri=f"{ONTO_NAMESPACE}hasText", mapping_iri=DCTERMS_TITLE)],
        )
        assert result == expected
