from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

import regex
from loguru import logger


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
        r"0.0.0.0": "localhost",  # noqa: S104 (hardcoded-bind-all-interfaces)
    }
    for pattern, repl in server_substitutions.items():
        server = regex.sub(pattern, repl, server)
    return server


@dataclass(frozen=True)
class DiagnosticsConfig:
    """Configures all diagnostics for a given upload."""

    server_as_foldername: str = "unknown"
    save_location: Path = field(default=Path.home() / ".dsp-tools" / "xmluploads")


@dataclass(frozen=True)
class UploadConfig:
    """Configuration for the upload process."""

    media_previously_uploaded: bool = False
    server: str = "unknown"
    shortcode: str = "unknown"
    diagnostics: DiagnosticsConfig = field(default_factory=DiagnosticsConfig)
    interrupt_after: int | None = None
    skip_iiif_validation: bool = False

    def with_server_info(
        self,
        server: str,
        shortcode: str,
    ) -> UploadConfig:
        """Create a new UploadConfig with the given server."""
        server_as_foldername = _transform_server_url_to_foldername(server)
        save_location = Path.home() / Path(".dsp-tools") / "xmluploads" / server_as_foldername / "resumable/latest.pkl"
        save_location.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"{save_location=:}")
        diagnostics: DiagnosticsConfig = dataclasses.replace(
            self.diagnostics,
            server_as_foldername=server_as_foldername,
            save_location=save_location,
        )
        return dataclasses.replace(self, server=server, shortcode=shortcode, diagnostics=diagnostics)
