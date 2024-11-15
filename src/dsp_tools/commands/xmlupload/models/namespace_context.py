from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rdflib.namespace import Namespace


@dataclass(frozen=True)
class JSONLDContext:
    context: dict[str, Any]

    def serialise(self) -> dict[str, Any]:
        return {"@context": self.context}


def get_json_ld_context_for_project(ontos: dict[str, str]) -> JSONLDContext:
    """Provided a dictionary of ontology names and IRIs, returns a JSON-LD context for the project."""
    context = _get_default_json_ld_context()
    project_context = _correct_project_context_namespaces(ontos)
    context.update(project_context)
    return JSONLDContext(context)


def _get_default_json_ld_context() -> dict[str, str]:
    """
    Returns the JSON-LD context as a dictionary.

    Returns:
        JSON-LD context as a dictionary.
    """
    return {
        "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
        "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
    }


def make_namespace_dict_from_onto_names(ontos: dict[str, str]) -> dict[str, Namespace]:
    """Provided a dictionary of ontology names and IRIs, returns a dictionary of Namespace objects."""
    ontos = _correct_project_context_namespaces(ontos)
    namespaces = {k: Namespace(v) for k, v in ontos.items()}
    namespaces["knora-api"] = Namespace("http://api.knora.org/ontology/knora-api/v2#")
    return namespaces


def _correct_project_context_namespaces(ontos: dict[str, str]) -> dict[str, str]:
    """Add the hashtag to make it a valid namespace."""
    return {k: f"{v}#" for k, v in ontos.items()}
