from __future__ import annotations

from dataclasses import dataclass

from rdflib import URIRef

from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.permission import Permissions


@dataclass
class XmlReferenceLookups:
    permissions: dict[str, Permissions]
    listnodes: dict[tuple[str, str], str]
    namespaces: dict[str, str]
    authorships: dict[str, list[str]]


@dataclass
class IRILookups:
    project_iri: URIRef
    id_to_iri: IriResolver


def make_namespace_dict_from_onto_names(ontos: dict[str, str]) -> dict[str, str]:
    """Provided a dictionary of ontology names and IRIs, returns a dictionary of Namespace objects."""
    ontos = _correct_project_context_namespaces(ontos)
    ontos["knora-api"] = "http://api.knora.org/ontology/knora-api/v2#"
    return ontos


def _correct_project_context_namespaces(ontos: dict[str, str]) -> dict[str, str]:
    """Add the hashtag to make it a valid namespace."""
    return {k: f"{v}#" for k, v in ontos.items()}
