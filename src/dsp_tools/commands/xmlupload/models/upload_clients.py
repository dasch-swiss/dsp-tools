from dataclasses import dataclass

from dsp_tools.clients.ingest import AssetClient
from dsp_tools.clients.legal_info_client import LegalInfoClient
from dsp_tools.clients.list_client import ListGetClient


@dataclass(frozen=True)
class UploadClients:
    """Holds all the clients needed for the upload process."""

    asset_client: AssetClient
    list_client: ListGetClient
    legal_info_client: LegalInfoClient
