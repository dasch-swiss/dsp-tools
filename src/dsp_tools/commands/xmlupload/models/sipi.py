from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dsp_tools.utils.connection import Connection


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

    con: Connection
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
            timeout = 5 * 60
            res = self.con.post(route="/upload", files=files, timeout=timeout)
            return res
