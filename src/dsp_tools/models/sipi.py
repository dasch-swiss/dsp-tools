from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Any

import requests

from dsp_tools.models.connection import check_for_api_error


@dataclass
class Sipi:
    """
    A Sipi instance represents a connection to a SIPI server.

    Attributes:
        sipi_server: address of the server, e.g https://iiif.dasch.swiss
        token: session token received by the server after login
        log: if True, every request is written into a file
        log_directory: directory where the log files are written
    """

    sipi_server: str
    token: str
    log: bool = False
    log_directory: Path = Path("HTTP requests")

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
            route = "/upload"
            headers = {"Authorization": "Bearer " + self.token}
            timeout = 5 * 60
            response = requests.post(
                url=self.sipi_server + route,
                headers=headers,
                files=files,
                timeout=timeout,
            )
            self.write_log_file(
                method="POST",
                route=route,
                headers=headers,
                filepath=filepath,
                timeout=timeout,
                response=response,
            )
        check_for_api_error(response)
        res: dict[Any, Any] = response.json()
        return res

    def start_logging(self) -> None:
        """Start writing every API call to a file"""
        self.log = True
        self.log_directory.mkdir(exist_ok=True)

    def stop_logging(self) -> None:
        """Stop writing every API call to a file"""
        self.log = False

    def write_log_file(
        self,
        method: str,
        route: str,
        headers: dict[str, str],
        filepath: str,
        timeout: int,
        response: requests.Response,
    ) -> None:
        """
        If logging is enabled (self.log == True), write the request and response to a file.

        Args:
            method: HTTP method of the request (GET, POST, PUT, DELETE)
            route: route of SIPI that was called
            headers: headers of the HTTP request
            filepath: path to the file that was uploaded
            timeout: timeout of the HTTP request
            response: response of the server
        """
        if not self.log:
            return
        if response.status_code == 200:
            _return = response.json()
        else:
            _return = {"status": response.status_code, "message": response.text}
        logobj = {
            "SIPI server": self.sipi_server,
            "route": route,
            "method": method,
            "filepath": filepath,
            "timeout": timeout,
            "headers": headers,
            "return-headers": dict(response.headers),
            "return": _return,
        }
        timestamp = datetime.now().strftime("%Y-%m-%d %H.%M.%S.%f")
        filename = f"{timestamp} {method} SIPI {route.replace('/', '_')} {filepath.replace('/', '_')}.json"
        with open(self.log_directory / filename, "w", encoding="utf-8") as f:
            json.dump(logobj, f, indent=4)
