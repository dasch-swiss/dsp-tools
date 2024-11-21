from rdflib import Namespace
from rdflib import URIRef

from dsp_tools.commands.xmlupload.models.permission import Permissions
from dsp_tools.models.exceptions import InputError
from dsp_tools.models.exceptions import PermissionNotExistsError


def resolve_permission(permissions: str | None, permissions_lookup: dict[str, Permissions]) -> str | None:
    """Resolve the permission into a string that can be sent to the API."""
    if permissions:
        if not (per := permissions_lookup.get(permissions)):
            raise PermissionNotExistsError(f"Could not find permissions for value: {permissions}")
        return str(per)
    return None


def get_absolute_iri(prefixed_iri: str, namespaces: dict[str, Namespace]) -> URIRef:
    """Get the absolute IRI from a prefixed property or resource."""
    prefix, prop = prefixed_iri.split(":", maxsplit=1)
    if not (namespace := namespaces.get(prefix)):
        raise InputError(f"Could not find namespace for prefix: {prefix}")
    return namespace[prop]
