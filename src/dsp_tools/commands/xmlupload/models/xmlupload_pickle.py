from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource
from dsp_tools.commands.xmlupload.stash.stash_models import Stash


@dataclass
class XmlUploadPickle:
    sorted_resources: list[ProcessedResource]
    stash: Stash | None
    shortcode: str


def save_pickle(data: XmlUploadPickle, path: Path) -> None:
    path.write_bytes(pickle.dumps(data))


def load_pickle(path: Path) -> XmlUploadPickle:
    return pickle.loads(path.read_bytes())  # noqa: S301
