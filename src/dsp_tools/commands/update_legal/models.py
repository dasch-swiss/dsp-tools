from dataclasses import dataclass


@dataclass(frozen=True)
class LegalProperties:
    """Property names in the XML, e.g. ':hasAuthor', ':hasCopyright', ':hasLicense'."""

    authorship_prop: str | None = None
    copyright_prop: str | None = None
    license_prop: str | None = None

    def has_any_property(self) -> bool:
        return any([self.authorship_prop, self.copyright_prop, self.license_prop])


@dataclass(frozen=True)
class MetadataDefaults:
    """Default values to use when legal metadata is missing from XML."""

    authorship_default: str | None = None
    copyright_default: str | None = None
    license_default: str | None = None


def is_fixme_value(value: str | None) -> bool:
    """Check if a value is a FIXME marker"""
    return value is not None and value.startswith("FIXME:")


@dataclass(frozen=True)
class Problem:
    """
    Represents a problem with legal metadata for a single resource.

    Attributes:
        file: The multimedia file path referenced by the resource
        res_id: The resource ID
        license: The license value or FIXME marker
        copyright: The copyright value or FIXME marker
        authorships: List of authorship values, or FIXME marker in first position
    """

    file: str
    res_id: str
    license: str
    copyright: str
    authorships: list[str]

    def execute_error_protocol(self) -> str:
        """Format problem as human-readable string for console output."""
        parts = [f"Resource ID: {self.res_id}", f"File: {self.file}"]

        if is_fixme_value(self.license):
            parts.append(f"License: {self.license}")
        if is_fixme_value(self.copyright):
            parts.append(f"Copyright: {self.copyright}")
        if self.authorships and is_fixme_value(self.authorships[0]):
            parts.append(f"Authorship: {self.authorships[0]}")

        return " | ".join(parts)


@dataclass(frozen=True)
class LegalMetadata:
    """Represents legal metadata for a single resource, either from XML or CSV."""

    multimedia_filepath: str
    license: str | None
    copyright: str | None
    authorships: list[str]
