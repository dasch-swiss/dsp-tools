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
    preprocessing_done: bool = False
    server_as_foldername: str = field(default="unknown")
    save_location: Path = field(default=Path.home() / ".dsp-tools" / "xmluploads")
    timestamp_str: str = field(default=datetime.now().strftime("%Y-%m-%d_%H%M%S"))
    json_ld_context: dict[str, str] = field(
        default_factory=lambda: {
            "knora-api": "http://api.knora.org/ontology/knora-api/v2#",
            "salsah-gui": "http://api.knora.org/ontology/salsah-gui/v2#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        }
    )

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
        logger.info(f"save_location='{save_location}'")
        context_iri = f"{server}/ontology/{shortcode}/{onto_name}/v2#"
        return dataclasses.replace(
            self,
            save_location=save_location,
            server_as_foldername=server_as_foldername,
            json_ld_context=self.json_ld_context | {onto_name: context_iri},
        )
