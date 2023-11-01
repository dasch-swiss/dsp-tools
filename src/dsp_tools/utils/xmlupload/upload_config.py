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
class DiagnosticsConfig:
    """Configures all diagnostics for a given upload."""

    verbose: bool = False
    dump: bool = False
    server_as_foldername: str = "unknown"
    save_location: Path = field(default=Path.home() / ".dsp-tools" / "xmluploads")
    timestamp_str: str = field(default=datetime.now().strftime("%Y-%m-%d_%H%M%S"))


@dataclass(frozen=True)
class UploadConfig:
    """Configuration for the upload process."""

    preprocessing_done: bool = False
    server: str = "unknown"
    shortcode: str = "unknown"
    diagnostics: DiagnosticsConfig = field(default_factory=DiagnosticsConfig)

    def with_server_info(
        self,
        server: str,
        shortcode: str,
        onto_name: str,
    ) -> UploadConfig:
        """Create a new UploadConfig with the given server."""
        server_as_foldername = _transform_server_url_to_foldername(server)
        save_location = Path.home() / Path(".dsp-tools") / "xmluploads" / server_as_foldername / shortcode / onto_name
        save_location.mkdir(parents=True, exist_ok=True)
        logger.info(f"{save_location=:}")
        diagnostics: DiagnosticsConfig = dataclasses.replace(
            self.diagnostics,
            server_as_foldername=server_as_foldername,
            save_location=save_location,
        )
        return dataclasses.replace(self, server=server, shortcode=shortcode, diagnostics=diagnostics)
