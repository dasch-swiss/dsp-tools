from dataclasses import dataclass

from dsp_tools.xml_upload.domain.model.value import Value

# TODO: use wrappers where it makes sense


@dataclass(frozen=True)
class InputPermissions:
    """Maps a user group (built-in or custom) to the permission level it has (CR, D, M, V, RV)"""

    permissions: dict[str, str]


@dataclass(frozen=True)
class InputResource:
    resource_id: str
    resource_type: str
    label: str
    values: list[Value]
    bitstream_path: str | None = None
    permissions: InputPermissions | None = None
    iri: str | None = None
    ark: str | None = None
    creation_date: str | None = None


@dataclass(frozen=True)
class InputResourceCollection:
    shortcode: str
    default_ontology: str
    resources: list[InputResource]


@dataclass(frozen=True)
class ProcessedResource:
    resource_id: str
    resource_type: str
    label: str
    values: list[Value]
    bitstream_info: str | None = None
    permissions: str | None = None
    iri: str | None = None
    ark: str | None = None
    creation_date: str | None = None
