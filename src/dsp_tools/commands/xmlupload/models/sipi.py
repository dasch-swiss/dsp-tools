import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from dsp_tools.utils.connection_live import check_for_api_error


@dataclass(frozen=True)
class Sipi:
    """
    A Sipi instance represents a connection to a SIPI server.

    Attributes:
        sipi_server: address of the server, e.g https://iiif.dasch.swiss
        token: session token received by the server after login
        dump: if True, every request is written into a file
        dump_directory: directory where the HTTP requests are written
    """

    sipi_server: str
    token: str
    dump: bool = False
    dump_directory = Path("HTTP requests")

    def __post_init__(self) -> None:
        """
        Create dumping directory (if applicable)
        """
        if self.dump:
            self.dump_directory.mkdir(exist_ok=True)

    def upload_bitstream(self, filepath: str) -> dict[Any, Any]:
        """
        Uploads a bitstream to the Sipi server

        Args:
            filepath: path to the file, could be either absolute or relative

        Returns:
            API response
        """
        with open(filepath, "rb") as bitstream_file:
            files = {"file": (Path(filepath).name, bitstream_file)}
            url = self.sipi_server + "/upload"
            headers = {"Authorization": "Bearer " + self.token}
            timeout = 5 * 60
            response = requests.post(
                url=url,
                headers=headers,
                files=files,
                timeout=timeout,
            )
            if self.dump:
                self.write_request_to_file(
                    method="POST",
                    url=url,
                    headers=headers,
                    filepath=filepath,
                    timeout=timeout,
                    response=response,
                )
        check_for_api_error(response)
        res: dict[Any, Any] = response.json()
        return res

    def write_request_to_file(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        filepath: str,
        timeout: int,
        response: requests.Response,
    ) -> None:
        """
        Write the request and response to a file.

        Args:
            method: HTTP method of the request (GET, POST, PUT, DELETE)
            url: complete URL (server + route of SIPI) that was called
            headers: headers of the HTTP request
            filepath: path to the file that was uploaded
            timeout: timeout of the HTTP request
            response: response of the server
        """
        if response.status_code == 200:
            _return = response.json()
        else:
            _return = {"status": response.status_code, "message": response.text}
        dumpobj = {
            "SIPI server": self.sipi_server,
            "url": url,
            "method": method,
            "filepath": filepath,
            "timeout": timeout,
            "headers": headers,
            "return-headers": dict(response.headers),
            "return": _return,
        }
        timestamp = datetime.now().strftime("%Y-%m-%d %H.%M.%S.%f")
        route_for_filename = url.replace(self.sipi_server, "").replace("/", "_")
        filename = f"{timestamp} {method} SIPI {route_for_filename} {filepath.replace('/', '_')}.json"
        with open(self.dump_directory / filename, "w", encoding="utf-8") as f:
            json.dump(dumpobj, f, indent=4)
