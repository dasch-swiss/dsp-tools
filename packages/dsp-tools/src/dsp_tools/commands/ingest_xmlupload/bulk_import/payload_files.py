import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class PayloadFiles:
    """The files of one bulk data import, all in the same folder."""

    payload: Path
    id2iri: Path
    error: Path


def data_imports_folder(server_as_foldername: str) -> Path:
    """Returns the folder of the data imports of a server, and creates it if it is missing."""
    folder = Path.home() / ".dsp-tools" / "data-imports" / server_as_foldername
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def make_payload_files(server_as_foldername: str, shortcode: str) -> PayloadFiles:
    """Creates the folder of the data imports of a server and returns the file paths for a new import."""
    folder = data_imports_folder(server_as_foldername)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    payload = folder / f"{shortcode}_{timestamp}.jsonld"
    return PayloadFiles(
        payload=payload,
        id2iri=payload.with_name(f"{payload.stem}_id2iri.json"),
        error=payload.with_name(f"{payload.stem}_error.txt"),
    )


def write_minted_mapping(id2iri: dict[str, str], target: Path) -> None:
    """Writes the mapping of internal IDs to the minted IRIs."""
    target.write_text(json.dumps(id2iri, ensure_ascii=False, indent=4), encoding="utf-8")


def delete_payload_files(files: PayloadFiles) -> None:
    """Deletes the payload file and the minted mapping of an import."""
    files.payload.unlink(missing_ok=True)
    files.id2iri.unlink(missing_ok=True)
