from dataclasses import dataclass

from dsp_tools.xml_upload.domain.model.value import Value

# TODO: use wrappers where it makes sense


@dataclass(frozen=True)
class Resource:
    resource_id: str
    resource_type: str
    label: str
    values: list[Value]
    bitstream: str | None = None
    permissions: str | None = None
    iri: str | None = None
    ark: str | None = None
    creation_date: str | None = None


@dataclass(frozen=True)
class UploadResourceCollection:
    shortcode: str
    default_ontology: str
    resources: list[Resource]
