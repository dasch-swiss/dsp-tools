import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class PayloadFiles:
    """The files of one bulk data import, all in the same folder."""

    payload: Path
    id2iri: Path


def get_or_create_data_imports_folder(server_as_foldername: str) -> Path:
    """Returns the folder of the data imports of a server, and creates it if it is missing."""
    folder = Path.home() / ".dsp-tools" / "data-imports" / server_as_foldername
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def make_payload_files(server_as_foldername: str, shortcode: str) -> PayloadFiles:
    """Creates the folder of the data imports of a server and returns the file paths for a new import."""
    folder = get_or_create_data_imports_folder(server_as_foldername)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    base = f"{shortcode}_{timestamp}"
    return PayloadFiles(
        payload=folder / f"{base}_payload.jsonld",
        id2iri=folder / f"{base}_id2iri.json",
    )


def error_file(folder: Path, shortcode: str, import_id: str) -> Path:
    """Returns the path of the file for the error message of a failed bulk data import."""
    return folder / f"{shortcode}_{import_id}_error.txt"


def write_minted_mapping(id2iri: dict[str, str], target: Path) -> None:
    """Writes the mapping of internal IDs to the minted IRIs."""
    target.write_text(json.dumps(id2iri, ensure_ascii=False, indent=4), encoding="utf-8")


def delete_payload_files(files: PayloadFiles) -> None:
    """Deletes the payload file and the minted mapping of an import."""
    files.payload.unlink(missing_ok=True)
    files.id2iri.unlink(missing_ok=True)
