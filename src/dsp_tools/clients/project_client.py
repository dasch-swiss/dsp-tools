from typing import Any
from typing import Protocol
from dataclasses import dataclass
from rdflib import Literal

from dsp_tools.clients.authentication_client import AuthenticationClient


@dataclass
class ProjectInfoClient(Protocol):
    api_url: str

    def get_project_iri(self, shortcode: str) -> str | None:
        """Get the IRI of a project via shortcode."""


