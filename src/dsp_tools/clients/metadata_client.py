from dataclasses import dataclass
from enum import Enum
from enum import auto
from typing import Protocol

from dsp_tools.clients.authentication_client import AuthenticationClient


class MetadataRetrieval(Enum):
    SUCCESS = auto()
    FAILURE = auto()


@dataclass
class MetadataClient(Protocol):
    """
    Protocol class/interface for the metadata endpoint in the API.
    """

    server: str
    authentication_client: AuthenticationClient

    def get_resource_metadata(self, shortcode: str) -> tuple[MetadataRetrieval, list[dict[str, str]]]:
        """Get all resource metadata from one project."""
