from dataclasses import dataclass


@dataclass
class ProjectDefinition:
    shortcode: str
    shortname: str
    longname: str
    keywords: list[str] | None = None
    descriptions: dict[str, str] | None = None
    groups: list[dict[str, str]] | None = None
    users: list[dict[str, str]] | None = None
