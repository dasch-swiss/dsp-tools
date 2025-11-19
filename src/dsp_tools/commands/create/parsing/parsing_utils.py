from typing import Any

import regex

from dsp_tools.commands.create.constants import KNORA_API_STR
from dsp_tools.commands.create.constants import UNIVERSAL_PREFIXES
from dsp_tools.utils.data_formats.iri_util import make_dsp_ontology_prefix
from dsp_tools.utils.data_formats.uri_util import is_uri


def resolve_to_absolute_iri(prefixed: str, current_onto: str, prefix_lookup: dict[str, str]) -> str | None:
    if is_uri(prefixed):
        return prefixed
    if prefixed.startswith(":"):
        return f"{current_onto}{prefixed.lstrip(':')}"
    segments = prefixed.split(":", maxsplit=1)
    if len(segments) == 1:
        return f"{KNORA_API_STR}{segments[0]}"
    if not (found := prefix_lookup.get(segments[0])):
        return None
    return f"{found}{segments[1]}"


def create_prefix_lookup(project_json: dict[str, Any], api_url: str) -> dict[str, str]:
    defined_prefixes = project_json.get("prefixes", {})
    defined_prefixes = defined_prefixes | UNIVERSAL_PREFIXES
    defined_prefixes = _correct_external_prefix(defined_prefixes)
    shortcode = project_json["project"]["shortcode"]
    for onto in project_json["project"]["ontologies"]:
        onto_name = onto["name"]
        defined_prefixes[onto_name] = make_dsp_ontology_prefix(api_url, shortcode, onto_name)
    return defined_prefixes


def _correct_external_prefix(prefixes: dict[str, str]) -> dict[str, str]:
    for prfx, namespace in prefixes.items():
        if regex.search(r"(#|\/)$", namespace):
            continue
        prefixes[prfx] = f"{namespace}/"
    return prefixes
