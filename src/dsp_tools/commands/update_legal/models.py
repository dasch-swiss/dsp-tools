from dataclasses import dataclass

from dsp_tools.error.exceptions import InputError, InvalidLicenseError
from dsp_tools.xmllib.general_functions import find_license_in_string
from dsp_tools.xmllib.models.licenses.recommended import License


@dataclass(frozen=True)
class LegalProperties:
    """Property names in the XML, e.g. ':hasAuthor', ':hasCopyright', ':hasLicense'."""

    authorship_prop: str | None = None
    copyright_prop: str | None = None
    license_prop: str | None = None

    def has_any_property(self) -> bool:
        return any([self.authorship_prop, self.copyright_prop, self.license_prop])


@dataclass(frozen=True)
class LegalMetadata:
    """Represents legal metadata for a single resource, either from XML or CSV."""

    license: str | None
    copyright: str | None
    authorships: list[str]


class LegalMetadataDefaults:
    """Default values to use when legal metadata is missing from XML."""

    authorship_default: str | None = None
    copyright_default: str | None = None
    license_default: License | None = None

    def __init__(
        self,
        authorship_default: str | None = None,
        copyright_default: str | None = None,
        license_default: str | None = None,
    ):
        self.authorship_default = authorship_default
        self.copyright_default = copyright_default
        if license_default:
            if lic := find_license_in_string(license_default):
                self.license_default = lic
            else:
                raise InvalidLicenseError(license_default)


@dataclass(frozen=True)
class Problem:
    """Represents a problem with legal metadata for a single resource."""

    file_or_iiif_uri: str
    res_id: str
    license: str
    copyright: str
    authorships: list[str]
