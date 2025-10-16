from dsp_tools.commands.create.constants import KNORA_API


def resolve_prefixed_iri(prefixed: str, current_onto: str, prefix_lookup: dict[str, str]) -> str | None:
    if prefixed.startswith(":"):
        return f"{current_onto}{prefixed.lstrip(':')}"
    segments = prefixed.split(":", maxsplit=1)
    if len(segments) == 1:
        return f"{KNORA_API}{segments[0]}"
    if not (found := prefix_lookup.get(segments[1])):
        return None
    return f"{found}{segments}"
