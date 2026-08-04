from collections.abc import Sequence
from urllib.parse import urlparse

from loguru import logger
from rdflib import RDFS
from rdflib import Graph
from rdflib import URIRef

from dsp_tools.commands.mapping.models import ExistingMappings
from dsp_tools.commands.mapping.models import MappingDeletion
from dsp_tools.commands.mapping.models import MappingDeletions
from dsp_tools.commands.mapping.models import ResolvedMapping
from dsp_tools.commands.mapping.models import ResolvedMappings
from dsp_tools.utils.data_formats.iri_util import is_dsp_project_iri

# An IRI on one of these hosts is never a user mapping: it is knora-api, knora-base, a DSP shared ontology or a
# production project ontology. The DSP-API rejects these as mapping targets, so they can only be super-entities
# that the ontology needs. Always keep them.
MAPPING_HOST_SUBSTRINGS_TO_KEEP = ("knora.org", "dasch.swiss")

# Technical RDF vocabularies. A super-entity in one of these is structural, so it is kept. Note that only the RDF
# Schema *namespace* is listed: a mapping to a document URL such as https://www.w3.org/TR/rdf-schema/Book is a
# legitimate user mapping and stays deletable.
MAPPING_NAMESPACES_TO_KEEP = (
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "http://www.w3.org/2000/01/rdf-schema#",
    "http://www.w3.org/2002/07/owl#",
    "http://www.w3.org/2001/XMLSchema#",
    "https://www.w3.org/ns/shacl#",
    "http://datashapes.org/dash#",
)


def is_deletable_mapping_iri(iri: str, dsp_server_host: str) -> bool:
    """Decide if an IRI is an external mapping that may be deleted, as opposed to a DSP-internal super-entity."""
    host = urlparse(iri).hostname
    if not host:
        # A mapping IRI that is not http(s) cannot be stored through the DSP-API in the first place,
        # and the remaining host checks cannot classify it.
        return False
    if any(substring in host for substring in MAPPING_HOST_SUBSTRINGS_TO_KEEP):
        return False
    if host == dsp_server_host:
        # The DSP-API does not have this rule. It is what protects same-project super-entities on a local
        # or testcontainer stack, where their IRIs are hosted at the DSP server itself.
        return False
    if any(iri.startswith(namespace) for namespace in MAPPING_NAMESPACES_TO_KEEP):
        return False
    return not is_dsp_project_iri(iri)


def get_existing_mappings(ontology_ttl: str, ontology_namespace: str, dsp_server: str) -> ExistingMappings:
    """Find the deletable external mappings of all classes and properties of one ontology."""
    logger.debug("Look for existing external mappings in the ontology on the server.")
    graph = Graph()
    graph.parse(data=ontology_ttl, format="ttl")
    dsp_server_host = urlparse(dsp_server).hostname or ""
    return ExistingMappings(
        classes=_find_deletable_mappings(graph, RDFS.subClassOf, ontology_namespace, dsp_server_host),
        properties=_find_deletable_mappings(graph, RDFS.subPropertyOf, ontology_namespace, dsp_server_host),
    )


def _find_deletable_mappings(
    graph: Graph, predicate: URIRef, ontology_namespace: str, dsp_server_host: str
) -> dict[str, list[str]]:
    # The predicate discriminates classes from properties: a class never carries rdfs:subPropertyOf.
    found: dict[str, list[str]] = {}
    for subject, obj in graph.subject_objects(predicate):
        # Objects that are no URIRef are the owl:Restriction blank nodes of the cardinalities.
        if not isinstance(obj, URIRef) or not str(subject).startswith(ontology_namespace):
            continue
        if is_deletable_mapping_iri(str(obj), dsp_server_host):
            found.setdefault(str(subject), []).append(str(obj))
    return {entity_iri: sorted(mapping_iris) for entity_iri, mapping_iris in sorted(found.items())}


def select_mappings_to_delete(existing: ExistingMappings, resolved: ResolvedMappings) -> MappingDeletions:
    """Determine which of the existing external mappings the Excel file does not ask for any more."""
    return MappingDeletions(
        classes=_select_stale_mappings(existing.classes, resolved.classes),
        properties=_select_stale_mappings(existing.properties, resolved.properties),
    )


def _select_stale_mappings(
    existing: dict[str, list[str]], resolved: Sequence[ResolvedMapping]
) -> list[MappingDeletion]:
    # Several Excel rows may name the same entity, so the desired IRIs of an entity are the union of its rows.
    desired: dict[str, set[str]] = {}
    for mapping in resolved:
        desired.setdefault(mapping.iri, set()).update(mapping.mapping_iris)
    return [
        MappingDeletion(entity_iri=entity_iri, mapping_iri=mapping_iri)
        for entity_iri, mapping_iris in existing.items()
        for mapping_iri in mapping_iris
        if mapping_iri not in desired.get(entity_iri, set())
    ]
