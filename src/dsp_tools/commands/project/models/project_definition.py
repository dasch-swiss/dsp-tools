from dataclasses import dataclass


@dataclass
class ProjectDefinition:
    shortcode: str
    shortname: str
    longname: str
    keywords: list[str] | None = None
    descriptions: dict[str, str] | None = None
    groups: list[str] | None = None
    users: list[str] | None = None
