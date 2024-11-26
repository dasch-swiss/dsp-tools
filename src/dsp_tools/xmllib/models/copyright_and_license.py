from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass
class CopyritghtAndLicense:
    copyright_attribution: list[CopyrightAttribution] = field(default_factory=list)
    license: list[License] = field(default_factory=list)

    @staticmethod
    def create_new() -> CopyritghtAndLicense:
        """
        Creates a new copyright attribution and license container.
        New copyright attributions and licenses can be added.

        The following licenses are included by default:
        The fist value is the reference ID to reference in the attribute.
            - ID:



        Returns:

        """
        return CopyritghtAndLicense()

    def add_copyright_attribution(self, id_: str, text: str) -> CopyritghtAndLicense:
        self.copyright_attribution.append(CopyrightAttribution(id_, text))
        return self

    def add_copyright_attribution_from_dict(self, copyright_dict: dict[str, str]) -> CopyritghtAndLicense:
        copyright_list = [CopyrightAttribution(k, v) for k, v in copyright_dict.items()]
        self.copyright_attribution.extend(copyright_list)
        return self

    def add_copyright_license(self, id_: str, text: str, uri: str | None = None) -> CopyritghtAndLicense:
        self.license.append(License(id_, text, uri))
        return self


@dataclass
class CopyrightAttribution:
    id_: str
    text: str

    @staticmethod
    def create_new(id_: str, text: str) -> CopyrightAttribution:
        pass


@dataclass
class License:
    id_: str
    text: str
    uri: str | None

    @staticmethod
    def create_new(id_: str, text: str, uri: str | None = None) -> License:
        pass
