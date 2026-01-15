from dataclasses import dataclass

from dsp_tools.clients.legal_info_client import LegalInfoClient
from dsp_tools.clients.list_client import ListGetClient
from dsp_tools.commands.xmlupload.models.ingest import AssetClient


@dataclass(frozen=True)
class UploadClients:
    """Holds all the clients needed for the upload process."""

    asset_client: AssetClient
    list_client: ListGetClient
    legal_info_client: LegalInfoClient
