from dataclasses import dataclass
from typing import Any
from typing import Protocol

from dsp_tools.utils.request_utils import ResponseCodeAndText


@dataclass
class ProjectClient(Protocol):
    server: str

    def get_project_iri(self, shortcode: str) -> str:
        """Get the IRI of a project via shortcode."""

    def post_new_project(self, project_info: dict[str, Any]) -> str | ResponseCodeAndText:
        """Post a new project."""
