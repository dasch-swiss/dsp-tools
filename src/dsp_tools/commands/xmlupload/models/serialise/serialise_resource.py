from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dsp_tools.models.datetimestamp import DateTimeStamp


@dataclass(frozen=True)
class SerialiseResource:
    res_id: str
    res_type: str
    label: str
    permissions: str | None
    migration_metadata: MigrationMetadata | None

    def serialise(self) -> dict[str, Any]:
        serialised = self.migration_metadata.to_dict() if self.migration_metadata else {}
        serialised.update(self._get_resource_info())
        return serialised

    def _get_resource_info(self) -> dict[str, Any]:
        serialised = {"rdfs:label": self.label, "@type": self.res_type}
        if self.permissions:
            serialised["knora-api:hasPermissions"] = self.permissions
        return serialised


@dataclass(frozen=True)
class ProjectContext:
    context: dict[str, Any]
    project_iri: str

    def serialise(self) -> dict[str, Any]:
        return {
            "knora-api:attachedToProject": {"@id": self.project_iri},
            "@context": self.context,
        }


@dataclass(frozen=True)
class MigrationMetadata:
    iri: str
    creation_date: DateTimeStamp | None

    def to_dict(self) -> dict[str, Any]:
        info: dict[str, Any] = {"@id": self.iri}
        if self.creation_date:
            info["knora-api:creationDate"] = {
                "@type": "xsd:dateTimeStamp",
                "@value": str(self.creation_date),
            }
        return info
