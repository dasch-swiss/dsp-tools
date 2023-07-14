# pylint: disable=too-few-public-methods

import os
from typing import Any

import requests

from dsp_tools.models.connection import check_for_api_error


class Sipi:
    """Represents the Sipi instance"""

    def __init__(self, sipi_server: str, token: str):
        self.sipi_server = sipi_server
        self.token = token

    def upload_bitstream(self, filepath: str) -> dict[Any, Any]:
        """
        Uploads a bitstream to the Sipi server

        Args:
            filepath: path to the file, could be either absolute or relative

        Returns:
            API response
        """
        with open(filepath, "rb") as bitstream_file:
            files = {
                "file": (os.path.basename(filepath), bitstream_file),
            }
            response = requests.post(
                self.sipi_server + "/upload",
                headers={"Authorization": "Bearer " + self.token},
                files=files,
                timeout=5 * 60,
            )
        check_for_api_error(response)
        res: dict[Any, Any] = response.json()
        return res
