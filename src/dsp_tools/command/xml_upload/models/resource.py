from dataclasses import dataclass

from dsp_tools.command.xml_upload.models.value import Value


@dataclass(frozen=True)
class InputPermissions:
    """Maps a user group (built-in or custom) to the permission level it has (CR, D, M, V, RV)"""

    permissions: dict[str, str]


@dataclass(frozen=True)
class InputResource:
    """All information of a resource as provided by the XML input."""

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
    """A collection of resources as provided by the XML input."""

    shortcode: str
    default_ontology: str
    resources: list[InputResource]


@dataclass(frozen=True)
class ProcessedResource:
    """All information of a resource after preprocessing."""

    resource_id: str
    resource_type: str
    label: str
    values: list[Value]
    bitstream_info: str | None = None
    permissions: str | None = None
    iri: str | None = None
    ark: str | None = None
    creation_date: str | None = None
    # XXX: stash could be included here?
