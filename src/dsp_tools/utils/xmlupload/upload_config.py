from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import regex

from dsp_tools.utils.create_logger import get_logger

logger = get_logger(__name__)


def _transform_server_url_to_foldername(server: str) -> str:
    """
    Take the server URL and transform it so that it can be used as foldername.

    Args:
        server: server, e.g. "https://api.test.dasch.swiss/" or "http://0.0.0.0:3333"

    Returns:
        simplified version, e.g. "test.dasch.swiss" or "localhost"
    """
    server_substitutions = {
        r"https?://": "",
        r"^api\.": "",
        r":\d{2,5}/?$": "",
        r"/$": "",
        r"0.0.0.0": "localhost",
    }
    for pattern, repl in server_substitutions.items():
        server = regex.sub(pattern, repl, server)
    return server


@dataclass(frozen=True)
class UploadConfig:
    """Configuration for the upload process."""

    verbose: bool = False
    dump: bool = False
    save_metrics: bool = False
    preprocessing_done: bool = False
    server_as_foldername: str = field(default="unknown")
    save_location: Path = field(default_factory=lambda: Path.home() / Path(".dsp-tools") / "xmluploads")
    timestamp_str: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d_%H%M%S"))

    def with_specific_save_location(
        self,
        server: str,
        shortcode: str,
        onto_name: str,
    ) -> UploadConfig:
        """Create a new UploadConfig with the given server."""
        server_as_foldername = _transform_server_url_to_foldername(server)
        save_location = Path.home() / Path(".dsp-tools") / "xmluploads" / server_as_foldername / shortcode / onto_name
        save_location.mkdir(parents=True, exist_ok=True)
        logger.info(f"save_location='{save_location}'")
        return dataclasses.replace(
            self,
            save_location=save_location,
            server_as_foldername=server_as_foldername,
        )
