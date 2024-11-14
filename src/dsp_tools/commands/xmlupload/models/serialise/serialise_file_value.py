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

    def _get_file_value(self, file_value_type: str) -> dict[str, str]:
        file_value = {
            "@type": f"knora-api:{file_value_type}",
            "knora-api:fileValueHasFilename": self.file_name,
        }
        if self.permissions:
            file_value["knora-api:hasPermissions"] = self.permissions
        return file_value


@dataclass
class SerialiseArchiveFileValue(SerialiseAbstractFileValue):
    def serialise(self) -> dict[str, Any]:
        return {"knora-api:hasArchiveFileValue": self._get_file_value("ArchiveFileValue")}


@dataclass
class SerialiseAudioFileValue(SerialiseAbstractFileValue):
    def serialise(self) -> dict[str, Any]:
        return {"knora-api:hasAudioFileValue": self._get_file_value("AudioFileValue")}


@dataclass
class SerialiseDocumentFileValue(SerialiseAbstractFileValue):
    def serialise(self) -> dict[str, Any]:
        return {"knora-api:hasDocumentFileValue": self._get_file_value("DocumentFileValue")}


@dataclass
class SerialiseMovingImageFileValue(SerialiseAbstractFileValue):
    def serialise(self) -> dict[str, Any]:
        return {"knora-api:hasMovingImageFileValue": self._get_file_value("MovingImageFileValue")}


@dataclass
class SerialiseStillImageFileValue(SerialiseAbstractFileValue):
    def serialise(self) -> dict[str, Any]:
        return {"knora-api:hasStillImageFileValue": self._get_file_value("StillImageFileValue")}


@dataclass
class SerialiseTextFileValue(SerialiseAbstractFileValue):
    def serialise(self) -> dict[str, Any]:
        return {"knora-api:hasTextFileValue": self._get_file_value("")}
