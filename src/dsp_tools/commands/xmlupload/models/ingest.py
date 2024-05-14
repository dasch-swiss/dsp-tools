from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import requests

from dsp_tools.utils.connection import Connection


@dataclass(frozen=True)
class IngestResponse:
    internal_filename: str


class IngestClient(Protocol):
    def ingest(self, shortcode: str, filepath: Path) -> IngestResponse:
        """
        Ingests a file to the asset repository

        Args:
          shortcode: the shortcode of the project
          filepath: path to the file, could be either absolute or relative

        Returns:
          API response
        """
        ...


@dataclass(frozen=True)
class DspIngestClient(IngestClient):
    dsp_ingest_url: str
    token: str

    def ingest(self, shortcode: str, filepath: Path) -> IngestResponse:
        with open(filepath, "rb") as binary_io:
            url = f"{self.dsp_ingest_url}/projects/{shortcode}/assets/ingest/{filepath.name}"
            res = requests.post(
                url=url,
                headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/octet-stream"},
                data=binary_io,
                timeout=60,
            )
            return IngestResponse(internal_filename=res.json()["internalFilename"])


@dataclass(frozen=True)
class Sipi(IngestClient):
    """
    A wrapper type around a connection to a SIPI server.
    Provides functionality to upload bitstreams files to the SIPI server.
    """

    con: Connection

    def ingest(self, shortcode: str, filepath: Path) -> IngestResponse:  # noqa: ARG002 (Unused method argument)
        with open(filepath, "rb") as binary_io:
            files = {"file": (filepath.name, binary_io)}
            res = self.con.post(route="/upload", files=files)
            return IngestResponse(internal_filename=res["uploadedFiles"][0]["internalFilename"])
