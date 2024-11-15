from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any
from dsp_tools.models.datetimestamp import DateTimeStamp

@dataclass(frozen=True)
class ProjectContext:
    context: dict[str, Any]
    project_iri: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "knora-api:attachedToProject": {"@id": self.project_iri},
            "@context": self.context,
        }


@dataclass(frozen=True)
class SerialiseAbstractResource(ABC):
    res_id: str
    label: str
    project_context: ProjectContext
    permissions: str | None
    migration_metadata: MigrationMetadata | None

    @abstractmethod
    def serialise_resource(self) -> dict[str, Any]: ...

    def _get_base_info(self) -> dict[str, Any]:
        serialised = self.project_context.to_dict()
        serialised["rdfs:label"] = self.label
        if self.permissions:
            serialised["knora-api:hasPermissions"] = self.permissions
        return serialised


@dataclass(frozen=True)
class SerialiseResource(SerialiseAbstractResource):
    res_type: str

    def serialise_resource(self) -> dict[str, Any]:
        serialised = self.migration_metadata.to_dict() if self.migration_metadata else {}
        serialised.update(self._get_base_info())
        serialised["@type"] = self.res_type
        return serialised


@dataclass(frozen=True)
class MigrationMetadata:
    creation_date: DateTimeStamp | None
    iri: str

    def to_dict(self) -> dict[str, Any]:
        info = {"@id": self.iri}
        if self.creation_date:
            info["knora-api:creationDate"] = {
                "@type": "xsd:dateTimeStamp",
                "@value": str(self.creation_date),
            }
        return info
