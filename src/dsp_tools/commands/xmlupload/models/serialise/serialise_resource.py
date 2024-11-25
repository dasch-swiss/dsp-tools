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
    project_iri: str
    migration_metadata: SerialiseMigrationMetadata | None

    def serialise(self) -> dict[str, Any]:
        serialised = self.migration_metadata.serialise() if self.migration_metadata else {}
        serialised.update(self._get_resource_info())
        return serialised

    def _get_resource_info(self) -> dict[str, Any]:
        serialised = {
            "rdfs:label": self.label,
            "@type": self.res_type,
            "knora-api:attachedToProject": {"@id": self.project_iri},
        }
        if self.permissions:
            serialised["knora-api:hasPermissions"] = self.permissions
        return serialised


@dataclass(frozen=True)
class SerialiseMigrationMetadata:
    iri: str | None
    creation_date: DateTimeStamp | None

    def serialise(self) -> dict[str, Any]:
        info: dict[str, Any] = {}
        if self.iri:
            info["@id"] = self.iri
        if self.creation_date:
            info["knora-api:creationDate"] = {
                "@type": "xsd:dateTimeStamp",
                "@value": str(self.creation_date),
            }
        return info
