from dataclasses import dataclass


@dataclass(frozen=True)
class UploadResult:
    id_to_iri_mapping: dict[str, str]
    not_uploaded_resources: list[str]
