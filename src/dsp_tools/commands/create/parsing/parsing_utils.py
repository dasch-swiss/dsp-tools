from dsp_tools.commands.create.constants import KNORA_API
from dsp_tools.utils.data_formats.uri_util import is_uri


def resolve_prefixed_iri(prefixed: str, current_onto: str, prefix_lookup: dict[str, str]) -> str | None:
    if is_uri(prefixed):
        return prefixed
    if prefixed.startswith(":"):
        return f"{current_onto}{prefixed.lstrip(':')}"
    segments = prefixed.split(":", maxsplit=1)
    if len(segments) == 1:
        return f"{KNORA_API}{segments[0]}"
    if not (found := prefix_lookup.get(segments[0])):
        return None
    return f"{found}{segments[1]}"
