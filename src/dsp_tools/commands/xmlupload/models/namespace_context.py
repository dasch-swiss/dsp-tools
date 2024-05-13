from dataclasses import dataclass
from dataclasses import field

from rdflib import Graph
from rdflib.namespace import Namespace
from rdflib.namespace import NamespaceManager


@dataclass
class NamespaceContext:
    onto_dict: dict[str, Namespace]
    knora_api: Namespace = field(default=Namespace("http://api.knora.org/ontology/knora-api/v2#"))
    salsah_gui: Namespace = field(default=Namespace("http://api.knora.org/ontology/salsah-gui/v2#"))

    def get_json_ld(self) -> dict[str, str]:
        context = self._get_default_json_ld_context()
        context.update({prefix: str(namespace) for prefix, namespace in self.onto_dict.items()})
        return context

    def _get_default_json_ld_context(self) -> dict[str, str]:
        return {
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        }

    def bind_namespace_prefixes_to_graph(self, graph: Graph) -> Graph:
        project_ns = NamespaceManager(graph)
        project_ns.bind("knora-api", self.knora_api)
        project_ns.bind("salsah-gui", self.salsah_gui)
        for prefix, uri in self.onto_dict.items():
            project_ns.bind(prefix, uri)
        return project_ns.graph


def get_json_ld_context_for_project(ontos: dict[str, str]) -> dict[str, str]:
    """Provided a dictionary of ontology names and IRIs, returns a JSON-LD context for the project."""
    project_context = NamespaceContext({k: Namespace(f"{v}#") for k, v in ontos.items()})
    return project_context.get_json_ld()
