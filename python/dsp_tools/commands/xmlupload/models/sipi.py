from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dsp_tools.utils.connection import Connection


@dataclass(frozen=True)
class Sipi:
    """
    A wrapper type around a connection to a SIPI server.
    Provides functionality to upload bitstreams files to the SIPI server.
    """

    con: Connection

    def upload_bitstream(self, filepath: Path) -> dict[str, Any]:
        """
        Uploads a bitstream to the Sipi server

        Args:
            filepath: path to the file, could be either absolute or relative

        Returns:
            API response
        """
        with open(filepath, "rb") as bitstream_file:
            files = {"file": (filepath.name, bitstream_file)}
            res = self.con.post(route="/upload", files=files)
            return res
