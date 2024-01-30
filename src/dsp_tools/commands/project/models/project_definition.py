from dataclasses import dataclass


@dataclass
class ProjectDefinition:
    shortcode: str
    shortname: str
    longname: str
    keywords: str | None = None
    descriptions: list[str] | None = None
    groups: list[str] | None = None
    users: list[str] | None = None
