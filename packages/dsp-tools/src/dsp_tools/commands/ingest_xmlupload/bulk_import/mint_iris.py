import base64
import uuid

from dsp_tools.commands.ingest_xmlupload.exceptions import ForeignShortcodeIriError
from dsp_tools.commands.xmlupload.iri_resolver import IriResolver
from dsp_tools.commands.xmlupload.models.processed.res import ProcessedResource

_RESOURCE_IRI_PREFIX = "http://rdfh.ch/"


def _make_base64_uuid() -> str:
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip("=")


def make_resource_iri(shortcode: str) -> str:
    """Mints a resource IRI of the form `http://rdfh.ch/<SHORTCODE>/<uuid>`, with the shortcode in upper case."""
    return f"{_RESOURCE_IRI_PREFIX}{shortcode.upper()}/{_make_base64_uuid()}"


def make_value_iri(resource_iri: str) -> str:
    """Mints a value IRI of the form `<resource_iri>/values/<uuid>`."""
    return f"{resource_iri}/values/{_make_base64_uuid()}"


def mint_resource_iris(resources: list[ProcessedResource], shortcode: str) -> IriResolver:
    """
    Assigns an IRI to every resource.
    A preset IRI (from the migration metadata) is kept, all others are minted.

    Args:
        resources: the resources of the XML file
        shortcode: the shortcode of the project

    Raises:
        ForeignShortcodeIriError: if the preset IRI of one or more resources belongs to another project

    Returns:
        resolver that maps the resource IDs to their IRIs
    """
    resolver = IriResolver()
    foreign: dict[str, str] = {}
    for res in resources:
        if res.migration_metadata and res.migration_metadata.iri_str:
            iri = res.migration_metadata.iri_str
            if not _has_shortcode(iri, shortcode):
                foreign[res.res_id] = iri
        else:
            iri = make_resource_iri(shortcode)
        resolver.update(res.res_id, iri)
    if foreign:
        raise ForeignShortcodeIriError(shortcode, foreign)
    return resolver


def _has_shortcode(resource_iri: str, shortcode: str) -> bool:
    # dsp-api compares shortcodes case-insensitively, but does not check that a preset IRI belongs to the project.
    if not resource_iri.startswith(_RESOURCE_IRI_PREFIX):
        return False
    iri_shortcode = resource_iri.removeprefix(_RESOURCE_IRI_PREFIX).split("/", maxsplit=1)[0]
    return iri_shortcode.upper() == shortcode.upper()
