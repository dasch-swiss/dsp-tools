from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class SerialiseAbstractFileValue(ABC):
    file_name: str
    permissions: str | None

    @abstractmethod
    def serialise(self) -> dict[str, Any]:
        """Serialise the value."""

    def _get_general_info(self) -> dict[str, str]:
        return {"knora-api:hasPermissions": self.permissions} if self.permissions else {}


@dataclass
class SerialiseArchiveFileValue(SerialiseAbstractFileValue):
    file_name: str
    permissions: str | None

    def serialise(self) -> dict[str, Any]:
        file_value = {
            "@type": "knora-api:ArchiveFileValue",
            "knora-api:fileValueHasFilename": self.file_name,
        }
        file_value.update(self._get_general_info())
        return {"knora-api:hasArchiveFileValue": file_value}


@dataclass
class SerialiseAudioFileValue(SerialiseAbstractFileValue):
    file_name: str
    permissions: str | None

    def serialise(self) -> dict[str, Any]:
        file_value = {
            "@type": "knora-api:AudioFileValue",
            "knora-api:fileValueHasFilename": self.file_name,
        }
        file_value.update(self._get_general_info())
        return {"knora-api:hasAudioFileValue": file_value}


@dataclass
class SerialiseDocumentFileValue(SerialiseAbstractFileValue):
    file_name: str
    permissions: str | None

    def serialise(self) -> dict[str, Any]:
        file_value = {
            "@type": "knora-api:DocumentFileValue",
            "knora-api:fileValueHasFilename": self.file_name,
        }
        file_value.update(self._get_general_info())
        return {"knora-api:hasDocumentFileValue": file_value}


@dataclass
class SerialiseMovingImageFileValue(SerialiseAbstractFileValue):
    file_name: str
    permissions: str | None

    def serialise(self) -> dict[str, Any]:
        file_value = {
            "@type": "knora-api:MovingImageFileValue",
            "knora-api:fileValueHasFilename": self.file_name,
        }
        file_value.update(self._get_general_info())
        return {"knora-api:hasMovingImageFileValue": file_value}


@dataclass
class SerialiseStillImageFileValue(SerialiseAbstractFileValue):
    file_name: str
    permissions: str | None

    def serialise(self) -> dict[str, Any]:
        file_value = {
            "@type": "knora-api:StillImageFileValue",
            "knora-api:fileValueHasFilename": self.file_name,
        }
        file_value.update(self._get_general_info())
        return {"knora-api:hasStillImageFileValue": file_value}


@dataclass
class SerialiseTextFileValue(SerialiseAbstractFileValue):
    file_name: str
    permissions: str | None

    def serialise(self) -> dict[str, Any]:
        file_value = {
            "@type": "knora-api:TextFileValue",
            "knora-api:fileValueHasFilename": self.file_name,
        }
        file_value.update(self._get_general_info())
        return {"knora-api:hasTextFileValue": file_value}
