from dataclasses import dataclass
from typing import Protocol


@dataclass
class ProjectInfoClient(Protocol):
    api_url: str

    def get_project_iri(self, shortcode: str) -> str:
        """Get the IRI of a project via shortcode."""
