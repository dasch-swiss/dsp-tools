"""Configuration dataclasses and helper functions for legal metadata updates."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MetadataPropertyConfig:
    """
    Configuration for property names used to extract legal metadata from XML.

    Attributes:
        authorship_prop: Property name for authorship (e.g., ':hasAuthor')
        copyright_prop: Property name for copyright (e.g., ':hasCopyright')
        license_prop: Property name for license (e.g., ':hasLicense')
    """

    authorship_prop: str | None = None
    copyright_prop: str | None = None
    license_prop: str | None = None

    def has_any_property(self) -> bool:
        """Check if at least one property is configured."""
        return any([self.authorship_prop, self.copyright_prop, self.license_prop])


@dataclass(frozen=True)
class MetadataDefaults:
    """
    Default values to use when legal metadata is missing from XML.

    Attributes:
        authorship_default: Default authorship value when missing
        copyright_default: Default copyright value when missing
        license_default: Default license value when missing
    """

    authorship_default: str | None = None
    copyright_default: str | None = None
    license_default: str | None = None


def is_fixme_value(value: str | None) -> bool:
    """
    Check if a value is a FIXME marker.

    Args:
        value: The value to check

    Returns:
        True if value starts with "FIXME:", False otherwise
    """
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
    """
    Represents legal metadata for a single resource, either from XML or CSV.

    Attributes:
        file: The multimedia file path
        license: The license value (or None if missing)
        copyright: The copyright holder (or None if missing)
        authorships: List of authorship values (empty list if missing)
    """

    file: str
    license: str | None
    copyright: str | None
    authorships: list[str]
