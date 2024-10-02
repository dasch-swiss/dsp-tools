from dataclasses import dataclass


@dataclass
class MigrationMetadata:
    creation_date: str | None
    iri: str | None
    ark: str | None
