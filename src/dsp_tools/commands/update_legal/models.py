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


@dataclass(frozen=True)
class Problem:
    """Represents a problem with legal metadata for a single resource."""

    file_or_iiif_uri: str
    res_id: str
    license: str
    copyright: str
    authorships: list[str]


@dataclass(frozen=True)
class LegalMetadata:
    """Represents legal metadata for a single resource, either from XML or CSV."""

    multimedia_filepath: str
    license: str | None
    copyright: str | None
    authorships: list[str]
