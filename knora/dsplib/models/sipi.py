import os
import requests
from typing import Any
from .helpers import BaseError


def on_api_error(res):
    """
    Checks for any API errors

    Args:
        res: the response from the API which is checked, usually in JSON format

    Returns:
        Knora Error that is being raised
    """

    if res.status_code != 200:
        raise BaseError("SIPI-ERROR: status code=" + str(res.status_code) + "\nMessage:" + res.text)

    if 'error' in res:
        raise BaseError("SIPI-ERROR: API error: " + res.error)


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
        with open(filepath, 'rb') as bitstream_file:
            files = {'file': (os.path.basename(filepath), bitstream_file), }
            req = requests.post(self.sipi_server + "/upload?token=" + self.token, files=files)
        on_api_error(req)
        print(f'Uploaded file {filepath}')
        res: dict[Any, Any] = req.json()
        return res
